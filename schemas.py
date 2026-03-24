from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import (
    HeroRole, PortalRarity, BattleStatus, SkillType, EffectType,
    CombatStatusEffect, HeroFaction, HeroRarity, PlayerOrderClass
)

# =============================================================================
# VEIL OF DOMINION — Schemas v2.0
# =============================================================================

# --- HERO ---

class HeroBase(BaseModel):
    name: str
    role: HeroRole

class HeroCreate(HeroBase):
    pass

class SkillBase(BaseModel):
    name: str
    skill_type: SkillType
    cooldown: int = 0
    energy_cost: int = 0
    effect_type: EffectType
    multiplier: float = 1.0
    launcher_status: CombatStatusEffect = CombatStatusEffect.NoneEffect
    chase_trigger: str = "NoneEffect"
    chase_effect: CombatStatusEffect = CombatStatusEffect.NoneEffect

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: str
    hero_id: str
    hit_count: int = 1
    apply_status: CombatStatusEffect = CombatStatusEffect.NoneEffect
    advance_amount: int = 0
    delay_amount: int = 0
    max_chases_per_turn: int = 1
    created_at: datetime

    class Config:
        from_attributes = True

class HeroResponse(HeroBase):
    id: str
    player_id: str
    faction: HeroFaction
    rarity: HeroRarity
    level: int
    breakthrough_level: int = 0
    max_hp: int
    current_hp: int
    max_mana: int
    current_mana: int
    attack: int
    defense: int
    speed: int
    team_slot: Optional[int] = None
    base_launcher_chance: float = 0.0
    base_launcher_status: CombatStatusEffect = CombatStatusEffect.NoneEffect
    death_cooldown_until: Optional[datetime] = None
    created_at: datetime
    skills: List[SkillResponse] = []

    class Config:
        from_attributes = True


# --- PLAYER COMMANDER ---

class CommanderResponse(BaseModel):
    player_id: str
    order_class: PlayerOrderClass
    level: int
    experience: int
    team_slot: int
    max_hp: int
    current_hp: int
    attack: int
    defense: int
    speed: int
    active_basic_id: Optional[str] = None
    active_active_id: Optional[str] = None
    active_ultimate_id: Optional[str] = None
    active_passive_id: Optional[str] = None

    class Config:
        from_attributes = True

class CommanderCreate(BaseModel):
    order_class: PlayerOrderClass


# --- PLAYER ---

class PlayerBase(BaseModel):
    username: str
    email: EmailStr

class PlayerCreate(PlayerBase):
    password: str
    order_class: PlayerOrderClass  # Classe escolhida no onboarding

class PlayerResponse(PlayerBase):
    id: str
    clan_id: Optional[str] = None
    created_at: datetime
    heroes: List[HeroResponse] = []
    commander: Optional[CommanderResponse] = None

    class Config:
        from_attributes = True


# --- CLÃ ---

class ClanBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClanCreate(ClanBase):
    pass

class ClanResponse(ClanBase):
    id: str
    level: int
    experience: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- CLAN BOSS ---

class ClanBossDamageResponse(BaseModel):
    player_id: str
    damage_dealt: int
    attacks_used: int
    last_attack_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClanBossSessionResponse(BaseModel):
    id: str
    clan_id: str
    boss_name: str
    boss_max_hp: int
    boss_current_hp: int
    boss_level: int
    status: str
    week_start: datetime
    damage_contributions: List[ClanBossDamageResponse] = []

    class Config:
        from_attributes = True


# --- GACHA ---

class GachaBannerResponse(BaseModel):
    id: str
    name: str
    description: str
    faction_focus: Optional[HeroFaction] = None
    cost_amount: int
    cost_currency: str
    hard_pity_count: int
    soft_pity_start: int
    is_active: bool
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PlayerBannerStateResponse(BaseModel):
    banner_id: str
    pity_counter_sss: int
    guaranteed_next: bool = False

    class Config:
        from_attributes = True

class GachaPullResult(BaseModel):
    hero: HeroResponse
    pity_counter_sss: int
    is_hard_pity: bool


# --- PORTAL ---

class PortalBase(BaseModel):
    name: str
    rarity: PortalRarity
    resource_type: str
    resource_generation_rate: int

class PortalCreate(PortalBase):
    map_x: float = 0.0
    map_y: float = 0.0

class PortalResponse(PortalBase):
    id: str
    map_x: float
    map_y: float
    controlling_clan_id: Optional[str] = None
    controlling_player_id: Optional[str] = None
    defender_1_id: Optional[str] = None
    defender_2_id: Optional[str] = None
    defender_3_id: Optional[str] = None
    last_collected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- BATTLE ---

class PortalAttackRequest(BaseModel):
    attacker_1_id: str
    attacker_2_id: Optional[str] = None
    attacker_3_id: Optional[str] = None
