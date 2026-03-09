import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Player, GachaBanner, HeroFaction, PlayerWallet
from gacha_service import pull_from_banner
from engine import simulate_3v3_combat

# 1. Configurar Banco SQLite Em-Memória para o Teste
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("--- 1. INICIALIZANDO BANCO E DADOS ---")
# Criar Jogador
player = Player(username="Tester_Alpha", email="test@alpha.com")
db.add(player)
db.commit()

# Dar dinheiro ao jogador
wallet = PlayerWallet(player_id=player.id, crystals_premium=50000, summon_tickets=0)
db.add(wallet)

# Criar um Banner da Vanguarda e um do Círculo Etereal
vanguard_banner = GachaBanner(
    name="Baú da Vanguarda", faction_focus=HeroFaction.Vanguard, 
    cost_amount=100, cost_currency="premium_aetherium", hard_pity_count=10
)
arcane_banner = GachaBanner(
    name="Baú do Círculo Etereal", faction_focus=HeroFaction.Arcane, 
    cost_amount=100, cost_currency="premium_aetherium", hard_pity_count=10
)
shadow_banner = GachaBanner(
    name="Baú das Sombras", faction_focus=HeroFaction.Shadow, 
    cost_amount=100, cost_currency="premium_aetherium", hard_pity_count=10
)
db.add_all([vanguard_banner, arcane_banner, shadow_banner])
db.commit()

print("--- 2. SIMULANDO GACHA PULLS (COMBO SYNERGY) ---")
# Vamos forçar a tentar puxar Válkios, Aric e Clerigo (Vanguarda)
# Em um teste realista, a RNG rodaria solta. Vamos fazer 10 pulls na Vanguarda para pegar pity SSS
vanguard_team = []
for i in range(10):
    result = pull_from_banner(db, player.id, vanguard_banner.id)
    hero = result["hero"]
    # Pegamos os diferentes
    if not any(h.name == hero.name for h in vanguard_team) and len(vanguard_team) < 3:
        vanguard_team.append(hero)
        print(f"🎯 Puxou: {hero.name} [{hero.rarity.value}] - Skills Injetadas: {len(hero.skills)}")

# Adicionar ao Grid (Slots 1, 2, 3)
for idx, h in enumerate(vanguard_team):
    h.team_slot = idx + 1
db.commit()

print("\n--- 3. GERANDO INIMIGOS (CÍRCULO ETEREAL - DESVANTAGEM FRACTAL) ---")
arcane_team = []
# Puxar do Arcane Banner para gerar os inimigos (Shattered by Vanguard)
for i in range(15):
    result = pull_from_banner(db, player.id, shadow_banner.id)
    hero = result["hero"]
    if not any(h.name == hero.name for h in arcane_team) and len(arcane_team) < 3:
        arcane_team.append(hero)
        print(f"💀 Inimigo gerado: {hero.name} [{hero.rarity.value}]")

for idx, h in enumerate(arcane_team):
    h.team_slot = idx + 1 # Inimigos usam seu próprio grid relativo

print("\n--- 4. INICIANDO ENGINE DE COMBATE 2.0 (AV, ENERGY & CHASES) ---")
combat_result = simulate_3v3_combat(vanguard_team, arcane_team)

print(f"\n🏆 VENCEDOR: {combat_result['winner'].upper()}")
print("\n--- LOG DE TURNOS ---")

for turn_data in combat_result["log"]:
    print(f"\n[AV TICK {turn_data['tick']}] - Turno de {turn_data['actor']}")
    for action in turn_data["actions"]:
        s_type = action.get("effect_type", "Damage")
        print(f"  👉 Usou: {action.get('skill_used', 'Basic')} -> Alvo: {action.get('target_name', 'None')}")
        
        if "healed" in action:
            print(f"     💚 Curou {action['healed']} HP (Restante: {action.get('target_hp_remaining', 'N/A')})")
        
        if "damage" in action:
            print(f"     💥 Dano: {action['damage']} (Restante: {action.get('target_hp_remaining', 'N/A')})")
            
            if action.get("shatter_triggered"):
                print(f"     ⚡ SHATTER! Vantagem de Facção! Postura Quebrada (Status Extra: {action.get('shatter_status')})")
                
            if action.get("status_applied"):
                print(f"     🌀 Status Aplicado: {action['status_applied']}")

        if s_type == "CHASE_COMBO":
            print(f"     🔗 PERSEGUIÇÃO ({action.get('triggered_by')})! Dano Extra: {action.get('damage')}")

        if action.get("target_died"):
            print(f"     💀 {action['target_name']} MORREU!")
            
        if action.get("summoned_clone"):
            print(f"     👥 INVOCADA! {action['summoned_clone']} cobriu a linha de frente no Slot {action['slot']}!")
            
print("\n[ FIM DA SIMULAÇÃO ]")
