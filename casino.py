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
            game_ids["".join(players)] = Match("".join(players))
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
    def process_game(match:Match,metadata):
        if match.results:
            temp = match.results.copy()
            game_ids.pop(match.match_id)
            del match
            return flask.jsonify(temp),200
        teamscpy = match.teams.copy()
        r = requests.get("http://127.0.0.1:8080/match", params={"team_a":teamscpy.popitem()[1]
                                                                ,"team_b":teamscpy.popitem()[1]})
        print(match.as_json())
        if not r.ok:
            return r.text, r.status_code
        match.results = r.json()
        metadata_bonus = {}
        for key,data in metadata.items():
            if data:
                metadata_bonus[key] = len(match.results[key]) == data
        match.results["metadata_bonus"] = metadata_bonus
        won_team = match.results["status"].replace(" win")
        for u,team in match.teams.items():
            if team != won_team:
                lost_team = team
                lost_user = u
            else:
                won_user = u
        lost_cash = 500
        won_cash = lost_cash*2
        for bonus,val in metadata_bonus.items():
            if val:
                won_cash += 50
        r = requests.put("http://127.0.0.1:5555/withdraw", params={"user_id":lost_user,"cash":
                                            lost_cash})
        if not r.ok:
            return r.text,r.status_code
        r = requests.put("http://127.0.0.1:5555/deposit", params={"user_id": won_user, "cash":
            won_cash})
        if not r.ok:
            return r.text, r.status_code

        return flask.jsonify(match.results),200

        # calculate winner do update balances


@app.post("/game")
def start_game():
    metadata_schema = {"goals":None,
                      "assists":None,
                      "red cards":None,
                      "yellow cards":None}
    team = flask.request.json.get("team", None)
    user = flask.request.json.get("user_id", None)
    metadata = flask.request.json.get("metadata",metadata_schema)
    if metadata.keys() != metadata_schema.keys():
        return "Bad metadata schema",400
    for data in metadata.values():
        if type(data) != int and data is not None:
            return f"Bad metadata type {type(data)}"
    r = requests.get("http://127.0.0.1:5555/balance", params={"user_id": user})
    if not r.ok:
        return r.text, r.status_code
    if len(game_ids) == 0:
        return "no games ready", 400

    if not user:
        return "bad request",400
    if not team:
        return "bad request",400
    for g in game_ids:
        if user in g:
            if len(game_ids[g].teams) == 2:
                return Casino.process_game(game_ids[g],metadata)
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
