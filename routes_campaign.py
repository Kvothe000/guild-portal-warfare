from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import schemas_campaign
import crud_campaign

# Iniciando um router modular para isolar o escopo do main.py
router = APIRouter()

@router.post("/stages/", response_model=schemas_campaign.CampaignStageResponse)
def create_stage(stage: schemas_campaign.CampaignStageCreate, db: Session = Depends(get_db)):
    """Admin Endpoint: Cria dezenas de fases de PvE antecipadamente no DB"""
    return crud_campaign.create_campaign_stage(db, stage)

@router.get("/stages/", response_model=List[schemas_campaign.CampaignStageResponse])
def list_stages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna o mapa (Worlds/Stages) que o jogador joga"""
    return crud_campaign.get_campaign_stages(db, skip, limit)

@router.get("/progress/{player_id}", response_model=schemas_campaign.PlayerProgressResponse)
def get_progress(player_id: str, db: Session = Depends(get_db)):
    """Busca os status atuais do Idle (Limites diários, fase mais alta)"""
    return crud_campaign.get_player_progress(db, player_id)

@router.post("/progress/{player_id}/afk_collect", response_model=schemas_campaign.AfkRewardResponse)
def claim_afk_box(player_id: str, db: Session = Depends(get_db)):
    """
    O Botão principal do Gacha Hábito Diário.
    O jogador clica aqui para resgatar horas de sono convertido em Gold e XP.
    """
    reward = crud_campaign.process_afk_rewards(db, player_id)
    return reward
@router.post("/play", response_model=dict)
def play_stage(player_id: str, stage_number: int, db: Session = Depends(get_db)):
    """
    Simula jogar uma fase. O jogador ganha gold, exp e se for a primeira vez,
    avança seu progresso maximo. O drop de equipamento deverá ser chamado separadamente.
    """
    return crud_campaign.play_campaign_stage(db, player_id, stage_number)
