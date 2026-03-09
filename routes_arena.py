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

@router.post("/seed_mock_teams")
def seed_mock_teams(db: Session = Depends(get_db)):
    """ Endpoint temporário para gerar 2 jogadores com equipes perfeitamente combadas 
        para testes no Frontend Visualizer """
    import models
    from hero_skills_manifest import get_hero_template
    import uuid

    # Player 1 (Vanguard Chase Team)
    p1 = models.Player(email=f"p1_{uuid.uuid4()}@test.com", username="VanguardMaster", password_hash="fake")
    db.add(p1)
    
    # Player 2 (Shadow/Arcane Loop Team)
    p2 = models.Player(email=f"p2_{uuid.uuid4()}@test.com", username="ShadowLord", password_hash="fake")
    db.add(p2)
    db.commit()

    def build_hero(player_id, template_name, slot):
        template = get_hero_template(template_name)
        if not template: return
        
        # Instantiate Hero manually to bypass schema limits
        hero = models.Hero(
            player_id=player_id,
            name=template["name"],
            role=models.HeroRole(template["role"]),
            faction=models.HeroFaction(template["faction"]),
            rarity=models.HeroRarity(template["rarity"]),
            max_hp=template["base_stats"]["hp"] * 10, # Buff for longer fight
            current_hp=template["base_stats"]["hp"] * 10,
            attack=template["base_stats"]["attack"],
            defense=template["base_stats"]["defense"],
            speed=template["base_stats"]["speed"],
            max_mana=100, current_mana=50,
            team_slot=slot
        )
        db.add(hero)
        db.flush()

        for skill_data in template["skills"]:
            skill = models.Skill(
                hero_id=hero.id,
                name=skill_data["name"],
                skill_type=models.SkillType(skill_data["type"]),
                cooldown=skill_data.get("cooldown", 0),
                energy_cost=skill_data.get("cost", 0),
                effect_type=models.EffectType(skill_data["effect"]),
                multiplier=skill_data.get("multiplier", 1.0),
                launcher_status=models.CombatStatusEffect(skill_data.get("launcher", "NoneEffect")),
                chase_trigger=str(skill_data.get("chase_trigger", "NoneEffect")),
                chase_effect=models.CombatStatusEffect(skill_data.get("chase_effect", "NoneEffect")),
                hit_count=skill_data.get("hit_count", 1),
                apply_status=models.CombatStatusEffect(skill_data.get("apply_status", "NoneEffect")),
                advance_amount=skill_data.get("advance_amount", 0),
                delay_amount=skill_data.get("delay_amount", 0),
                max_chases_per_turn=skill_data.get("max_chases_per_turn", 1)
            )
            db.add(skill)

    # Equipe Vanguarda Perfeita: Avatar_Ignis (High Float/Repulse) -> Valkios (Repulse->Knockdown) -> Aric (Knockdown->High Float) 
    build_hero(p1.id, "Avatar_Ignis", 2)
    build_hero(p1.id, "Valkios", 5)
    build_hero(p1.id, "Aric", 8)

    # Equipe Sombras/Arcana Perfeita: Kaelen (Low Float) -> Nyx (Low Float->Repulse) -> Fenris (Repulse->Knockdown) -> Seraphine (Knockdown->High Float) -> Kaelen (High Float->Low Float)
    build_hero(p2.id, "Kaelen", 2)
    build_hero(p2.id, "Nyx", 5)
    build_hero(p2.id, "Fenris", 8)

    db.commit()

    return {
        "message": "Teams seeded successfully",
        "attacker_id": p1.id,
        "defender_id": p2.id
    }
