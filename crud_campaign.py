from sqlalchemy.orm import Session
import models
import schemas_campaign
import datetime

# --- CRUD PARA FASE 4 (PvE & IDLE) ---

def create_campaign_stage(db: Session, stage: schemas_campaign.CampaignStageCreate):
    """Cria uma nova fase no banco de dados (ex: pelo painel de admin)"""
    db_stage = models.CampaignStage(**stage.model_dump())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage

def get_campaign_stages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CampaignStage).order_by(models.CampaignStage.stage_number.asc()).offset(skip).limit(limit).all()

def init_player_progress(db: Session, player_id: str):
    """
    Função vital: Inicia a tabela de progresso atrelada a um jogador novo.
    Chamado automaticamente quando a conta é criada (ou no primeiro login se não existir).
    """
    existing = db.query(models.PlayerProgress).filter(models.PlayerProgress.player_id == player_id).first()
    if existing:
        return existing
        
    new_progress = models.PlayerProgress(player_id=player_id)
    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)
    return new_progress

def get_player_progress(db: Session, player_id: str):
    progress = db.query(models.PlayerProgress).filter(models.PlayerProgress.player_id == player_id).first()
    if not progress:
        # Auto-init para retrocompatibilidade com contas velhas no MVP
        progress = init_player_progress(db, player_id)
    return progress

def process_afk_rewards(db: Session, player_id: str):
    """
    Coração matemático do Idle System (Caixa AFK).
    Calcula tempo offline e gera a recompensa baseada na fase de PvE mais alta concluída.
    """
    progress = get_player_progress(db, player_id)
    
    now = datetime.datetime.utcnow()
    time_diff = now - progress.last_afk_collection
    hours_passed = time_diff.total_seconds() / 3600.0
    
    # Cap de 24 horas máximo de baú AFK para forçar o login diário
    if hours_passed > 24.0:
        hours_passed = 24.0
        
    # Busca a fase atual para saber a "Renda" do jogador
    current_stage = db.query(models.CampaignStage).filter(
        models.CampaignStage.stage_number == progress.highest_stage_number
    ).first()
    
    # Valores matemáticos fallback se o jogador não passou o 1-1 ainda
    xp_rate = current_stage.afk_xp_per_hour if current_stage else 10
    gold_rate = current_stage.afk_gold_per_hour if current_stage else 20
    
    gained_xp = int(hours_passed * xp_rate)
    gained_gold = int(hours_passed * gold_rate)
    
    # Zera o cofre (redefine timestamp)
    progress.last_afk_collection = now
    db.commit()
    
    # Nota Fazer: Aqui precisará enviar o gold e xp real para uma tabela de inventário/player no futuro
    
    return {"xp_gained": gained_xp, "gold_gained": gained_gold, "hours_calculated": round(hours_passed, 2)}
