import flask
import requests
team_a = "Team A"
team_b = "Team B"
draw = "DRAW"

app = flask.Flask("casino")

active_games = []
class Game:
    def __init__(self,name,action,bet,cash_pot):
        self.name = name
        self.action = action
        self.bet = bet
        self.cash_pot = cash_pot
        self.results = None

    # def run(self):
        # status = run_simulation()
        # self.results = self.bet in status["status"]

    def calculate_results(self):
        if self.results:
            print("you win!")
            return self.cash_pot * 2
        else:
            print("you lose!")
            return 0

class Casino:
    def __init__(self,name):
        self.active_games = []
        self.history_games = []
        self.balance = 100

    def get_game(self,bet,pot):
        if self.balance >= pot:
            self.balance -= pot
        else:
            return None
        # return Game("game1",run_simulation,bet,pot)

@app.post("/game")
def start_game():
    if active_games == []:
        return "no games ready", 400
    game = active_games.pop(-1)
    teams = {"team_a":"REAL","team_b":"BARCA"}
    r = requests.get("http://127.0.0.1:8080/match",params=teams)
    print(game)
    if not r.ok:
        return r.text,r.status_code
    # game logic
    return r.json(),200

@app.get("/game")
def get_game():
    game = {}
    for arg in ("name","action","bet","cash_pot"):
        param = flask.request.args.get(arg,None)
        if not param:
            return "Bad Request",400
        game.update({arg:param})
    game_obj = Game(**game)
    r = requests.get("http://127.0.0.1:5555/balance", params={"user_id": game_obj.name})
    if not r.ok:
        return "Error User Not Found", 400
    active_games.append(game_obj)
    print(active_games)
    return "OK",200

# def main():
#     gui = gui_.GUI()
#     gui.mainloop()
#     casino = Casino("guest")
#     game = casino.get_game(team_b,20)
#     if not game:
#         print("balance not enough..")
#         return
#     game.run()
#     casino.balance += game.calculate_results()


if __name__ == '__main__':
    app.run(port=5050)