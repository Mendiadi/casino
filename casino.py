import hashlib
import threading
import time

import routes
from routes import Routes as urls
import flask

team_a = "Team A"
team_b = "Team B"
draw = "DRAW"

service_run = True

app = flask.Flask("casino")


class League:
    players = {}
    top_goals = {}

    def add_player(self, p_id):
        if p_id not in self.players:
            League.players.update({p_id: 0})

    def update_rate(self, p_id, rate):
        p = League.players.get(p_id, None)
        if not p:
            return
        if p + rate < 0:
            p = 0
        else:
            p = p + rate
        League.players.update({p_id: p})

    def get_player(self, pid):
        return League.players.get(pid, None)

    def add_goal(self, pid, value):
        p = League.top_goals.get(pid, None) + value
        League.top_goals.update({pid: p})

    def get_top_players(self, n=10):
        return {k: v for k, v in sorted(League.players.items(), key=lambda item: item[1])[:int(n):]}

    def get_top_goals(self, n=10):
        return {k: v for k, v in sorted(League.top_goals.items(), key=lambda item: item[1])[:int(n):]}


class PVP:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def hash(self):
        return hashlib.md5(str(self.p1 + "$" + self.p2).encode()).hexdigest()


class Match:
    def __init__(self, id_):
        self.games = {}
        self.match_id = id_
        self.teams = {}
        self.results = None

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
    # while service_run:
    players = get_two_players()
    if players:
        pvp = PVP(*players)
        Casino.pvp_dict.update({pvp.p2: pvp, pvp.p1: pvp})
        Casino.game_ids[pvp.hash()] = Match(pvp.hash())
    # time.sleep(0.5)
    print(f"casino statuses: Casino.game_ids = {[game.__dict__ for game in Casino.game_ids.values()]}")
    print(f"casino status : players_waiting_ready = {Casino.waiting_for_ready_players}")

    print(f"casino statuses: players_searching = {Casino.players_in_searching}")
    print(f"casino statuses: pvp = {Casino.pvp_dict}")


class Casino:
    waiting_for_ready_players = {}
    game_ids = {}
    players_in_searching = {}
    pvp_dict = {}

    def __init__(self, name):
        self.history_games = []

    @staticmethod
    def search_players(user_id):

        r = routes.get(urls.service_session_auth_port, urls.service_session_auth_sessions,
                       params={"user_id": user_id})
        if r.ok:
            return r.json()
        return r.text, r.status_code

    @staticmethod
    def reset(match, sender):
        print(f"reset for {sender} {match} {'=' * 100}")
        random_g = match.games.copy().popitem()[1]
        temp = match.results.copy()
        status = temp.get("status", "")
        League().add_player(random_g.p1)
        League().add_player(random_g.p2)
        team_won = status.split(" ")[0] if status != "DRAW" else None
        if team_won:
            League().update_rate(random_g.p1 if random_g.p1 != team_won else random_g.p2, -5)
            League().update_rate(team_won, 5)
        else:
            League().update_rate(random_g.p2, 1)
            League().update_rate(random_g.p1, 1)
        for g in temp.get("goals"):
            team = g.split(" ")[0]
            goals = temp.get("goals").get(g)
            League().add_goal(team, goals)
            League().update_rate(team, goals)
        Casino.pvp_dict.pop(random_g.p1, None)
        Casino.pvp_dict.pop(random_g.p2, None)
        Casino.game_ids.pop(match.match_id)
        del match
        return temp

    @staticmethod
    def process_game(sender, match: Match, metadata):
        print(f"casino statuses: Casino.game_ids = {[game.__dict__ for game in Casino.game_ids.values()]}")
        print(f"casino status : players_waiting_ready = {Casino.waiting_for_ready_players}")
        print(f"casino statuses: players_searching = {Casino.players_in_searching}")
        print(f"casino statuses: pvp = {Casino.pvp_dict}")
        if match.results:
            temp = Casino.reset(match, sender)
            return flask.jsonify(temp), 200

        teamscpy = match.teams.copy()

        r = routes.get(urls.service_simulator_port, urls.service_simulator_match,
                       params={"team_a": teamscpy.popitem()[1]
                           , "team_b": teamscpy.popitem()[1]})
        print(match.as_json())
        if not r.ok:
            return r.text, r.status_code
        match.results = r.json()
        metadata_bonus = {}
        for key, data in metadata.items():
            if data:
                metadata_bonus[key] = len(match.results[key]) == data
        match.results["metadata_bonus"] = metadata_bonus
        won_team = match.results["status"].replace(" win", "")
        for u, team in match.teams.items():
            if team != won_team:
                lost_team = team
                lost_user = u
            else:
                won_user = u
        lost_cash = 500
        won_cash = lost_cash * 2
        for bonus, val in metadata_bonus.items():
            if val:
                won_cash += 50

        r = routes.put(urls.service_pay_port, urls.service_pay_withdraw, params={"user_id": lost_team, "cash":
            lost_cash})
        if not r.ok:
            return r.text, r.status_code
        r = routes.put(urls.service_pay_port, urls.service_pay_deposit, params={"user_id": won_team, "cash":
            won_cash})
        if not r.ok:
            return r.text, r.status_code

        return "ok", 200

        # calculate winner do update balances


