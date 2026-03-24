import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

def req_json(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    if data:
        data_bytes = json.dumps(data).encode("utf-8")
        req.data = data_bytes
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 500, str(e)

def test_login():
    # 1. Create a fake player
    create_data = {
        "username": "tester",
        "email": "test@test.com",
        "password": "123",
        "order_class": "SpectralBlade"
    }
    print("Creating player...")
    status, payload = req_json(f"{BASE_URL}/players/", "POST", data=create_data)
    
    player_id = None
    if status == 200:
        player_id = payload["id"]
        print(f"Player Created! ID: {player_id}")
    else:
        print("Create Player Failed!", status, payload)
        # fallback to db
        from database import SessionLocal
        import models
        db = SessionLocal()
        player = db.query(models.Player).first()
        if player:
            player_id = player.id
            print(f"Fallback to DB Player ID: {player_id}")
        else:
            print("No players found nowhere!")
            return

    # 2. Test fetchPlayer
    s1, r1 = req_json(f"{BASE_URL}/players/{player_id}")
    print(f"fetchPlayer -> {s1}")
    if s1 != 200:
        print(r1)

    # 3. Test fetchPlayerWallet
    s2, r2 = req_json(f"{BASE_URL}/economy/wallet/{player_id}")
    print(f"fetchPlayerWallet -> {s2}")
    if s2 != 200:
        print(r2)

    # 4. Test fetchBanners
    s3, r3 = req_json(f"{BASE_URL}/economy/gacha/banners")
    print(f"fetchBanners -> {s3}")
    if s3 != 200:
        print(r3)

if __name__ == "__main__":
    test_login()
