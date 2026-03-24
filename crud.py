from sqlalchemy.orm import Session
import models, schemas
import hashlib
from models import PlayerOrderClass

# =============================================================================
# VEIL OF DOMINION — CRUD v2.0
# =============================================================================

# --- PLAYER ---

def get_player(db: Session, player_id: str):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_player_by_email(db: Session, email: str):
    return db.query(models.Player).filter(models.Player.email == email).first()

def create_player(db: Session, player: schemas.PlayerCreate):
    """Cria Player + PlayerProgress + PlayerWallet + PlayerCommander de uma vez."""
    password_hash = hashlib.sha256(player.password.encode()).hexdigest()
    db_player = models.Player(
        email=player.email,
        username=player.username,
        password_hash=password_hash
    )
    db.add(db_player)
    db.flush()

    # Progresso inicial
    progress = models.PlayerProgress(player_id=db_player.id)
    db.add(progress)

    # Carteira inicial
    wallet = models.PlayerWallet(
        player_id=db_player.id,
        summon_tickets=10,  # 10 tickets grátis no início
        crystals_premium=300  # 300 Cristais de boas-vindas
    )
    db.add(wallet)

    # Comandante da Ordem (Avatar do jogador)
    commander_stats = _get_commander_base_stats(player.order_class)
    commander = models.PlayerCommander(
        player_id=db_player.id,
        order_class=player.order_class,
        **commander_stats
    )
    db.add(commander)

    db.commit()
    db.refresh(db_player)
    return db_player

def _get_commander_base_stats(order_class: PlayerOrderClass) -> dict:
    """Retorna os stats base de cada classe de Comandante."""
    stats_map = {
        PlayerOrderClass.FlameInquisitor: {"max_hp": 2000, "current_hp": 2000, "attack": 180, "defense": 110, "speed": 105},
        PlayerOrderClass.EtherChronist:   {"max_hp": 1700, "current_hp": 1700, "attack": 140, "defense": 100, "speed": 145},
        PlayerOrderClass.SpectralBlade:   {"max_hp": 1500, "current_hp": 1500, "attack": 200, "defense": 90,  "speed": 155},
        PlayerOrderClass.StoneCleric:     {"max_hp": 2400, "current_hp": 2400, "attack": 110, "defense": 180, "speed": 95},
        PlayerOrderClass.LunarHunter:     {"max_hp": 1600, "current_hp": 1600, "attack": 160, "defense": 95,  "speed": 135},
    }
    return stats_map.get(order_class, {"max_hp": 2000, "current_hp": 2000, "attack": 150, "defense": 120, "speed": 110})


# --- HEROES ---

def get_player_heroes(db: Session, player_id: str):
    return db.query(models.Hero).filter(models.Hero.player_id == player_id).all()

def create_player_hero(db: Session, hero: schemas.HeroCreate, player_id: str):
    db_hero = models.Hero(**hero.model_dump(), player_id=player_id)
    db.add(db_hero)
    db.commit()
    db.refresh(db_hero)
    return db_hero

def update_hero_team_slot(db: Session, hero_id: str, team_slot: int = None):
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id).first()
    if not hero:
        return None
    if team_slot is not None:
        if team_slot < 1 or team_slot > 9:
            raise ValueError("Slot do grid deve ser entre 1 e 9.")

        current_team = db.query(models.Hero).filter(
            models.Hero.player_id == hero.player_id,
            models.Hero.team_slot.isnot(None)
        ).all()
        other_members = [h for h in current_team if h.id != hero_id]
        if len(other_members) >= 5:
            raise ValueError("Limite de equipe (5 Heróis) atingido.")
        if any(h.team_slot == team_slot for h in other_members):
            raise ValueError(f"Slot {team_slot} já está ocupado.")

    hero.team_slot = team_slot
    db.commit()
    db.refresh(hero)
    return hero

def create_hero_skill(db: Session, hero_id: str, skill: schemas.SkillCreate):
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id).first()
    if not hero:
        raise ValueError("Herói não encontrado.")
    db_skill = models.Skill(**skill.model_dump(), hero_id=hero_id)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


# --- CLÃS ---

def create_clan(db: Session, clan: schemas.ClanCreate):
    db_clan = models.Clan(name=clan.name, description=clan.description)
    db.add(db_clan)
    db.commit()
    db.refresh(db_clan)
    return db_clan

def get_clan(db: Session, clan_id: str):
    return db.query(models.Clan).filter(models.Clan.id == clan_id).first()

def get_clans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Clan).offset(skip).limit(limit).all()

