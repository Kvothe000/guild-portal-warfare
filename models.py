from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum
from database import Base

# Enums
class HeroRole(enum.Enum):
    Tank = "Tank"
    Carry = "Carry"
    Support = "Support"
    Control = "Control"

class CombatStatusEffect(enum.Enum):
    NoneEffect = "NoneEffect"
    Knockdown = "Knockdown"
    HighFloat = "HighFloat"
    LowFloat = "LowFloat"
    Repulse = "Repulse"
    # New CCs and DoTs
    Stun = "Stun"
    Silence = "Silence"
    Blind = "Blind"
    Root = "Root"
    Burn = "Burn"
    Poison = "Poison"
    Bleed = "Bleed"
    Shield = "Shield"

class HeroFaction(enum.Enum):
    Vanguard = "Vanguard"
    Arcane = "Arcane"
    Shadow = "Shadow"
    Neutral = "Neutral"

class HeroRarity(enum.Enum):
    SSS = "SSS"
    SS = "SS"
    S = "S"
    A = "A"
    B = "B"

class PortalRarity(enum.Enum):
    C = "C"
    B = "B"
    A = "A"
    S = "S"

class BattleStatus(enum.Enum):
    Pending = "Pending"
    Resolved = "Resolved"

class SkillType(enum.Enum):
    Basic = "Basic"
    Active = "Active"
    Ultimate = "Ultimate"
    Passive = "Passive"

class EffectType(enum.Enum):
    Damage = "Damage"
    Heal = "Heal"
    Taunt = "Taunt"
    Buff = "Buff"
    Debuff = "Debuff"
    Action_Advance = "Action_Advance"
    Action_Delay = "Action_Delay"
    Damage_And_CC = "Damage_And_CC"
    Damage_And_Buff = "Damage_And_Buff"
    Taunt_And_Shield = "Taunt_And_Shield"
    Damage_Ignore_Def = "Damage_Ignore_Def"
    Heal_And_Shield = "Heal_And_Shield"
    AoE_Damage_HitCombo = "AoE_Damage_HitCombo"
    Damage_And_Debuff = "Damage_And_Debuff"
    Damage_And_DoT = "Damage_And_DoT"
    Damage_Multihit = "Damage_Multihit"
    Damage_CC_Delay = "Damage_CC_Delay"
    Damage_Heal = "Damage_Heal"
    Sacrifice_Heal_Buff = "Sacrifice_Heal_Buff"
    AoE_Damage_Multihit = "AoE_Damage_Multihit"
    Summon_Clone = "Summon_Clone"

# Funções utilitárias
def generate_uuid():
    return str(uuid.uuid4())

class Guild(Base):
    __tablename__ = "guilds"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    players = relationship("Player", back_populates="guild")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    guild = relationship("Guild", back_populates="players")
    heroes = relationship("Hero", back_populates="player")
    
    # FASE 4: Relacionamento 1:1 com o painel de progressão PvE e AFK do jogador
    progress = relationship("PlayerProgress", back_populates="player", uselist=False)
    
    # FASE 7: Economia e Carteira do Jogador
    wallet = relationship("PlayerWallet", back_populates="player", uselist=False)
    
    # FASE 10.5: O Mestre da Guilda (Avatar / Main Character)
    avatar = relationship("PlayerAvatar", back_populates="player", uselist=False)
    guardian_spirits = relationship("GuardianSpirit", back_populates="player", cascade="all, delete-orphan")

class Hero(Base):
    __tablename__ = "heroes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))
    name = Column(String)
    role = Column(Enum(HeroRole))
    faction = Column(Enum(HeroFaction), default=HeroFaction.Neutral)
    rarity = Column(Enum(HeroRarity), default=HeroRarity.B)
    level = Column(Integer, default=1)
    max_hp = Column(Integer, default=100)
    current_hp = Column(Integer, default=100)
    
    # FASE 6: Mana/Energy System
    max_mana = Column(Integer, default=100)
    current_mana = Column(Integer, default=0)
    
    attack = Column(Integer, default=10)
    defense = Column(Integer, default=10)
    speed = Column(Integer, default=10)
    
    # FASE 9: Grid de Batalha (Posição de 1 a 9). None significa que não está no time.
    team_slot = Column(Integer, nullable=True)
    
    # FASE 9: Chase Mechanics Inatos (Basic Attack pode dar Launch)
    base_launcher_chance = Column(Float, default=0.0)
    base_launcher_status = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)
    
    # FASE 5: Death Cooldown System (Anti-Whale Mechanic)
    # Se morto em uma Guerra de Portal, o herói recebe um timestamp futuro.
    # Até esse timestamp expirar, ele não pode atacar Portais.
    # Opcional no futuro: cobrar Cristais para reverter esse timestamp para NULL.
    death_cooldown_until = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    player = relationship("Player", back_populates="heroes")
    skills = relationship("Skill", back_populates="hero", cascade="all, delete-orphan")

