from pydantic import BaseModel
from typing import List
from models import HeroRole
import schemas

# --- ECONOMY & GACHA SCHEMAS (Fase 7) ---

class PlayerWalletResponse(BaseModel):
    player_id: str
    gold: int
    crystals_premium: int
    guild_coins: int
    summon_tickets: int
    pity_counter: int
    
    class Config:
        from_attributes = True

class GachaPullRequest(BaseModel):
    # Quantidade de invocacoes (1 ou 10)
    amount: int
    # Opção: usar ticket ou crystal
    use_currency: str = "crystal" # 'crystal' ou 'ticket'

class GachaPullResult(BaseModel):
    heroes_pulled: List[schemas.HeroResponse]
    wallet_state: PlayerWalletResponse
    message: str
