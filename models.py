from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum, Boolean, Text
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum
from database import Base

# =============================================================================
# VEIL OF DOMINION — Models v2.0
# =============================================================================

# --- Enums ---

class HeroRole(enum.Enum):
    Tank = "Tank"
    Carry = "Carry"
    Support = "Support"
    Control = "Control"

class CombatStatusEffect(enum.Enum):
    NoneEffect = "NoneEffect"
    # Estados de Chase
    Knockdown = "Knockdown"
    HighFloat = "HighFloat"
    LowFloat = "LowFloat"
    Repulse = "Repulse"
    # CC (Crowd Control)
    Stun = "Stun"
    Silence = "Silence"
    Blind = "Blind"
    Root = "Root"
    # DoT (Damage over Time)
    Burn = "Burn"
    Poison = "Poison"
    Bleed = "Bleed"
    # Buff
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

class PlayerOrderClass(enum.Enum):
    """As 5 Classes de Comandante — o Avatar jogável do jogador."""
    FlameInquisitor = "FlameInquisitor"      # Vanguarda / Carry AoE
    EtherChronist = "EtherChronist"          # Arcano / Control + Support
    SpectralBlade = "SpectralBlade"          # Sombras / Assassino
    StoneCleric = "StoneCleric"              # Vanguarda / Support + Tank
    LunarHunter = "LunarHunter"             # Arcano / Multihit / Chase

class ClanBossStatus(enum.Enum):
    Active = "Active"
    Defeated = "Defeated"

# --- Utilitários ---
def generate_uuid():
    return str(uuid.uuid4())


# =============================================================================
# CLÃS (antigo: Guildas)
# =============================================================================

class Clan(Base):
    __tablename__ = "clans"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relacionamentos
    players = relationship("Player", back_populates="clan")
    clan_boss_sessions = relationship("ClanBossSession", back_populates="clan")

    @property
    def max_members(self):
        return self.level * 5


class ClanBossSession(Base):
    """
    Uma sessão semanal do Boss do Clã.
    O HP do boss é compartilhado — todos os membros atacam e o dano é acumulado.
    """
    __tablename__ = "clan_boss_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    clan_id = Column(String, ForeignKey("clans.id"), nullable=False)

    boss_name = Column(String, default="Lich Soberano de Valdris")
    boss_max_hp = Column(Integer, default=10_000_000)
    boss_current_hp = Column(Integer, default=10_000_000)
    boss_level = Column(Integer, default=1)  # Aumenta a cada semana vencida

    status = Column(Enum(ClanBossStatus), default=ClanBossStatus.Active)

    week_start = Column(DateTime, default=datetime.datetime.utcnow)
    week_end = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    clan = relationship("Clan", back_populates="clan_boss_sessions")
    damage_contributions = relationship("ClanBossDamage", back_populates="session")


class ClanBossDamage(Base):
    """Rastreia o dano individual de cada membro ao Boss do Clã."""
    __tablename__ = "clan_boss_damage"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("clan_boss_sessions.id"))
    player_id = Column(String, ForeignKey("players.id"))

    damage_dealt = Column(Integer, default=0)
    attacks_used = Column(Integer, default=0)  # Max 3 por dia
    last_attack_at = Column(DateTime, nullable=True)

    session = relationship("ClanBossSession", back_populates="damage_contributions")
    player = relationship("Player")


# =============================================================================
# JOGADOR
# =============================================================================

