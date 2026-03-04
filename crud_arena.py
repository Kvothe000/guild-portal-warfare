from sqlalchemy.orm import Session
import models
import schemas_arena
import engine
import json
import datetime

# --- CRUD PARA FASE 5 (ARENA 1v1) ---

def calculate_elo_change(winner_elo: int, loser_elo: int, k_factor: int = 32):
    """
    Fórmula de ELO simplificada. 
    Se o vencedor tinha muito menos pontos que o perdedor, ganha mais, e vice-versa.
    """
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    rating_change = int(k_factor * (1 - expected_winner))
    # Garantir mínimo de 1 ponto trocado para não frustrar
    return max(rating_change, 1)

def get_arena_leaderboard(db: Session, limit: int = 50):
    """Retorna o Top N jogadores focados apenas na tabela Progress onde reside a Pontuação"""
    # Join com Player para pegar o username
    results = db.query(
        models.Player.id.label("player_id"),
        models.Player.username,
        models.PlayerProgress.arena_points
    ).join(
        models.PlayerProgress, models.PlayerProgress.player_id == models.Player.id
    ).order_by(
        models.PlayerProgress.arena_points.desc()
    ).limit(limit).all()
    
    return [
        schemas_arena.ArenaLeaderboardEntry(
            player_id=r.player_id,
            username=r.username,
            arena_points=r.arena_points
        ) for r in results
    ]

def execute_arena_match(db: Session, attacker_id: str, defender_id: str):
    """
    Simula uma batalha 1v1 na Arena.
    Não usa 'Hero Lock' nem aciona 'Death Cooldown', é apenas para pontos/vaidade.
    """
    # 1. Pega os dois times principais ativos (sem stress de portais)
    atk_team = db.query(models.Hero).filter(
        models.Hero.player_id == attacker_id, 
        models.Hero.is_in_team == True, 
        models.Hero.current_hp > 0
    ).limit(3).all()
    
    def_team = db.query(models.Hero).filter(
        models.Hero.player_id == defender_id, 
        models.Hero.is_in_team == True, 
        models.Hero.current_hp > 0
    ).limit(3).all()
    
    if not atk_team:
        raise ValueError("Atacante não possui heróis vivos no time ativo.")
    if not def_team:
        raise ValueError("Defensor não possui heróis ativos.")
        
    # 2. Busca Progress para manipular pontos ELO
    atk_progress = db.query(models.PlayerProgress).filter(models.PlayerProgress.player_id == attacker_id).first()
    def_progress = db.query(models.PlayerProgress).filter(models.PlayerProgress.player_id == defender_id).first()
    
    atk_before = atk_progress.arena_points if atk_progress else 1000
    def_before = def_progress.arena_points if def_progress else 1000
    
    # 3. Roda Motor de Batalha (Mock na memória, sem persistir dano eterno se for Arena, 
    # mas o MVP do engine altera objetos em memória, então vamos rodar e depois ignoraremos o commit de HP)
    # OBS: Gostaríamos que personagens na arena curassem full hp antes/depois, 
    # mas simplificaremos pro motor atual usando a "Foto" momentânea.
    result = engine.simulate_3v3_combat(atk_team, def_team)
    
    winner_id = attacker_id if result["winner"] == "attacker" else defender_id
    loser_id = defender_id if winner_id == attacker_id else attacker_id
    
    # 4. Cálculo ELO
    winner_elo = atk_before if winner_id == attacker_id else def_before
    loser_elo = def_before if winner_id == attacker_id else atk_before
    points_exchanged = calculate_elo_change(winner_elo, loser_elo)
    
    # Atualiza pontos em memória (que vão pro BD)
    if atk_progress and def_progress:
        if winner_id == attacker_id:
            atk_progress.arena_points += points_exchanged
            def_progress.arena_points -= points_exchanged
        else:
            def_progress.arena_points += points_exchanged
            atk_progress.arena_points -= points_exchanged
            
        # Proteção para não ficar negativo
        if def_progress.arena_points < 0: def_progress.arena_points = 0
        if atk_progress.arena_points < 0: atk_progress.arena_points = 0

    # 5. Salva a Partida no Histórico
    history = models.ArenaMatch(
        attacker_player_id=attacker_id,
        defender_player_id=defender_id,
        attacker_points_before=atk_before,
        defender_points_before=def_before,
        winner_player_id=winner_id,
        points_exchanged=points_exchanged,
        combat_log=json.dumps(result["log"])
    )
    
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return {
        "match": history,
        "log": result["log"],
        "winner": result["winner"]
    }
