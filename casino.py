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

waiting_for_start_players = set()
waiting_for_ready_players = set()
game_ids = {}
players_in_searching = {}
pvp_dict = {}


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
        pvp_dict.update({pvp.p2: pvp, pvp.p1: pvp})
        game_ids[pvp.hash()] = Match(pvp.hash())
    # time.sleep(0.5)
    print(f"casino statuses: game_ids = {[game.__dict__ for game in game_ids.values()]}")
    print(f"casino status : players_waiting_ready = {waiting_for_ready_players}")
    print(f"casino status : players_waiting_start = {waiting_for_start_players}")
    print(f"casino statuses: players_searching = {players_in_searching}")
    print(f"casino statuses: pvp = {players_in_searching}")


class Casino:
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
    def reset(match,sender):
        waiting_for_start_players.remove(sender)
        random_g = match.games.copy().popitem()[1]
        pvp_dict.pop(random_g.p1, None)
        pvp_dict.pop(random_g.p2, None)
        temp = match.results.copy()
        game_ids.pop(match.match_id)
        del match
        return temp

    @staticmethod
    def process_game(sender,match: Match, metadata):
        print(f"casino statuses: game_ids = {[game.__dict__ for game in game_ids.values()]}")
        print(f"casino status : players_waiting_ready = {waiting_for_ready_players}")
        print(f"casino status : players_waiting_start = {waiting_for_start_players}")
        print(f"casino statuses: players_searching = {players_in_searching}")
        print(f"casino statuses: pvp = {players_in_searching}")
        if match.results:


            temp = Casino.reset(match,sender)
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

        return match.results, 200

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
            game_ids.pop(game.match_id)
            return "user_left", 200


def kick_player(p):
    try:
        if p in waiting_for_start_players:
            waiting_for_start_players.remove(p)
        if p in waiting_for_ready_players:
            waiting_for_ready_players.remove(p)
        if p in players_in_searching:
            players_in_searching.pop(p)
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
        p2 = pvp_dict[user].p1 if pvp_dict[user].p1 != user else pvp_dict[user].p2
    game = game_ids.get(pvp_dict[p2].hash())
    if len(game.teams) == 2 and p2 in waiting_for_start_players and user in waiting_for_start_players:
        return Casino.process_game(user,game, metadata)
    status = is_user_online(p2, game)
    if status is not None:
        kick_player(p2)
        return status
    if user not in waiting_for_ready_players:
        if user not in waiting_for_start_players:
            return "no games ready", 400
    if user not in game.teams:
        waiting_for_ready_players.remove(user)
        waiting_for_start_players.add(user)
        game.teams[user] = team

    # game logic
    return "OK", 200


def get_two_players():
    if len(players_in_searching) >= 2:
        p1 = players_in_searching.popitem()[1]
        p2 = players_in_searching.popitem()[1]
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
    pvp = pvp_dict.get(game_obj.p1, None)
    if pvp:
        game_id = game_ids.get(pvp.hash(), None)
        if game_id:
            game_id.games[game_obj.p1] = game_obj
            waiting_for_ready_players.add(game_obj.p1)
            game_obj.p2 = pvp.p1 if pvp.p1 != game_obj.p1 else pvp.p2
            return flask.jsonify(game_id.as_json()), 200
    if game_obj.p1 not in players_in_searching:
        players_in_searching[game_obj.p1] = game_obj.p1
    tracker()
    return "OK", 200


if __name__ == '__main__':
    # threading.Thread(target=tracker, daemon=True).start()
    app.run(port=urls.service_casino_port, host=urls.host_url)
    service_run = False
