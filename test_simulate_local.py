from database import SessionLocal
from main import test_battle_simulation
from routes_arena import seed_mock_teams

db = SessionLocal()
try:
    # 1. Seed
    res1 = seed_mock_teams(db)
    atk = res1["attacker_id"]
    dfd = res1["defender_id"]
    
    # 2. Simulate
    res2 = test_battle_simulation(atk, dfd, db)
    print("FINISHED:", len(res2["log"]))
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
