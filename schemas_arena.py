from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- ARENA SCHEMAS (Fase 5) ---

class ArenaMatchRequest(BaseModel):
    # Quem ataca. Quem defende será passado na URL, mas precisamos saber quem ataca.
    attacker_player_id: str

class ArenaMatchResponse(BaseModel):
    id: str
    attacker_player_id: str
    defender_player_id: str
    attacker_points_before: int
    defender_points_before: int
    winner_player_id: Optional[str] = None
    points_exchanged: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArenaLeaderboardEntry(BaseModel):
    player_id: str
    username: str
    arena_points: int
    
    class Config:
        from_attributes = True
