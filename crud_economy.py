from sqlalchemy.orm import Session
import models

# --- CRUD CARTEIRA ---

def init_player_wallet(db: Session, player_id: str):
    """Injeta a carteira em jogadores virgens se não existir no DB"""
    existing = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    if existing:
        return existing
    
    # Bonus de boas vindas para MVP (10 Rolls grátis)
    new_wallet = models.PlayerWallet(player_id=player_id, crystals_premium=5000, summon_tickets=20)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

def get_player_wallet(db: Session, player_id: str):
    wallet = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    if not wallet:
        wallet = init_player_wallet(db, player_id)
    return wallet
