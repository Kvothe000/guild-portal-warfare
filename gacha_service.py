from sqlalchemy.orm import Session
from models import Player, PlayerWallet, GachaBanner, PlayerBannerState, Hero, HeroFaction, HeroRarity, HeroRole
import random

from hero_skills_manifest import get_hero_template, list_all_heroes, HERO_TEMPLATES, Faction, Rarity

# Usamos as listas baseadas nas definições reais de manifesto
def get_heroes_by_faction_and_rarity(faction: HeroFaction, rarity: HeroRarity):
    matches = []
    # Mapeia enum SQLAlchemy para enum do Manifesto
    faction_str = faction.value
    rarity_str = rarity.value
    
    for key, data in HERO_TEMPLATES.items():
        if data["faction"].value == faction_str and data["rarity"].value == rarity_str:
            matches.append(key)
    return matches

# Probabilidades Padrão por Raridade (Fração de 10.000 para matemática exata)
# 1.2% SSS, 3% SS, 10% S, 40% A, 45.8% B
DROP_RATES = {
    HeroRarity.SSS: 120,    
    HeroRarity.SS: 300,     
    HeroRarity.S: 1000,     
    HeroRarity.A: 4000,     
    HeroRarity.B: 4580      
}

def pick_rarity(drop_rates_dict):
    """Roda a roleta e retorna a Raridade sorteada baseada nos pesos"""
    rand_val = random.randint(1, 10000)
    cumulative = 0
    for rarity, weight in drop_rates_dict.items():
        cumulative += weight
        if rand_val <= cumulative:
            return rarity
    return HeroRarity.B # Fallback seguro

def get_or_create_banner_state(db: Session, player_id: str, banner_id: str):
    state = db.query(PlayerBannerState).filter(
        PlayerBannerState.player_id == player_id,
        PlayerBannerState.banner_id == banner_id
    ).first()
    
    if not state:
        state = PlayerBannerState(player_id=player_id, banner_id=banner_id, pity_counter_sss=0)
        db.add(state)
        db.commit()
    return state

