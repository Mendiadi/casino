import routes

r = routes.get(routes.Routes.service_casino_port,"external/games")
print(r,r.text)
r=routes.get(routes.Routes.service_casino_port,"external/game",params={"pid":"4_guest"})
print(r,r.text)
r=routes.get(routes.Routes.service_casino_port,"external/goals",params={"n":4})
print(r,r.text)
r=routes.get(routes.Routes.service_casino_port,"external/goals")
print(r,r.text)
r=routes.get(routes.Routes.service_casino_port,"external/players")
print(r,r.text)
r=routes.get(routes.Routes.service_casino_port,"external/players",params={"n":3})
print(r,r.text)
