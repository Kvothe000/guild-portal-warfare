from sqlalchemy.orm import Session
import models, schemas
import hashlib

def get_player(db: Session, player_id: str):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_player_by_email(db: Session, email: str):
    return db.query(models.Player).filter(models.Player.email == email).first()

def create_player(db: Session, player: schemas.PlayerCreate):
    # Hash extremamente simples pra MVP
    fake_hashed_password = hashlib.sha256(player.password.encode()).hexdigest()
    db_player = models.Player(email=player.email, username=player.username, password_hash=fake_hashed_password)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def get_heroes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hero).offset(skip).limit(limit).all()

def create_player_hero(db: Session, hero: schemas.HeroCreate, player_id: str):
    # Status base pra todos os heróis novos. No futuro, "gacha" ou balanceamento
    db_hero = models.Hero(**hero.model_dump(), player_id=player_id)
    db.add(db_hero)
    db.commit()
    db.refresh(db_hero)
    return db_hero

def get_player_heroes(db: Session, player_id: str):
    return db.query(models.Hero).filter(models.Hero.player_id == player_id).all()

def update_hero_team_status(db: Session, hero_id: str, is_in_team: bool):
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id).first()
    if hero:
        # Se for para colocar no time, verificar se o player já tem 3 no time? (Para uma API mais sólida)
        if is_in_team:
            current_team_count = db.query(models.Hero).filter(models.Hero.player_id == hero.player_id, models.Hero.is_in_team == True).count()
            if current_team_count >= 3:
                raise ValueError("Player already has 3 heroes in the team")
                
        hero.is_in_team = is_in_team
        db.commit()
        db.refresh(hero)
    return hero

def create_hero_skill(db: Session, hero_id: str, skill: schemas.SkillCreate):
    """Adiciona uma habilidade ao grimório do herói específico."""
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id).first()
    if not hero:
        raise ValueError("Hero not found")
        
    db_skill = models.Skill(**skill.model_dump(), hero_id=hero_id)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

# --- GUILD CRUD ---
def create_guild(db: Session, guild: schemas.GuildCreate):
    db_guild = models.Guild(name=guild.name)
    db.add(db_guild)
    db.commit()
    db.refresh(db_guild)
    return db_guild

def get_guild(db: Session, guild_id: str):
    return db.query(models.Guild).filter(models.Guild.id == guild_id).first()

def get_guilds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guild).offset(skip).limit(limit).all()

def assign_player_to_guild(db: Session, player_id: str, guild_id: str):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    guild = db.query(models.Guild).filter(models.Guild.id == guild_id).first()
    
    if player and guild:
        # Lógica SIMPLES MVP: Limite baseado no level (ex: 5 * level)
        member_count = db.query(models.Player).filter(models.Player.guild_id == guild_id).count()
        if member_count >= (guild.level * 5):
            raise ValueError("Guild has reached its max member limit for its current level.")
            
        player.guild_id = guild_id
        db.commit()
        db.refresh(player)
    return player

# --- PORTAL CRUD ---
def create_portal(db: Session, portal: schemas.PortalCreate):
    db_portal = models.Portal(**portal.model_dump())
    db.add(db_portal)
    db.commit()
    db.refresh(db_portal)
    return db_portal

def get_portals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Portal).offset(skip).limit(limit).all()

def get_portal(db: Session, portal_id: str):
    return db.query(models.Portal).filter(models.Portal.id == portal_id).first()

def assign_portal_defenders(db: Session, portal_id: str, def_1_id: str, def_2_id: str = None, def_3_id: str = None):
    portal = get_portal(db, portal_id)
    if not portal:
        raise ValueError("Portal not found")
        
    portal.defender_1_id = def_1_id
    portal.defender_2_id = def_2_id
    portal.defender_3_id = def_3_id
    
    db.commit()
    db.refresh(portal)
    return portal
