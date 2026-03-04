from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import schemas_arena
import crud_arena

# Roteador Modular para PvP 1v1
router = APIRouter()

@router.get("/leaderboard", response_model=List[schemas_arena.ArenaLeaderboardEntry])
def get_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    """Retorna o top N jogadores rankeados por pontos de Arena"""
    return crud_arena.get_arena_leaderboard(db, limit)

@router.post("/match/{defender_id}")
def attack_in_arena(defender_id: str, request: schemas_arena.ArenaMatchRequest, db: Session = Depends(get_db)):
    """
    Consome 1 'ticket' (lógica futura) e inicia simulação de Arena 
    contra a defesa offline do jogador 'defender_id' e salva no histórico.
    """
    if defender_id == request.attacker_player_id:
        raise HTTPException(status_code=400, detail="Você não pode se atacar na Arena.")
        
    try:
        resultado = crud_arena.execute_arena_match(db, request.attacker_player_id, defender_id)
        return {
            "message": "Partida concluída.",
            "winner_side": resultado["winner"],
            "match_id": resultado["match"].id,
            "points_exchanged": resultado["match"].points_exchanged,
            "log": resultado["log"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
