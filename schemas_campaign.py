from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- PVE / CAMPAIGN SCHEMAS (Fase 4) ---

class CampaignStageBase(BaseModel):
    stage_number: int
    name: str
    difficulty_modifier: int = 1
    afk_xp_per_hour: int = 60
    afk_gold_per_hour: int = 120

class CampaignStageCreate(CampaignStageBase):
    pass

class CampaignStageResponse(CampaignStageBase):
    id: str
    
    class Config:
        from_attributes = True

class PlayerProgressBase(BaseModel):
    highest_stage_number: int = 0
    daily_sweeps_remaining: int = 5
    daily_fast_rewards_remaining: int = 1
    last_afk_collection: datetime
    last_daily_reset: datetime

class PlayerProgressResponse(PlayerProgressBase):
    player_id: str
    
    class Config:
        from_attributes = True

class AfkRewardResponse(BaseModel):
    xp_gained: int
    gold_gained: int
    hours_calculated: float
