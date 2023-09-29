import time

import requests
r = requests.get("http://127.0.0.1:5050/game",
                params={"p1":"12345", "action":2, "bet":2, "cash_pot":233,"p2":True})
print(r,r.text)
r = requests.get("http://127.0.0.1:5050/game",
                params={"p1":"2222", "action":2, "bet":2, "cash_pot":233,"p2":True})
print(r,r.text)
time.sleep(2)
r = requests.post("http://127.0.0.1:5050/game",
                json={"user_id":"2222","team":"REAL"})
print(r,r.text)
r = requests.post("http://127.0.0.1:5050/game",
                json={"user_id":"12345","team":"BARCA"})
print(r,r.text)
