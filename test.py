import requests
r = requests.post("http://127.0.0.1:5050/game")
print(r,r.text)
