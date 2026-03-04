from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import HeroRole, PortalRarity, BattleStatus, SkillType, EffectType

# --- HERO SCHEMAS ---
class HeroBase(BaseModel):
    name: str
    role: HeroRole

class HeroCreate(HeroBase):
    pass

# --- SKILL SCHEMAS ---
class SkillBase(BaseModel):
    name: str
    skill_type: SkillType
    cooldown: int = 0
    energy_cost: int = 0
    effect_type: EffectType
    multiplier: float = 1.0

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: str
    hero_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class HeroResponse(HeroBase):
    id: str
    player_id: str
    level: int
    max_hp: int
    current_hp: int
    max_mana: int
    current_mana: int
    attack: int
    defense: int
    speed: int
    is_in_team: bool
    created_at: datetime
    skills: List[SkillResponse] = []
    
    class Config:
        from_attributes = True

# --- PLAYER SCHEMAS ---
class PlayerBase(BaseModel):
    username: str
    email: EmailStr

class PlayerCreate(PlayerBase):
    password: str

class PlayerResponse(PlayerBase):
    id: str
    guild_id: Optional[str] = None
    created_at: datetime
    heroes: List[HeroResponse] = []
    
    class Config:
        from_attributes = True

# --- GUILD SCHEMAS ---
class GuildBase(BaseModel):
    name: str

class GuildCreate(GuildBase):
    pass

class GuildResponse(GuildBase):
    id: str
    level: int
    experience: int
    created_at: datetime
    players: List[PlayerResponse] = []
    
    class Config:
        from_attributes = True

# --- PORTAL SCHEMAS ---
class PortalBase(BaseModel):
    name: str
    rarity: PortalRarity
    resource_type: str
    resource_generation_rate: int

class PortalCreate(PortalBase):
    pass

class PortalResponse(PortalBase):
    id: str
    controlling_guild_id: Optional[str] = None
    controlling_player_id: Optional[str] = None
    defender_1_id: Optional[str] = None
    defender_2_id: Optional[str] = None
    defender_3_id: Optional[str] = None
    last_collected_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- BATTLE SCHEMAS ---
class PortalAttackRequest(BaseModel):
    attacker_1_id: str
    attacker_2_id: Optional[str] = None
    attacker_3_id: Optional[str] = None