# ==========================================
# FASE 6: Sistema de Habilidades (Combat Engine)
# ==========================================

class Skill(Base):
    """
    Representa uma Habilidade específica pertencente a um Herói.
    Em um Gacha em produção, isso clonaria um 'SkillTemplate' da definição do Herói base.
    """
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hero_id = Column(String, ForeignKey("heroes.id"))
    
    name = Column(String)
    skill_type = Column(Enum(SkillType)) # Basic, Active, Ultimate, Passive
    
    # Restrições de uso
    cooldown = Column(Integer, default=0) # Turnos de CD
    energy_cost = Column(Integer, default=0) # Custo para conjurar
    
    # Lógica de Impacto
    effect_type = Column(Enum(EffectType)) # Damage, Heal, Taunt, Buff
    multiplier = Column(Float, default=1.0) # Multiplicador Ex: 1.5 = 150% do attack stat
    
    # FASE 9: Mecânicas de Chase e Status
    launcher_status = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)
    chase_trigger = Column(String, default="NoneEffect") # Modificado para String para suportar "COMBO_10"
    chase_effect = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)
    
    # NOVAS ENGRENAGENS: Energia e Tempo
    hit_count = Column(Integer, default=1) # Para gerar hits
    apply_status = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)
    advance_amount = Column(Integer, default=0) # % de Turno Adiantado
    delay_amount = Column(Integer, default=0) # % de Turno Atrasado
    max_chases_per_turn = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    hero = relationship("Hero", back_populates="skills")

# ==========================================
# FASE 10.5: O Mestre da Guilda e Espíritos
# ==========================================

class PlayerAvatar(Base):
    """
    O Main Character do Jogador (Inspirado nos 5 Elementos do Naruto Online).
    Ocupa um slot obrigatório no Grid 3x3. Sua grande vantagem é a flexibilidade:
    A árvore de talentos pode ser trocada a qualquer momento para consertar Combos imperfeitos do Gacha.
    """
    __tablename__ = "player_avatars"
    
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    
    # A "Classe" escolhida pelo jogador no início do jogo (Ex: Inquisidor do Fogo, Mago D'água)
    avatar_class = Column(String, nullable=False) 
    level = Column(Integer, default=1)
    
    # Slots de Habilidades Dinâmicas (Mapeia para IDs de habilidades estáticas predefinidas na engine)
    active_basic_id = Column(String, nullable=True)     # O que ele faz no turno normal
    active_ultimate_id = Column(String, nullable=True)  # A mágica poderosa
    active_passive_1_id = Column(String, nullable=True) # Geralmente um Chase
    active_passive_2_id = Column(String, nullable=True) # Geralmente Buff universal
    
    # Posição no grid (1 a 9)
    team_slot = Column(Integer, default=5)
    
    player = relationship("Player", back_populates="avatar")

class GuardianSpirit(Base):
    """
    Inspirado no sistema de Invocação (Kuchiyose). 
    Fica fora do Tabuleiro. Se o combo do time quebrar, e ele tiver o Chase Trigger exato,
    ele aparece na arena de forma invisível, acerta o Hit, e desaparece, provendo uma "ponte" extra.
    """
    __tablename__ = "guardian_spirits"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))
    
    name = Column(String)
    rarity = Column(Enum(HeroRarity), default=HeroRarity.A)
    is_equipped = Column(Boolean, default=False)
    
    # A ponte mágica
    chase_trigger = Column(Enum(CombatStatusEffect))
    chase_effect = Column(Enum(CombatStatusEffect))
    damage_multiplier = Column(Float, default=1.5)
    
    player = relationship("Player", back_populates="guardian_spirits")


class Portal(Base):
    __tablename__ = "portals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    rarity = Column(Enum(PortalRarity))
    resource_type = Column(String)
    resource_generation_rate = Column(Integer)
    
    controlling_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    controlling_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    defender_1_id = Column(String, ForeignKey("players.id"), nullable=True)
    defender_2_id = Column(String, ForeignKey("players.id"), nullable=True)
    defender_3_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    last_collected_at = Column(DateTime, nullable=True)

class Battle(Base):
    __tablename__ = "battles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    portal_id = Column(String, ForeignKey("portals.id"))
    
    attacker_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    attacker_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    defender_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    defender_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    attacker_1_id = Column(String, ForeignKey("players.id"))
    attacker_2_id = Column(String, ForeignKey("players.id"), nullable=True)
    attacker_3_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    status = Column(Enum(BattleStatus), default=BattleStatus.Pending)
    
    winner_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    # Para SQLite usaremos String ao invés de JSONB, será serializado no Python
    combat_log = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

# ==========================================
# FASE 4: Sitema PvE (Campanha) e Retenção Idle
# ==========================================

