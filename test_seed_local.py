from database import SessionLocal
from routes_arena import seed_mock_teams

db = SessionLocal()
try:
    res = seed_mock_teams(db)
    print("Success:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
