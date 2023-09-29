import threading
import time

import flask
import requests

team_a = "Team A"
team_b = "Team B"
draw = "DRAW"

service_run = True

app = flask.Flask("casino")

active_games = []
game_ids = {}
players_in_searching = {}


class Match:
    def __init__(self, id_):
        self.games = {}
        self.match_id = id_
        self.teams = {}
        self.results=None

    def as_json(self):
        res = {}
        for g in self.games:
            res[g] = self.games[g].__dict__
        res["match_id"] = self.match_id
        res["teams"] = self.teams
        res["results"] = self.results
        return res


class Game:
    def __init__(self, p1, action, bet, cash_pot, p2=None):
        self.p1 = p1
        self.p2 = p2
        self.action = action
        self.bet = bet
        self.cash_pot = cash_pot
        self.results = None


def tracker():
    while service_run:
        players = get_two_players()
        if players:
            game_ids["".join(players)] = Match(len(active_games))
        time.sleep(0.5)


class Casino:
    def __init__(self, name):
        self.active_games = []
        self.history_games = []

    @staticmethod
    def search_players(user_id):
        r = requests.get("http://127.0.0.1:9090/sessions",
                         params={"user_id": user_id})
        if r.ok:
            return r.json()
        return r.text, r.status_code

    @staticmethod
    def process_game(match:Match):
        if match.results:
            return flask.jsonify(match.results),200
        teamscpy = match.teams.copy()
        r = requests.get("http://127.0.0.1:8080/match", params={"team_a":teamscpy.popitem()[1]
                                                                ,"team_b":teamscpy.popitem()[1]})
        print(match.as_json())
        if not r.ok:
            return r.text, r.status_code
        match.results = r.json()
        return flask.jsonify(match.results),200

        # calculate winner do update balances


@app.post("/game")
def start_game():
    if len(game_ids) == 0:
        return "no games ready", 400
    team = flask.request.json.get("team",None)
    user = flask.request.json.get("user_id",None)
    if not user:
        return "bad request",400
    if not team:
        return "bad request",400
    for g in game_ids:
        if user in g:
            if len(game_ids[g].teams) == 2:
                return Casino.process_game(game_ids[g])
            if user not in game_ids[g].teams:
                game_ids[g].teams[user] = team
    # game logic
    return "OK", 200


def get_two_players():
    if len(players_in_searching) >= 2:
        p1 = players_in_searching.popitem()[1]
        p2 = players_in_searching.popitem()[1]
        return p1, p2
    return None


@app.get("/game")
def get_game():
    game = {}
    for arg in ("p1", "action", "bet", "cash_pot"):
        param = flask.request.args.get(arg, None)
        if not param:
            return "Bad Request", 400
        game.update({arg: param})
    p2 = flask.request.args.get("p2", None)
    game.update({"p2": p2})
    game_obj = Game(**game)
    r = requests.get("http://127.0.0.1:5555/balance", params={"user_id": game_obj.p1})
    if not r.ok:
        return r.text, r.status_code
    for g in game_ids:
        if game_obj.p1 in g:
            game_ids[g].games[game_obj.p1] = game_obj
            return flask.jsonify(game_ids[g].as_json()), 200
    if game_obj.p1 in players_in_searching:
        return "OK", 200
    if p2:
        players_in_searching[game_obj.p1] = game_obj.p1
        active_games.append(game_obj)

        return "OK", 200
    active_games.append(game_obj)
    return "OK", 200


if __name__ == '__main__':
    threading.Thread(target=tracker, daemon=True).start()
    app.run(port=5050)
    service_run = False