def start_game_schema_validation():
    metadata_schema = {"goals": None,
                       "assists": None,
                       "red cards": None,
                       "yellow cards": None}
    team = flask.request.json.get("team", None)

    user = flask.request.json.get("user_id", None)
    metadata = flask.request.json.get("metadata", metadata_schema)
    if not user:
        return "bad request", 400
    if not team:
        return "bad request", 400
    if metadata.keys() != metadata_schema.keys():
        return "Bad metadata schema", 400
    for data in metadata.values():
        if type(data) != int and data is not None:
            return f"Bad metadata type {type(data)}", 400
    return user, team, metadata


def user_validation(user):
    r = routes.get(urls.service_pay_port, urls.service_pay_balance, params={"user_id": user})
    if not r.ok:
        return r.text, r.status_code
    return None, None


def is_user_online(usr, game):
    r = routes.get(urls.service_session_auth_port, urls.service_session_auth_login,
                   params={"user_id": usr})
    if not r.ok:
        return r.text, r.status_code
    else:
        if not r.json()["status"]:
            Casino.game_ids.pop(game.match_id)
            return "user_left", 200


def kick_player(p):
    try:
        print("$" * 200)
        if p in Casino.waiting_for_ready_players:
            Casino.waiting_for_ready_players.pop(p, None)
        if p in Casino.players_in_searching:
            Casino.players_in_searching.pop(p)
    except Exception as e:
        print(e)


@app.post(f"/{urls.service_casino_game}")
def start_game():
    args = start_game_schema_validation()
    if len(args) == 2:
        return args[0], args[1]
    user, team, metadata = args
    msg, code = user_validation(user)
    if msg and code:
        return msg, code
    p2 = flask.request.json.get("p2", None)
    if not p2:
        pvp = Casino.pvp_dict.get(user, None)
        if not pvp:
            return "no pvp game ready", 400
        p2 = pvp.p1 if pvp.p1 != user else pvp.p2
    if user not in Casino.waiting_for_ready_players and not Casino.pvp_dict.get(user, None):
        return "no games ready", 400
    game = Casino.game_ids.get(Casino.pvp_dict[p2].hash())
    if len(game.teams) == 2 and p2 not in Casino.waiting_for_ready_players and user not in Casino.waiting_for_ready_players:
        return Casino.process_game(user, game, metadata)
    status = is_user_online(p2, game)
    if status is not None:
        kick_player(p2)
        return status

    if user not in game.teams and user in Casino.waiting_for_ready_players:
        Casino.waiting_for_ready_players.pop(user, None)
        game.teams[user] = team

    # game logic
    return "OK", 200


def get_two_players():
    if len(Casino.players_in_searching) >= 2:
        p1 = Casino.players_in_searching.popitem()[1]
        p2 = Casino.players_in_searching.popitem()[1]
        return p1, p2
    return None


def get_game_arg_validation():
    game = {}
    for arg in ("p1", "action", "bet", "cash_pot"):
        param = flask.request.args.get(arg, None)
        if not param:
            return "Bad Request", 400
        game.update({arg: param})
    p2 = flask.request.args.get("p2", None)
    game.update({"p2": p2})
    game_obj = Game(**game)
    return game_obj, p2, None


@app.get(f"/{urls.service_casino_game}")
def get_game():
    args = get_game_arg_validation()
    if len(args) == 2:
        return args[0], args[1]
    game_obj, p2, _ = args
    msg, code = user_validation(game_obj.p1)
    if msg and code:
        return msg, code
    pvp = Casino.pvp_dict.get(game_obj.p1, None)
    if pvp:
        game_id = Casino.game_ids.get(pvp.hash(), None)
        if game_id:
            if game_obj.p1 not in Casino.waiting_for_ready_players:
                game_id.games[game_obj.p1] = game_obj
                Casino.waiting_for_ready_players[game_obj.p1] = game_obj.p1
                game_obj.p2 = pvp.p1 if pvp.p1 != game_obj.p1 else pvp.p2
                Casino.players_in_searching.pop(game_obj.p1, None)
            return flask.jsonify(game_id.as_json()), 200
    if game_obj.p1 not in Casino.players_in_searching:
        Casino.players_in_searching[game_obj.p1] = game_obj.p1
    tracker()
    return "OK", 200


@app.get("/external/game")
def external_game():
    game_id = flask.request.args.get("user_id", None)
    if not game_id:
        return "bad request", 400
    pvp = Casino.pvp_dict.get(game_id, None)
    if pvp:
        game = Casino.game_ids.get(pvp.hash(), None)
        if game:
            return flask.jsonify(game.as_json()), 200
    return "not found", 404


@app.get("/external/games")
def external_games():
    return flask.jsonify([{k:g.as_json()}  for k,g in Casino.game_ids.items()]), 200


@app.get("/external/player_rate")
def league_player_rate():
    pid = flask.request.args.get("pid", None)
    if pid:
        p = League().get_player(pid)
        if p is not None:
            return p, 200
        else:
            return "not found", 404
    return "bad requests", 400


@app.get("/external/players")
def external_players():
    return flask.jsonify(League().get_top_players(flask.request.args.get("n", 50))), 200


@app.get("/external/goals")
def external_goals():
    return flask.jsonify(League().get_top_goals(flask.request.args.get("n", 50))), 200


if __name__ == '__main__':
    # threading.Thread(target=tracker,daemon=True).start()
    app.run(port=urls.service_casino_port, host=urls.host_url)
    service_run = False
