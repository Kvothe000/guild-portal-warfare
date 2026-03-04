from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
import models, schemas, crud, engine
import json
from routes_campaign import router as campaign_router
from routes_arena import router as arena_router
from routes_economy import router as economy_router

app = FastAPI(title="Guild Portal Warfare API")

# Setup CORS para permitir que o Frontend (Next.js) se comunique sem bloqueio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Para desenvolvimento. Em prod, usar ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo a nova infraestrutura modular focada no End-game
app.include_router(campaign_router, prefix="/campaign", tags=["Campaign & Idle"])
app.include_router(arena_router, prefix="/arena", tags=["PvP Arena (1v1)"])
app.include_router(economy_router, prefix="/economy", tags=["Economy & Gacha"])

@app.get("/")
def root():
    return {"message": "Welcome to Guild Portal Warfare API"}

# --- PLAYER ROUTES ---
@app.post("/players/", response_model=schemas.PlayerResponse)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player_by_email(db, email=player.email)
    if db_player:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_player(db=db, player=player)

@app.get("/players/{player_id}", response_model=schemas.PlayerResponse)
def read_player(player_id: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# --- HERO ROUTES ---
@app.post("/players/{player_id}/heroes/", response_model=schemas.HeroResponse)
def create_hero_for_player(player_id: str, hero: schemas.HeroCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return crud.create_player_hero(db=db, hero=hero, player_id=player_id)

@app.get("/players/{player_id}/heroes/", response_model=List[schemas.HeroResponse])
def read_heroes_for_player(player_id: str, db: Session = Depends(get_db)):
    return crud.get_player_heroes(db=db, player_id=player_id)

@app.put("/heroes/{hero_id}/team", response_model=schemas.HeroResponse)
def update_hero_team(hero_id: str, is_in_team: bool, db: Session = Depends(get_db)):
    try:
        updated_hero = crud.update_hero_team_status(db=db, hero_id=hero_id, is_in_team=is_in_team)
        if not updated_hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return updated_hero
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/heroes/{hero_id}/skills/", response_model=schemas.SkillResponse)
def add_skill_to_hero(hero_id: str, skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    """API para injetar skills em um Herói instanciado. Para ser usado na lógica de Summon/Gacha."""
    try:
        return crud.create_hero_skill(db=db, hero_id=hero_id, skill=skill)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- GUILD & PORTAL ROUTES ---
@app.post("/guilds/", response_model=schemas.GuildResponse)
def create_guild(guild: schemas.GuildCreate, db: Session = Depends(get_db)):
    # Simples verif. de nome por MVP (O SQLAlchemy vai jogar exception de Unique constraint tbm)
    existing = db.query(models.Guild).filter(models.Guild.name == guild.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Guild name already taken")
    return crud.create_guild(db=db, guild=guild)

@app.get("/guilds/", response_model=List[schemas.GuildResponse])
def read_guilds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_guilds(db=db, skip=skip, limit=limit)

@app.put("/players/{player_id}/guild", response_model=schemas.PlayerResponse)
def join_guild(player_id: str, guild_id: str, db: Session = Depends(get_db)):
    try:
        updated_player = crud.assign_player_to_guild(db=db, player_id=player_id, guild_id=guild_id)
        if not updated_player:
            raise HTTPException(status_code=404, detail="Player or Guild not found")
        return updated_player
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/portals/", response_model=schemas.PortalResponse)
def create_portal(portal: schemas.PortalCreate, db: Session = Depends(get_db)):
    return crud.create_portal(db=db, portal=portal)

@app.get("/portals/", response_model=List[schemas.PortalResponse])
def read_portals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_portals(db=db, skip=skip, limit=limit)

@app.put("/portals/{portal_id}/defenders", response_model=schemas.PortalResponse)
def set_portal_defenders(portal_id: str, def_1_id: str, def_2_id: str = None, def_3_id: str = None, db: Session = Depends(get_db)):
    try:
        updated_portal = crud.assign_portal_defenders(
            db=db, portal_id=portal_id, def_1_id=def_1_id, def_2_id=def_2_id, def_3_id=def_3_id
        )
        return updated_portal
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- BATTLE ROUTES ---
@app.post("/battles/test_simulation")
def test_battle_simulation(attacker_player_id: str, defender_player_id: str, db: Session = Depends(get_db)):
    # Pega o time (máx 3 heróis focados em 'is_in_team == True')
    atk_heroes = db.query(models.Hero).filter(models.Hero.player_id == attacker_player_id, models.Hero.is_in_team == True, models.Hero.current_hp > 0).limit(3).all()
    def_heroes = db.query(models.Hero).filter(models.Hero.player_id == defender_player_id, models.Hero.is_in_team == True, models.Hero.current_hp > 0).limit(3).all()
    
    if len(atk_heroes) == 0 or len(def_heroes) == 0:
        raise HTTPException(status_code=400, detail="Ambass as equipes devem ter pelo menos 1 herói vivo no time ativo.")
        
    result = engine.simulate_3v3_combat(atk_heroes, def_heroes)
    
    # Salvar Batalha de teste
    battle = models.Battle(
        attacker_player_id=attacker_player_id,
        defender_player_id=defender_player_id,
        attacker_1_id=atk_heroes[0].id if len(atk_heroes) > 0 else None,
        attacker_2_id=atk_heroes[1].id if len(atk_heroes) > 1 else None,
        attacker_3_id=atk_heroes[2].id if len(atk_heroes) > 2 else None,
        status=models.BattleStatus.Resolved,
        combat_log=json.dumps(result["log"]),
        resolved_at=datetime.datetime.utcnow()
    )
    
    # Commit changes from simulation (HP decreases) and battle record
    db.add(battle)
    db.commit()
    
    return {"message": "Battle completed", "winner": result["winner"], "battle_id": battle.id, "log": result["log"]}

@app.post("/portals/{portal_id}/attack")
def attack_portal(portal_id: str, attack_req: schemas.PortalAttackRequest, db: Session = Depends(get_db)):
    portal = crud.get_portal(db, portal_id)
    if not portal:
        raise HTTPException(status_code=404, detail="Portal not found")

    attacker_ids = [aid for aid in [attack_req.attacker_1_id, attack_req.attacker_2_id, attack_req.attacker_3_id] if aid]
    defender_ids = [did for did in [portal.defender_1_id, portal.defender_2_id, portal.defender_3_id] if did]
    
    if not attacker_ids:
        raise HTTPException(status_code=400, detail="Must provide at least 1 attacker")

    # Fetch teams
    def get_team(p_id):
        return db.query(models.Hero).filter(models.Hero.player_id == p_id, models.Hero.is_in_team == True, models.Hero.current_hp > 0).limit(3).all()

    attacker_teams = [get_team(aid) for aid in attacker_ids]
    defender_teams = [get_team(did) for did in defender_ids]
    
    # Filter empty teams
    attacker_teams = [t for t in attacker_teams if t]
    defender_teams = [t for t in defender_teams if t]

    # Vantagem para o defensor se não tiver defensores (PvE / portal livre)
    if not defender_teams:
        # Se for portal livre de monstros, podemos mockar monstros. Pro MVP, vitória instantânea.
        pass

    full_combat_log = []
    winner = "attacker" if not defender_teams else None
    
    atk_idx = 0
    def_idx = 0
    
    # King of the Hill (Survivor) logic
    while atk_idx < len(attacker_teams) and def_idx < len(defender_teams):
        current_atk_team = [h for h in attacker_teams[atk_idx] if h.current_hp > 0]
        current_def_team = [h for h in defender_teams[def_idx] if h.current_hp > 0]
        
        if not current_atk_team:
            atk_idx += 1
            continue
        if not current_def_team:
            def_idx += 1
            continue
            
        result = engine.simulate_3v3_combat(current_atk_team, current_def_team)
        full_combat_log.append({
            "match": f"Attacker {atk_idx+1} vs Defender {def_idx+1}",
            "result": result
        })
        
        if result["winner"] == "attacker":
            def_idx += 1
        elif result["winner"] == "defender":
            atk_idx += 1
        else: # draw ou double KO
            atk_idx += 1
            def_idx += 1

    final_winner = "attacker" if def_idx >= len(defender_teams) and atk_idx < len(attacker_teams) else "defender"
    if not defender_teams: final_winner = "attacker"
    
    # Identificar dono principal do ataque (para simplicidade, o Player 1 ou sua Guilda)
    main_attacker_player = db.query(models.Player).filter(models.Player.id == attacker_ids[0]).first()
    
    battle = models.Battle(
        portal_id=portal_id,
        attacker_player_id=main_attacker_player.id,
        attacker_guild_id=main_attacker_player.guild_id,
        defender_player_id=portal.controlling_player_id,
        defender_guild_id=portal.controlling_guild_id,
        status=models.BattleStatus.Resolved,
        combat_log=json.dumps(full_combat_log),
        resolved_at=datetime.datetime.utcnow()
    )
    
    if final_winner == "attacker":
        battle.winner_player_id = main_attacker_player.id
        battle.winner_guild_id = main_attacker_player.guild_id
        
        portal.controlling_player_id = main_attacker_player.id
        portal.controlling_guild_id = main_attacker_player.guild_id
        portal.defender_1_id = attack_req.attacker_1_id
        portal.defender_2_id = attack_req.attacker_2_id
        portal.defender_3_id = attack_req.attacker_3_id
    else:
        # Defensor venceu
        battle.winner_player_id = portal.controlling_player_id
        battle.winner_guild_id = portal.controlling_guild_id

    db.add(battle)
    db.commit()

    return {
        "message": f"Siege resolved. {final_winner.upper()} wins!",
        "winner": final_winner,
        "battle_id": battle.id,
        "log": full_combat_log
    }

