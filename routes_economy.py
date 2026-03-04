from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas_economy
import crud_economy
from database import get_db

router = APIRouter()

@router.get("/wallet/{player_id}", response_model=schemas_economy.PlayerWalletResponse)
def get_wallet(player_id: str, db: Session = Depends(get_db)):
    """Retorna os Fundos do Jogador (Anti-Cheat check)"""
    return crud_economy.get_player_wallet(db, player_id)

@router.post("/gacha/{player_id}/pull", response_model=schemas_economy.GachaPullResult)
def pull_gacha(player_id: str, request: schemas_economy.GachaPullRequest, db: Session = Depends(get_db)):
    """
    O Botão de Invocar Heróis. 
    Verifica se tem grana, tira a grana, usa a RNG+Pity do Servidor,
    Cria os Heróis na conta e retorna tudo junto pra animação.
    """
    try:
        heroes, wallet_state = crud_economy.execute_gacha_pull(
            db=db, 
            player_id=player_id, 
            amount=request.amount, 
            currency=request.use_currency
        )
        return {
            "heroes_pulled": heroes,
            "wallet_state": wallet_state,
            "message": f"Você obteve {len(heroes)} heróis do Banner!"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