class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    clan_id = Column(String, ForeignKey("clans.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relacionamentos
    clan = relationship("Clan", back_populates="players")
    heroes = relationship("Hero", back_populates="player")
    progress = relationship("PlayerProgress", back_populates="player", uselist=False)
    wallet = relationship("PlayerWallet", back_populates="player", uselist=False)

    # O Comandante (Avatar jogável) — 1:1 com o Player
    commander = relationship("PlayerCommander", back_populates="player", uselist=False)
    guardian_spirits = relationship("GuardianSpirit", back_populates="player", cascade="all, delete-orphan")
    equipment_items  = relationship("Equipment", back_populates="player", foreign_keys="Equipment.player_id", cascade="all, delete-orphan")


class PlayerCommander(Base):
    """
    O personagem jogável do jogador — o Comandante da Ordem.
    Inspirado nos 5 elementos do Naruto Online, mas com identidade própria do mundo Valdris.
    Ocupa um slot no grid 3x3. A classe pode ser trocada (com custo de Cristais),
    mas as habilidades devem ser reaprendidas.
    """
    __tablename__ = "player_commanders"

    player_id = Column(String, ForeignKey("players.id"), primary_key=True)

    order_class = Column(Enum(PlayerOrderClass), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)

    # Slots de habilidade desbloqueados progressivamente (por level)
    # IDs referenciam habilidades estaticas definidas no commander_skills_manifest.py
    active_basic_id = Column(String, nullable=True)
    active_active_id = Column(String, nullable=True)
    active_ultimate_id = Column(String, nullable=True)
    active_passive_id = Column(String, nullable=True)

    # Posição padrão no grid (5 = centro)
    team_slot = Column(Integer, default=5)

    # Stats base (crescem por level)
    max_hp = Column(Integer, default=2000)
    current_hp = Column(Integer, default=2000)
    attack = Column(Integer, default=150)
    defense = Column(Integer, default=120)
    speed = Column(Integer, default=110)

    player = relationship("Player", back_populates="commander")


# =============================================================================
# HERÓIS
# =============================================================================

class Hero(Base):
    __tablename__ = "heroes"

    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))

    name = Column(String)
    role = Column(Enum(HeroRole))
    faction = Column(Enum(HeroFaction), default=HeroFaction.Neutral)
    rarity = Column(Enum(HeroRarity), default=HeroRarity.B)
    level = Column(Integer, default=1)

    # Sistema de Breakthrough (BT0 → BT6)
    breakthrough_level = Column(Integer, default=0)
    # Fragmentos acumulados para o próximo BT (thresholds: 10, 20, 40, 80, 150, 300)
    breakthrough_fragments = Column(Integer, default=0)

    # Stats
    max_hp = Column(Integer, default=1000)
    current_hp = Column(Integer, default=1000)
    max_mana = Column(Integer, default=100)
    current_mana = Column(Integer, default=0)
    attack = Column(Integer, default=100)
    defense = Column(Integer, default=80)
    speed = Column(Integer, default=100)

    # Posição no grid 3x3 (1-9). None = fora do time
    team_slot = Column(Integer, nullable=True)

    # Mecânicas de chase inatas do Basic Attack
    base_launcher_chance = Column(Float, default=0.0)
    base_launcher_status = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)

    # Death Cooldown (Guerra de Clã — anti-whale)
    death_cooldown_until = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    player = relationship("Player", back_populates="heroes")
    skills = relationship("Skill", back_populates="hero", cascade="all, delete-orphan")
    equipment_items = relationship("Equipment", back_populates="hero", foreign_keys="Equipment.hero_id")


class Skill(Base):
    """Habilidade instanciada de um Herói (cópia do template do manifesto)."""
    __tablename__ = "skills"

    id = Column(String, primary_key=True, default=generate_uuid)
    hero_id = Column(String, ForeignKey("heroes.id"))

    name = Column(String)
    skill_type = Column(Enum(SkillType))

    # Restrições de uso
    cooldown = Column(Integer, default=0)
    energy_cost = Column(Integer, default=0)

    # Lógica de Impacto
    effect_type = Column(Enum(EffectType))
    multiplier = Column(Float, default=1.0)

    # Chase Mechanics
    launcher_status = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)
    chase_trigger = Column(String, default="NoneEffect")  # String para suportar "COMBO_10"
    chase_effect = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)

    # Mecânicas secundárias
    hit_count = Column(Integer, default=1)
    apply_status = Column(Enum(CombatStatusEffect), default=CombatStatusEffect.NoneEffect)
    advance_amount = Column(Integer, default=0)
    delay_amount = Column(Integer, default=0)
    max_chases_per_turn = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    hero = relationship("Hero", back_populates="skills")


