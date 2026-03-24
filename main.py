from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
from fastapi.middleware.cors import CORSMiddleware
from database import engine as db_engine, Base, get_db
import models, schemas, crud
from engine import simulate_3v3_combat
import json
from routes_campaign import router as campaign_router
from routes_arena import router as arena_router
from routes_economy import router as economy_router
from routes_progression import router as progression_router

# =============================================================================
# VEIL OF DOMINION — API v2.0
# =============================================================================

Base.metadata.create_all(bind=db_engine)

app = FastAPI(
    title="Veil of Dominion API",
    description="Backend do RPG tático por turno com sistema Gacha.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaign_router,   prefix="/campaign",  tags=["Campaign & AFK Farm"])
app.include_router(arena_router,      prefix="/arena",     tags=["PvP Arena"])
app.include_router(economy_router,    prefix="/economy",   tags=["Economy & Gacha"])
app.include_router(progression_router, prefix="",          tags=["Progression"])


@app.get("/", tags=["Root"])
def root():
    return {"message": "⚔️ Veil of Dominion API v2.0 — Enter the Rift."}


# ===========================================================================
# PLAYER ROUTES
# ===========================================================================

@app.post("/players/", response_model=schemas.PlayerResponse, tags=["Players"])
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """
    Cria um novo jogador com classe de Comandante escolhida.
    Automaticamente cria: Carteira (300 Cristais + 10 Tickets), Progresso e Comandante.
    """
    if crud.get_player_by_email(db, email=player.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    return crud.create_player(db=db, player=player)

@app.get("/players/{player_id}", response_model=schemas.PlayerResponse, tags=["Players"])
def read_player(player_id: str, db: Session = Depends(get_db)):
    player = crud.get_player(db, player_id=player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    return player


# ===========================================================================
# HERO ROUTES
# ===========================================================================

@app.post("/players/{player_id}/heroes/", response_model=schemas.HeroResponse, tags=["Heroes"])
def create_hero(player_id: str, hero: schemas.HeroCreate, db: Session = Depends(get_db)):
    if not crud.get_player(db, player_id):
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    return crud.create_player_hero(db=db, hero=hero, player_id=player_id)

@app.get("/players/{player_id}/heroes/", response_model=List[schemas.HeroResponse], tags=["Heroes"])
def read_heroes(player_id: str, db: Session = Depends(get_db)):
    return crud.get_player_heroes(db=db, player_id=player_id)

@app.put("/heroes/{hero_id}/team", response_model=schemas.HeroResponse, tags=["Heroes"])
def update_hero_team(hero_id: str, team_slot: int = None, db: Session = Depends(get_db)):
    """Define a posição de um herói no grid 3x3 (1-9). team_slot=null remove do time."""
    try:
        hero = crud.update_hero_team_slot(db=db, hero_id=hero_id, team_slot=team_slot)
        if not hero:
            raise HTTPException(status_code=404, detail="Herói não encontrado.")
        return hero
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/heroes/{hero_id}/skills/", response_model=schemas.SkillResponse, tags=["Heroes"])
def add_skill(hero_id: str, skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    """Injeta uma habilidade em um Herói — usado pelo Gacha Service após summon."""
    try:
        return crud.create_hero_skill(db=db, hero_id=hero_id, skill=skill)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===========================================================================
# CLÃ ROUTES
# ===========================================================================

@app.post("/clans/", response_model=schemas.ClanResponse, tags=["Clans"])
def create_clan(clan: schemas.ClanCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Clan).filter(models.Clan.name == clan.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nome de Clã já em uso.")
    return crud.create_clan(db=db, clan=clan)

@app.get("/clans/", response_model=List[schemas.ClanResponse], tags=["Clans"])
def read_clans(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_clans(db=db, skip=skip, limit=limit)

@app.get("/clans/{clan_id}", response_model=schemas.ClanResponse, tags=["Clans"])
def read_clan(clan_id: str, db: Session = Depends(get_db)):
    clan = crud.get_clan(db, clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clã não encontrado.")
    return clan

@app.put("/players/{player_id}/clan", response_model=schemas.PlayerResponse, tags=["Clans"])
def join_clan(player_id: str, clan_id: str, db: Session = Depends(get_db)):
    """Faz um jogador entrar em um Clã (respeitando o limite de membros por nível)."""
    try:
        player = crud.assign_player_to_clan(db=db, player_id=player_id, clan_id=clan_id)
        if not player:
            raise HTTPException(status_code=404, detail="Jogador ou Clã não encontrado.")
        return player
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/clans/{clan_id}/donate", tags=["Salão do Clã"])
def donate_to_clan(
    clan_id: str, player_id: str, amount: int, currency: str = "gold",
    db: Session = Depends(get_db)
):
    """
    O jogador doa gold ou crystals para a guilda.
    A guilda ganha EXP e sobe de level se atingir o limiar.
    O jogador lucra 'Clan Coins'.
    """
    try:
        return crud.donate_to_clan(db, clan_id, player_id, amount, currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/clans/{clan_id}/buffs", tags=["Salão do Clã"])
def get_clan_buffs(clan_id: str, db: Session = Depends(get_db)):
    """
    Retorna os buffs passivos globais do clã baseados no nível.
    Regra atual: +5% HP, +5% ATK, +5% DEF por nível do Clã.
    """
    clan = crud.get_clan(db, clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clã não encontrado.")
    
    # Exemplo: Nível 1 = +5% stats, Nível 2 = +10% stats etc
    buff_multiplier = clan.level * 0.05
    
    return {
        "clan_level": clan.level,
        "max_members": clan.max_members,
        "buffs": {
            "hp_bonus_pct": buff_multiplier,
            "atk_bonus_pct": buff_multiplier,
            "def_bonus_pct": buff_multiplier
        },
        "description": f"O Clã provê +{int(buff_multiplier*100)}% de HP, Ataque e Defesa para todos os membros."
    }

# ===========================================================================
# CLAN BOSS ROUTES
# ===========================================================================

@app.get("/clans/{clan_id}/boss", response_model=schemas.ClanBossSessionResponse, tags=["Clan Boss"])
def get_clan_boss(clan_id: str, db: Session = Depends(get_db)):
    """Retorna a sessão ativa do Boss do Clã."""
    boss = crud.get_active_clan_boss(db, clan_id)
    if not boss:
        raise HTTPException(status_code=404, detail="Nenhuma sessão de Boss ativa para este Clã.")
    return boss

@app.post("/clans/{clan_id}/boss/create", response_model=schemas.ClanBossSessionResponse, tags=["Clan Boss"])
def create_boss_session(clan_id: str, boss_level: int = 1, db: Session = Depends(get_db)):
    """Cria uma nova sessão semanal do Boss. (Admin endpoint)"""
    existing = crud.get_active_clan_boss(db, clan_id)
    if existing:
        raise HTTPException(status_code=400, detail="Já existe uma sessão de Boss ativa.")
    return crud.create_clan_boss_session(db, clan_id, boss_level)

@app.post("/clans/{clan_id}/boss/attack", tags=["Clan Boss"])
def attack_boss(
    clan_id: str, player_id: str, attacker_player_id: str,
    db: Session = Depends(get_db)
):
    """
    Ataca o Boss do Clã com o time ativo do jogador.
    Limita 3 ataques por dia por jogador. Dano calculado via engine de combate.
    """
    boss_session = crud.get_active_clan_boss(db, clan_id)
    if not boss_session:
        raise HTTPException(status_code=404, detail="Nenhuma sessão de Boss ativa.")

    # Busca time do jogador
    heroes = db.query(models.Hero).filter(
        models.Hero.player_id == attacker_player_id,
        models.Hero.team_slot.isnot(None),
        models.Hero.current_hp > 0
    ).limit(5).all()

    if not heroes:
        raise HTTPException(status_code=400, detail="Jogador não tem heróis no time.")

    # Gera inimigos do Boss baseado no level
    boss_hp = boss_session.boss_current_hp
    boss_heroes = _generate_boss_heroes(boss_session.boss_level)

    result = simulate_3v3_combat(heroes, boss_heroes)

    # Calcula dano causado
    total_boss_damage = sum(
        (b.max_hp - b.current_hp) for b in boss_heroes
    )

    try:
        updated_session = crud.attack_clan_boss(
            db, boss_session.id, attacker_player_id, total_boss_damage
        )
        return {
            "message": "Ataque ao Boss registrado.",
            "damage_dealt": total_boss_damage,
            "boss_hp_remaining": updated_session.boss_current_hp,
            "boss_defeated": updated_session.boss_current_hp <= 0,
            "combat_log": result["log"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def _generate_boss_heroes(boss_level: int) -> List[models.Hero]:
    """Gera heróis temporários representando o Boss do Clã."""
    scale = boss_level * 2
    boss = models.Hero(
        id=f"boss_main_{boss_level}",
        name=f"Lich Soberano (Nível {boss_level})",
        faction=models.HeroFaction.Shadow,
        rarity=models.HeroRarity.SSS,
        max_hp=500_000 * scale,
        current_hp=500_000 * scale,
        attack=200 * scale,
        defense=150 * scale,
        speed=80,
        team_slot=5,
        skills=[]
    )
    return [boss]


# ===========================================================================
# PORTAL ROUTES
# ===========================================================================

@app.post("/portals/", response_model=schemas.PortalResponse, tags=["Portals"])
def create_portal(portal: schemas.PortalCreate, db: Session = Depends(get_db)):
    return crud.create_portal(db=db, portal=portal)

@app.get("/portals/", response_model=List[schemas.PortalResponse], tags=["Portals"])
def read_portals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_portals(db=db, skip=skip, limit=limit)

@app.put("/portals/{portal_id}/defenders", response_model=schemas.PortalResponse, tags=["Portals"])
def set_defenders(portal_id: str, def_1_id: str, def_2_id: str = None, def_3_id: str = None, db: Session = Depends(get_db)):
    try:
        return crud.assign_portal_defenders(db, portal_id, def_1_id, def_2_id, def_3_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===========================================================================
# BATTLE ROUTES
# ===========================================================================

@app.post("/battles/simulate", tags=["Battles"])
def simulate_battle(attacker_player_id: str, defender_player_id: str, db: Session = Depends(get_db)):
    """Simula um combate rápido entre dois jogadores para testes."""
    atk_heroes = db.query(models.Hero).filter(
        models.Hero.player_id == attacker_player_id,
        models.Hero.team_slot.isnot(None),
        models.Hero.current_hp > 0
    ).limit(5).all()
    def_heroes = db.query(models.Hero).filter(
        models.Hero.player_id == defender_player_id,
        models.Hero.team_slot.isnot(None),
        models.Hero.current_hp > 0
    ).limit(5).all()

    if not atk_heroes or not def_heroes:
        raise HTTPException(status_code=400, detail="Ambas as equipes precisam de ao menos 1 herói vivo no time.")

    result = simulate_3v3_combat(atk_heroes, def_heroes)
    return {"winner": result["winner"], "log": result["log"]}

@app.post("/portals/{portal_id}/attack", tags=["Battles"])
def attack_portal(portal_id: str, attack_req: schemas.PortalAttackRequest, db: Session = Depends(get_db)):
    """Guerra de Clã: ataca um Portal com King-of-the-Hill entre times."""
    portal = crud.get_portal(db, portal_id)
    if not portal:
        raise HTTPException(status_code=404, detail="Portal não encontrado.")

    attacker_ids = [aid for aid in [attack_req.attacker_1_id, attack_req.attacker_2_id, attack_req.attacker_3_id] if aid]
    defender_ids = [did for did in [portal.defender_1_id, portal.defender_2_id, portal.defender_3_id] if did]

    if not attacker_ids:
        raise HTTPException(status_code=400, detail="Ao menos 1 atacante é necessário.")

    def get_team(p_id):
        return db.query(models.Hero).filter(
            models.Hero.player_id == p_id,
            models.Hero.team_slot.isnot(None),
            models.Hero.current_hp > 0
        ).limit(5).all()

    attacker_teams = [t for t in [get_team(aid) for aid in attacker_ids] if t]
    defender_teams = [t for t in [get_team(did) for did in defender_ids] if t]

    full_log = []
    atk_idx = def_idx = 0

    while atk_idx < len(attacker_teams) and def_idx < len(defender_teams):
        current_atk = [h for h in attacker_teams[atk_idx] if h.current_hp > 0]
        current_def = [h for h in defender_teams[def_idx] if h.current_hp > 0]

        if not current_atk:
            atk_idx += 1; continue
        if not current_def:
            def_idx += 1; continue

        result = simulate_3v3_combat(current_atk, current_def)
        full_log.append({"match": f"Atacante {atk_idx+1} vs Defensor {def_idx+1}", "result": result})

        if result["winner"] == "attacker":
            def_idx += 1
        elif result["winner"] == "defender":
            atk_idx += 1
        else:
            atk_idx += 1; def_idx += 1

    final_winner = "attacker" if (not defender_teams or def_idx >= len(defender_teams)) else "defender"

    main_attacker = db.query(models.Player).filter(models.Player.id == attacker_ids[0]).first()

    battle = models.Battle(
        portal_id=portal_id,
        attacker_player_id=main_attacker.id,
        attacker_clan_id=main_attacker.clan_id,
        defender_player_id=portal.controlling_player_id,
        defender_clan_id=portal.controlling_clan_id,
        status=models.BattleStatus.Resolved,
        combat_log=json.dumps(full_log),
        resolved_at=datetime.datetime.utcnow()
    )

    if final_winner == "attacker":
        battle.winner_player_id = main_attacker.id
        battle.winner_clan_id = main_attacker.clan_id
        portal.controlling_player_id = main_attacker.id
        portal.controlling_clan_id = main_attacker.clan_id
        portal.defender_1_id = attack_req.attacker_1_id
        portal.defender_2_id = attack_req.attacker_2_id
        portal.defender_3_id = attack_req.attacker_3_id
    else:
        battle.winner_player_id = portal.controlling_player_id
        battle.winner_clan_id = portal.controlling_clan_id

    db.add(battle)
    db.commit()

    return {
        "message": f"Cerco resolvido. {final_winner.upper()} vence!",
        "winner": final_winner,
        "battle_id": battle.id,
        "log": full_log
    }