def pull_from_banner(db: Session, player_id: str, banner_id: str):
    """
    Função principal do Gacha 2.0.
    Deduz saldo, roda o rng, testa pity de 100 e cria o Herói no DB.
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    wallet = db.query(PlayerWallet).filter(PlayerWallet.player_id == player_id).first()
    banner = db.query(GachaBanner).filter(GachaBanner.id == banner_id).first()
    
    if not player or not wallet or not banner:
        raise ValueError("Player, Wallet, or Banner not found")
        
    # Verificar fundos
    if banner.cost_currency == "premium_aetherium":
        if wallet.crystals_premium < banner.cost_amount:
            raise ValueError("Not enough Aetherium (Premium Currency)")
        wallet.crystals_premium -= banner.cost_amount
    elif banner.cost_currency == "summon_tickets":
        if wallet.summon_tickets < banner.cost_amount:
            raise ValueError("Not enough Summon Tickets")
        wallet.summon_tickets -= banner.cost_amount
    else:
        raise ValueError("Unknown currency type for banner")
        
    state = get_or_create_banner_state(db, player_id, banner_id)
    
    # MATEMÁTICA DO PITY
    # Se chegamos em 99 sem SSS, o tiro 100 garante o prêmio.
    is_hard_pity = False
    if state.pity_counter_sss >= (banner.hard_pity_count - 1):
        rolled_rarity = HeroRarity.SSS
        is_hard_pity = True
    else:
        # Se for banner genérico que NÃO pode dropar SSS, ajustamos as chances
        if banner.faction_focus is None:
            no_sss_rates = {
                HeroRarity.SS: 50,
                HeroRarity.S: 500,
                HeroRarity.A: 2000,
                HeroRarity.B: 7450
            }
            rolled_rarity = pick_rarity(no_sss_rates)
        else:
            rolled_rarity = pick_rarity(DROP_RATES)
            
    # Lógica do Herói a ser Instanciado
    chosen_faction = banner.faction_focus if banner.faction_focus else HeroFaction.Neutral
    
    # Fallback se a facção específica ainda não tiver aquela raridade no Roster Dictionary
    # Na fase avançada, nós sortearíamos Aleatório DENTRO do Array de disponíveis daquela facção e raridade.
    possible_hero_keys = get_heroes_by_faction_and_rarity(chosen_faction, rolled_rarity)
    
    # Se a facção temática não tiver esse Rank (ex: Vanguard B não foi codado), pegamos um Neutral correspondente
    if not possible_hero_keys:
        possible_hero_keys = get_heroes_by_faction_and_rarity(HeroFaction.Neutral, rolled_rarity)
        chosen_faction = HeroFaction.Neutral
        
        # Super Fallback caso o Neutro tb não tenha, forçamos um A tier "default" de Vanguarda
        if not possible_hero_keys:
            possible_hero_keys = ["ClerigoRuinas"] # Default fallback seguro do nosso manifesto
            rolled_rarity = HeroRarity.A
            chosen_faction = HeroFaction.Vanguard
    
    # Sorteia exatamente qual herói dentre os elegíveis da lista
    chosen_hero_key = random.choice(possible_hero_keys)
    template = get_hero_template(chosen_hero_key)
    
    # Criar a Instância Física do Herói e Atribuir ao Jogador
    new_hero = Hero(
        player_id=player_id,
        name=template["name"],
        role=HeroRole(template["role"]), # Converte string do Manifesto para Enum
        faction=chosen_faction,
        rarity=rolled_rarity,
        # Estatísticas Básicas
        max_hp=template["base_stats"]["hp"],
        current_hp=template["base_stats"]["hp"],
        attack=template["base_stats"]["attack"],
        defense=template["base_stats"]["defense"],
        speed=template["base_stats"]["speed"],
        max_mana=100, current_mana=0
    )
    db.add(new_hero)
    db.flush() # Gerar o UUID do Herói sem commitar ainda
    
    # === FASE 10: INJEÇÃO DE CONJUNTOS DE HABILIDADE ===
    from models import Skill, SkillType, EffectType, CombatStatusEffect
    for skill_data in template["skills"]:
        # Mapping base strings to Enums gracefully
        s_type = SkillType(skill_data["type"])
        e_type = EffectType(skill_data["effect"])
        
        # Chase Triggers and Base Launchers
        l_status = CombatStatusEffect(skill_data.get("launcher", "NoneEffect"))
        c_effect = CombatStatusEffect(skill_data.get("chase_effect", "NoneEffect"))
        
        new_skill = Skill(
            hero_id=new_hero.id,
            name=skill_data["name"],
            skill_type=s_type,
            cooldown=skill_data.get("cooldown", 0),
            energy_cost=skill_data.get("cost", 0),
            effect_type=e_type,
            multiplier=skill_data.get("multiplier", 1.0),
            launcher_status=l_status,
            chase_trigger=str(skill_data.get("chase_trigger", "NoneEffect")),
            chase_effect=c_effect,
            hit_count=skill_data.get("hit_count", 1),
            apply_status=CombatStatusEffect(skill_data.get("apply_status", "NoneEffect")),
            advance_amount=skill_data.get("advance_amount", 0),
            delay_amount=skill_data.get("delay_amount", 0),
            max_chases_per_turn=skill_data.get("max_chases_per_turn", 1)
        )
        db.add(new_skill)
    
    # Gestão final da Moeda Pity
    if rolled_rarity == HeroRarity.SSS:
        state.pity_counter_sss = 0 # Reinicia a contagem
    else:
        state.pity_counter_sss += 1 # Adiciona +1 frustração

    db.commit()
    db.refresh(new_hero)
    
    return {
        "hero": new_hero,
        "pity_counter_sss": state.pity_counter_sss,
        "is_hard_pity": is_hard_pity
    }