# =============================================================================
# PORTAIS DE ÉTER
# =============================================================================

class Portal(Base):
    __tablename__ = "portals"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    rarity = Column(Enum(PortalRarity))
    resource_type = Column(String)
    resource_generation_rate = Column(Integer)

    # Posição no mapa de Valdris
    map_x = Column(Float, default=0.0)
    map_y = Column(Float, default=0.0)

    controlling_clan_id = Column(String, ForeignKey("clans.id"), nullable=True)
    controlling_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    # Defensores (até 3 jogadores do clã controlador)
    defender_1_id = Column(String, ForeignKey("players.id"), nullable=True)
    defender_2_id = Column(String, ForeignKey("players.id"), nullable=True)
    defender_3_id = Column(String, ForeignKey("players.id"), nullable=True)

    last_collected_at = Column(DateTime, nullable=True)


class Battle(Base):
    __tablename__ = "battles"

    id = Column(String, primary_key=True, default=generate_uuid)
    portal_id = Column(String, ForeignKey("portals.id"))

    attacker_clan_id = Column(String, ForeignKey("clans.id"), nullable=True)
    attacker_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    defender_clan_id = Column(String, ForeignKey("clans.id"), nullable=True)
    defender_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    attacker_1_id = Column(String, ForeignKey("players.id"))
    attacker_2_id = Column(String, ForeignKey("players.id"), nullable=True)
    attacker_3_id = Column(String, ForeignKey("players.id"), nullable=True)

    status = Column(Enum(BattleStatus), default=BattleStatus.Pending)

    winner_clan_id = Column(String, ForeignKey("clans.id"), nullable=True)
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)

    combat_log = Column(Text, nullable=True)  # JSON serializado

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


# =============================================================================
# PROGRESSÃO PvE — Campanha & AFK Farm
# =============================================================================

class CampaignStage(Base):
    """Fase da campanha PvE. Completar desbloqueia AFK farm naquele nível."""
    __tablename__ = "campaign_stages"

    id = Column(String, primary_key=True, default=generate_uuid)
    # Ex: 101 = Mundo 1 Fase 1, 312 = Mundo 3 Fase 12
    stage_number = Column(Integer, unique=True, index=True)
    name = Column(String)
    world_number = Column(Integer, default=1)

    difficulty_modifier = Column(Integer, default=1)

    # Renda passiva por hora (AFK Farm)
    afk_xp_per_hour = Column(Integer, default=60)
    afk_gold_per_hour = Column(Integer, default=120)
    afk_clan_coins_per_hour = Column(Integer, default=0)  # Fases avançadas


class PlayerProgress(Base):
    """Extensão 1:1 do Player com dados de progressão PvE e temporais."""
    __tablename__ = "player_progress"

    player_id = Column(String, ForeignKey("players.id"), primary_key=True)

    highest_stage_number = Column(Integer, default=0)
    last_afk_collection = Column(DateTime, default=datetime.datetime.utcnow)

    # Tickets de conteúdo diário
    daily_sweeps_remaining = Column(Integer, default=5)
    daily_fast_rewards_remaining = Column(Integer, default=1)
    daily_boss_attacks_remaining = Column(Integer, default=3)  # Boss do Clã

    # Arena ELO
    arena_points = Column(Integer, default=1000)

    last_daily_reset = Column(DateTime, default=datetime.datetime.utcnow)

    player = relationship("Player", back_populates="progress")


# =============================================================================
# ARENA PvP 1v1
# =============================================================================

class ArenaMatch(Base):
    __tablename__ = "arena_matches"

    id = Column(String, primary_key=True, default=generate_uuid)

    attacker_player_id = Column(String, ForeignKey("players.id"))
    defender_player_id = Column(String, ForeignKey("players.id"))

    attacker_points_before = Column(Integer)
    defender_points_before = Column(Integer)

    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    points_exchanged = Column(Integer, default=0)

    combat_log = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =============================================================================
