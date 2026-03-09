import sys
from database import SessionLocal
from models import Player

def get_or_create_player():
    db = SessionLocal()
    player = db.query(Player).first()
    if not player:
        player = Player(username="TesterGod", email="test@godmode.com", password_hash="fake")
        db.add(player)
        db.commit()
        db.refresh(player)
        print(f"CREATED_NEW_PLAYER: {player.id}")
    else:
        print(f"FOUND_PLAYER: {player.id}")
    db.close()

if __name__ == "__main__":
    get_or_create_player()
