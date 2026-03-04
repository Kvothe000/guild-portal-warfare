from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import HeroRole, PortalRarity, BattleStatus

# --- HERO SCHEMAS ---
class HeroBase(BaseModel):
    name: str
    role: HeroRole

class HeroCreate(HeroBase):
    pass

class HeroResponse(HeroBase):
    id: str
    player_id: str
    level: int
    max_hp: int
    current_hp: int
    attack: int
    defense: int
    speed: int
    is_in_team: bool
    created_at: datetime
    
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