class CampaignStage(Base):
    """
    Representa uma fase fixa do modo Campanha (PvE).
    Define quão difícil é o combate e qual a 'renda passiva' (AFK) que o jogador
    ganha ao ter concluído esta fase. O muro de dificuldade substitui a Stamina.
    """
    __tablename__ = "campaign_stages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    # Exemplo: 101 (Mundo 1, Fase 1), 102 (Mundo 1, Fase 2)
    stage_number = Column(Integer, unique=True, index=True) 
    name = Column(String)
    
    # Multiplicador abstrato de status para os inimigos a serem gerados contra a engine
    difficulty_modifier = Column(Integer, default=1) 
    
    # Renda Passiva gerada por HORA no Caixa AFK. Quanto maior a fase, melhor o farm.
    afk_xp_per_hour = Column(Integer, default=60)
    afk_gold_per_hour = Column(Integer, default=120)


class PlayerProgress(Base):
    """
    Uma extensão 1:1 da tabela Player. Guarda tudo relacionado ao avanço
    matemático do jogador no tempo (Idle) e nos modos PvE. 
    Modularizado para evitar inflar colunas ativas na tabela 'players'.
    """
    __tablename__ = "player_progress"
    
    # A mesma ID do Player é a Primary Key aqui (Relação 1:1 absoluta)
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    
    # Fase mais alta concluída (Define o teto de farm AFK atual)
    highest_stage_number = Column(Integer, default=0) 
    
    # Timestamp base do Idle System (Caixa AFK). Toda a lógica matemática F2P reside aqui.
    # Loot Retrotativo = (Now - last_afk_collection).horas * afk_rate_da_sua_highest_stage
    last_afk_collection = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Sistema de Tickets e Mecânicas Diárias Anti-Burnout (Limita mas não prende)
    daily_sweeps_remaining = Column(Integer, default=5) # Dungeons Sweeps
    daily_fast_rewards_remaining = Column(Integer, default=1) # Botão de resgatar 2h do AFK imediatamente grátis
    
    # FASE 5: Rankeada (Ladder 1v1)
    # Pontuação ELO padrão que sobe ao vencer e cai ao perder
    arena_points = Column(Integer, default=1000)
    
    # Para controlarmos os resets pontuais de servidores baseados no ciclo de 24h
    last_daily_reset = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Conexão de volta com a tabela Principal
    player = relationship("Player", back_populates="progress")

# ==========================================
# FASE 5: Arena de Honra (PvP 1v1 Rankeado)
# ==========================================

class ArenaMatch(Base):
    """
    Registro independente para partidas 1v1. 
    A Arena é focada no ganho de pontos de vaidade (Ladder), 
    não acionando as pesadas mecânicas de Guilda como 'Death Cooldown' ou 'Hero Lock'.
    """
    __tablename__ = "arena_matches"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # O desafiante e o defensor
    attacker_player_id = Column(String, ForeignKey("players.id"))
    defender_player_id = Column(String, ForeignKey("players.id"))
    
    # Status ELO no momento em que a batalha começou (Para histórico verídico)
    attacker_points_before = Column(Integer)
    defender_points_before = Column(Integer)
    
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    # Quantos pontos ELO foram movimentados nesta partida
    points_exchanged = Column(Integer, default=0) 
    
    # Serializado em string/JSONB caso SQLite/Postgres. 
    # Guarda o mesmo formato 3v3 de engine.py
    combat_log = Column(String, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# ==========================================
# FASE 7: Economia, Moedas e Sistema de Gacha
# ==========================================

class PlayerWallet(Base):
    """
    Guarda 100% da parte financeira/econômica do jogador.
    Isolada da tabela principal 'players' e do progresso para segurança (Anti-Exploit).
    """
    __tablename__ = "player_wallets"
    
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    
    # Moedas
    gold = Column(Integer, default=0) # Dinheiro base (Usado para Upgrades de Level)
    crystals_premium = Column(Integer, default=0) # Moeda premium/Real money (Gacha e Skips)
    guild_coins = Column(Integer, default=0) # Farma nas guerras e usa na Loja da Guilda
    
    # Invocação
    summon_tickets = Column(Integer, default=0) # Tickets grátis ou ganhos em eventos
    
    # Sistema Anti-Frustração (Pity) genérico antigo (mantido por compatibilidade)
    pity_counter = Column(Integer, default=0) 
    
    player = relationship("Player", back_populates="wallet")

class GachaBanner(Base):
    __tablename__ = "gacha_banners"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String) # Ex: "Baú da Vanguarda"
    description = Column(String)
    faction_focus = Column(Enum(HeroFaction), nullable=True) # Se None, é o Baú Básico Fodder
    cost_amount = Column(Integer, default=1)
    cost_currency = Column(String, default="premium_aetherium") # "premium_aetherium" ou "summon_tickets"
    hard_pity_count = Column(Integer, default=100)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PlayerBannerState(Base):
    __tablename__ = "player_banner_states"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))
    banner_id = Column(String, ForeignKey("gacha_banners.id"))
    
    pity_counter_sss = Column(Integer, default=0)
    
    player = relationship("Player")
    banner = relationship("GachaBanner")
