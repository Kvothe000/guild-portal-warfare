import urllib.request
import urllib.error
import urllib.parse
import json

base = "https://guild-portal-warfare.onrender.com"
url1 = f"{base}/arena/seed_mock_teams"
req1 = urllib.request.Request(url1, method="POST")

try:
    with urllib.request.urlopen(req1) as response:
        body = response.read().decode()
        data = json.loads(body)
        print("SEED SUCCESS:", data["attacker_id"], data["defender_id"])

        atk = data["attacker_id"]
        def_id = data["defender_id"]
        url2 = f"{base}/battles/test_simulation?attacker_player_id={atk}&defender_player_id={def_id}"
        req2 = urllib.request.Request(url2, method="POST")

        with urllib.request.urlopen(req2) as res2:
            body2 = res2.read().decode()
            data2 = json.loads(body2)
            print("SIMULATION SUCCESS. Logs length:", len(data2.get("log", [])))

except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Error Body:", e.read().decode())