def assign_player_to_clan(db: Session, player_id: str, clan_id: str):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    clan = db.query(models.Clan).filter(models.Clan.id == clan_id).first()
    if not player or not clan:
        return None

    member_count = db.query(models.Player).filter(models.Player.clan_id == clan_id).count()
    if member_count >= clan.max_members:
        raise ValueError(f"Clã atingiu o limite de {clan.max_members} membros (Nível {clan.level}).")

    player.clan_id = clan_id
    db.commit()
    db.refresh(player)
    return player

def get_clan_level_requirement(level: int):
    """Calcula a EXP necessária para uppar o Clã."""
    return level * 5000  # Nível 1 -> 5000, Nível 2 -> 10000, etc.

def donate_to_clan(db: Session, clan_id: str, player_id: str, amount: int, currency="gold"):
    clan = get_clan(db, clan_id)
    wallet = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    
    if not clan or not wallet:
        raise ValueError("Clã ou jogador não encontrado.")
    
    if amount <= 0:
        raise ValueError("A quantidade deve ser positiva.")
        
    if currency == "gold":
        if wallet.gold < amount:
            raise ValueError("Ouro insuficiente.")
        wallet.gold -= amount
        clan.experience += amount // 10  # Cada 10 de gold = 1 de EXP pro clã
        wallet.clan_coins += amount // 100 # Ganha clan coins
    elif currency == "crystals":
        if wallet.crystals_premium < amount:
            raise ValueError("Cristais insuficientes.")
        wallet.crystals_premium -= amount
        clan.experience += amount * 5    # Cada 1 cristal = 5 EXP
        wallet.clan_coins += amount      # Ganha clan coins na memsa proporção
    else:
        raise ValueError("Moeda inválida. Use 'gold' ou 'crystals'.")
        
    # Level up logic
    while True:
        req = get_clan_level_requirement(clan.level)
        if clan.experience >= req:
            clan.experience -= req
            clan.level += 1
        else:
            break
            
    db.commit()
    db.refresh(clan)
    return {
        "clan": clan, 
        "wallet": wallet, 
        "message": f"Doação de {amount} {currency} realizada! O clã ganhou exp e você ganhou Clan Coins."
    }


# --- PORTAIS ---

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
        raise ValueError("Portal não encontrado.")
    portal.defender_1_id = def_1_id
    portal.defender_2_id = def_2_id
    portal.defender_3_id = def_3_id
    db.commit()
    db.refresh(portal)
    return portal


# --- CLAN BOSS ---

def get_active_clan_boss(db: Session, clan_id: str):
    return db.query(models.ClanBossSession).filter(
        models.ClanBossSession.clan_id == clan_id,
        models.ClanBossSession.status == models.ClanBossStatus.Active
    ).first()

def create_clan_boss_session(db: Session, clan_id: str, boss_level: int = 1):
    """Cria uma nova sessão semanal do Boss do Clã."""
    import datetime
    session = models.ClanBossSession(
        clan_id=clan_id,
        boss_level=boss_level,
        boss_max_hp=1_000_000 * boss_level,
        boss_current_hp=1_000_000 * boss_level,
        week_start=datetime.datetime.utcnow(),
        week_end=datetime.datetime.utcnow() + datetime.timedelta(days=7)
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def attack_clan_boss(db: Session, session_id: str, player_id: str, damage: int):
    """Registra o dano de um jogador ao Boss do Clã."""
    import datetime
    session = db.query(models.ClanBossSession).filter(models.ClanBossSession.id == session_id).first()
    if not session or session.status != models.ClanBossStatus.Active:
        raise ValueError("Sessão do Boss não encontrada ou já finalizada.")

    # Verifica se o jogador já usou todos os ataques do dia
    progress = db.query(models.PlayerProgress).filter(models.PlayerProgress.player_id == player_id).first()
    if not progress or progress.daily_boss_attacks_remaining <= 0:
        raise ValueError("Você não tem mais ataques ao Boss disponíveis hoje.")

    # Registra/atualiza contribuição do jogador
    contribution = db.query(models.ClanBossDamage).filter(
        models.ClanBossDamage.session_id == session_id,
        models.ClanBossDamage.player_id == player_id
    ).first()

    if not contribution:
        contribution = models.ClanBossDamage(
            session_id=session_id, player_id=player_id,
            damage_dealt=0, attacks_used=0
        )
        db.add(contribution)

    contribution.damage_dealt += damage
    contribution.attacks_used += 1
    contribution.last_attack_at = datetime.datetime.utcnow()

    # Reduz HP do Boss
    session.boss_current_hp = max(0, session.boss_current_hp - damage)
    if session.boss_current_hp <= 0:
        session.status = models.ClanBossStatus.Defeated
        session.week_end = datetime.datetime.utcnow()

    # Consome ticket de ataque do dia
    progress.daily_boss_attacks_remaining -= 1

    db.commit()
    db.refresh(session)
    return session
