from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas_economy
import schemas
import crud_economy
from database import get_db
from models import GachaBanner, PlayerBannerState
from gacha_service import pull_from_banner

router = APIRouter()

@router.get("/wallet/{player_id}", response_model=schemas_economy.PlayerWalletResponse)
def get_wallet(player_id: str, db: Session = Depends(get_db)):
    """Retorna os Fundos do Jogador (Anti-Cheat check)"""
    return crud_economy.get_player_wallet(db, player_id)

@router.get("/gacha/banners", response_model=List[schemas.GachaBannerResponse])
def get_banners(db: Session = Depends(get_db)):
    """Lista todos os Baús/Banners ativos no servidor"""
    return db.query(GachaBanner).all()

@router.get("/gacha/{player_id}/state", response_model=List[schemas.PlayerBannerStateResponse])
def get_player_banner_states(player_id: str, db: Session = Depends(get_db)):
    """Lista o histórico/pity do jogador para cada banner"""
    return db.query(PlayerBannerState).filter(PlayerBannerState.player_id == player_id).all()

@router.post("/gacha/{player_id}/pull/{banner_id}")
def pull_gacha(player_id: str, banner_id: str, amount: int = 1, db: Session = Depends(get_db)):
    """
    O Botão de Invocar Heróis. 
    Verifica se tem Aetherium/Prata, usa a RNG+Pity de Facção,
    e retorna os Heróis SSS para agitar a comunidade.
    """
    if amount not in [1, 10]:
        raise HTTPException(status_code=400, detail="Gacha pulls só suportam 1 ou 10 evocações simultâneas.")
        
    results = []
    try:
        for _ in range(amount):
            res = pull_from_banner(db, player_id, banner_id)
            results.append({
                "hero": res["hero"],
                "pity_counter_sss": res["pity_counter_sss"],
                "is_hard_pity": res["is_hard_pity"]
            })
            
        wallet = crud_economy.get_player_wallet(db, player_id)
        
        return {
            "pulls": results,
            "wallet_state": wallet,
            "message": f"Você obteve {amount} ecos do Baú."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