# ECONOMIA — Carteira & Gacha
# =============================================================================

class PlayerWallet(Base):
    """Carteira financeira do jogador. Isolada para segurança."""
    __tablename__ = "player_wallets"

    player_id = Column(String, ForeignKey("players.id"), primary_key=True)

    gold = Column(Integer, default=0)
    crystals_premium = Column(Integer, default=0)   # Cristais de Éter (premium)
    clan_coins = Column(Integer, default=0)          # Coins de Clã
    summon_tickets = Column(Integer, default=0)      # Tickets de Invocação
    spirit_tickets = Column(Integer, default=0)      # Tickets de Espírito (Guardião)
    pity_counter = Column(Integer, default=0)        # Legado — mantido por compatibilidade

    player = relationship("Player", back_populates="wallet")


class GachaBanner(Base):
    __tablename__ = "gacha_banners"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    description = Column(String)
    faction_focus = Column(Enum(HeroFaction), nullable=True)
    cost_amount = Column(Integer, default=1)
    cost_currency = Column(String, default="premium_aetherium")
    hard_pity_count = Column(Integer, default=100)
    soft_pity_start = Column(Integer, default=75)   # A partir daqui chance aumenta

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)     # None = permanente


class PlayerBannerState(Base):
    __tablename__ = "player_banner_states"

    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))
    banner_id = Column(String, ForeignKey("gacha_banners.id"))

    pity_counter_sss = Column(Integer, default=0)
    guaranteed_next = Column(Boolean, default=False)  # 50/50 perdido = garantia na próxima

    player = relationship("Player")
    banner = relationship("GachaBanner")


# =============================================================================
# GUARDIÃO ESPIRITUAL
# =============================================================================

class GuardianSpirit(Base):
    """Suporte passivo equipável — invocado com Spirit Tickets."""
    __tablename__ = "guardian_spirits"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)

    name     = Column(String, nullable=False)
    element  = Column(String, nullable=False)       # Fogo | Gelo | Sombra | Luz | Natureza
    rarity   = Column(String, nullable=False)       # SSS | SS | S | A
    level    = Column(Integer, default=1)

    passive_name        = Column(String, nullable=False)
    passive_description = Column(Text, nullable=False)

    # Stat bonuses planos (somados ao time)
    stat_hp  = Column(Integer, default=0)
    stat_atk = Column(Integer, default=0)
    stat_def = Column(Integer, default=0)
    stat_spd = Column(Integer, default=0)

    is_equipped = Column(Boolean, default=False)
    obtained_at = Column(DateTime, default=datetime.datetime.utcnow)

    player = relationship("Player", back_populates="guardian_spirits")


# =============================================================================
# EQUIPAMENTO
# =============================================================================

class Equipment(Base):
    """Itens equipáveis em heróis — obtidos via campanha e boss."""
    __tablename__ = "equipment"

    id        = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    hero_id   = Column(String, ForeignKey("heroes.id"), nullable=True)  # None = no inventário

    name      = Column(String, nullable=False)
    slot      = Column(String, nullable=False)    # Weapon | Armor | Accessory | Relic
    rarity    = Column(String, nullable=False)    # Lendário | Épico | Raro | Comum
    level     = Column(Integer, default=1)
    max_level = Column(Integer, default=10)

    # Stats (nullable — nem todo equip tem todos)
    stat_atk       = Column(Integer, nullable=True)
    stat_def       = Column(Integer, nullable=True)
    stat_hp        = Column(Integer, nullable=True)
    stat_spd       = Column(Integer, nullable=True)
    stat_crit_rate = Column(Float, nullable=True)   # Ex: 0.08 = 8%
    stat_crit_dmg  = Column(Float, nullable=True)   # Ex: 0.30 = 30%

    set_name  = Column(String, nullable=True)
    set_bonus = Column(Text, nullable=True)

    obtained_at = Column(DateTime, default=datetime.datetime.utcnow)

    player = relationship("Player", back_populates="equipment_items")
    hero   = relationship("Hero", back_populates="equipment_items")
