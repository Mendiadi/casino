import hashlib
import json

import routes

r = routes.get(routes.Routes.service_casino_port, "external/games")
print(r, r.text)
r = routes.get(routes.Routes.service_casino_port, "external/game", params={"pid": "4_guest"})
print(r, r.text)
r = routes.get(routes.Routes.service_casino_port, "external/goals", params={"n": 4})
print(r, r.text)
r = routes.get(routes.Routes.service_casino_port, "external/goals")
print(r, r.text)
r = routes.get(routes.Routes.service_casino_port, "external/players")
print(r, r.text)
r = routes.get(routes.Routes.service_casino_port, "external/players", params={"n": 3})
print(r, r.text)

import inspect
import random
import time
import requests


def login_all(players):
    res = []
    for p in players:
        r = requests.post("http://127.0.0.1:9090/login", json={"user_id": p})
        print(r, r.text)
        res.append((r.text, r.status_code))
    return res


def log_out_all(players):
    res = []
    for p in players:
        r = requests.put("http://127.0.0.1:9090/logout", json={"user_id": p})
        print(r, r.text)

        res.append((r.text, r.status_code))
    return res


players = ("12345", "2222", "dd", "d")


def get_games_all(players):
    res = []
    for p in players:
        time.sleep(float(f"0.{random.randint(1, 9)}"))
        r = requests.get("http://127.0.0.1:5050/game",
                         params={"p1": p, "action": 2, "bet": 2, "cash_pot": 233, "p2": True})
        print(r, r.text)
        res.append((r.text, r.status_code))
    return res


def start_games_all(players):
    res = []
    for p in players:
        time.sleep(float(f"0.{random.randint(1, 9)}"))
        r = requests.post("http://127.0.0.1:5050/game",
                          json={"user_id": p, "team": p, "p2": ""})

        print(r, r.text)
        res.append((r.text, r.status_code))
    return res


def assert_all(it, v, c):
    for i in it:
        s = i[0].lower()
        if type(v) is not tuple:
            v = v.lower()

        print(f"{v} in {s} and {i[1]} == {c}")
        try:
            if type(v) is tuple:
                assert v[1].lower() in s or v[0].lower() in s and c == i[1]
            else:
                assert v in s and i[1] == c
        except AssertionError as e:
            with open("test_result.txt", "a") as f:
                f.write(
                    f"{inspect.stack()[-2].function}:{inspect.stack()[-1].function}: {e} \n {v} in {s} and {i[1]} == {c}\n{'*' * 200}\n")


def assert_one(item):
    try:
        assert item
    except AssertionError as e:
        with open("test_result.txt", "a") as f:
            f.write(
                f"{inspect.stack()[-2].function}:{inspect.stack()[-1].function}: item : {item} \n{e}\n{'*' * 200}\n")


def assert_equal(item, value, code=""):
    try:
        assert item
    except AssertionError as e:
        with open("test_result.txt", "a") as f:
            f.write(
                f"{inspect.stack()[-2].function}:{inspect.stack()[-1].function}: {item} == {value} | {code}\n{e}\n{'*' * 200}\n")


def sanity_test():
    ua401_1 = get_games_all(players)
    assert_all(ua401_1, "Unauthorized", 401)
    ua401_2 = start_games_all(players)
    assert_all(ua401_2, "Unauthorized", 401)
    login_r = login_all(players)
    assert_all(login_r, "OK", 200)
    login_er = login_all(players)
    assert_all(login_er, "logged", 400)
    er_start_games_1 = start_games_all(players)
    assert_all(er_start_games_1, "ready", 400)
    get_games_1 = get_games_all(players)
    assert_all(get_games_1, "OK", 200)
    get_games_2 = get_games_all(players)
    assert_all(get_games_2, ("OK", "{"), 200)
    get_games_3 = get_games_all(players)
    assert_all(get_games_3, ("OK", "{"), 200)
    start_games_1 = start_games_all(players)
    assert_all(start_games_1, ("OK", "}"), 200)
    start_games_2 = start_games_all(players)
    assert_all(start_games_2, ("OK", "{"), 200)
    get_games_1_1 = get_games_all(players)
    assert_all(get_games_1_1, ("OK", "{"), 200)
    get_games_2_2 = get_games_all(players)
    assert_all(get_games_2_2, ("OK", "{"), 200)
    get_games_3_3 = get_games_all(players)
    assert_all(get_games_3_3, ("OK", "{"), 200)
    start_games_1_1 = start_games_all(players)
    assert_all(start_games_1_1, ("ok", "{"), 200)
    logout = log_out_all(players)
    assert_all(logout, "ok", 200)
    logout_2 = log_out_all(players)
    assert_all(logout_2, "user", 400)
    get_games_er = get_games_all(players)
    assert_all(get_games_er, "Unauthorized", 401)
    start_games_2 = start_games_all(players)
    assert_all(start_games_2, "Unauthorized", 401)


def stress_test():
    users = []
    for i in range(50):
        users.append(f"{i}_guest")
    assert_all(login_all(users), "ok", 200)
    assert_all(get_games_all(users), ("ok", "{"), 200)
    r = routes.get(routes.Routes.service_casino_port, "external/games")
    print(r, r.text)
    r = routes.get(routes.Routes.service_casino_port, "external/game", params={"pid": "4_guest"})
    print(r, r.text)
    assert_all(start_games_all(users), ("ok", "{"), 200)
    assert_all(start_games_all(users), ("ok", "{"), 200)
    r = routes.get(routes.Routes.service_casino_port, "external/games")
    print(r, r.text)
    r = routes.get(routes.Routes.service_casino_port, "external/game", params={"pid": "4_guest"})
    print(r, r.text)

    assert_all(log_out_all(users), "ok", 200)


def unauthorized_tests():
    #casino
    assert_all(start_games_all(["2222"]), "unauthorized", 401)
    assert_all(get_games_all(["2222"]), "unauthorized", 401)
    assert_all(get_games_all(["2222"]), "unauthorized", 401)
    #pay
    r = routes.get(routes.Routes.service_pay_port, routes.Routes.service_pay_balance,
                   params={"user_id": "aa"})
    assert_all(([r.text, r.status_code]), "unauthorized", 401)
    r = routes.put(routes.Routes.service_pay_port, routes.Routes.service_pay_withdraw,
                   params={"user_id": "aa", "cash": 2})
    assert_all(([r.text, r.status_code]), "unauthorized", 401)
    r = routes.put(routes.Routes.service_pay_port, routes.Routes.service_pay_deposit,
                   params={"user_id": "aa", "cash": 2})
    assert_all(([r.text, r.status_code]), "unauthorized", 401)
    r = routes.get(routes.Routes.service_session_auth_port, routes.Routes.service_session_auth_sessions,
                   )
    assert_all(([r.text, r.status_code]), "unauthorized", 401)


def bad_params_tests():
    # casino
    login_all(["12345"])
    r = requests.get("http://127.0.0.1:5050/game",
                     params={"action": 2, "bet": 2, "cash_pot": 233, "p2": True})
    assert_equal(r.status_code, 400, r.text)
    r = requests.get("http://127.0.0.1:5050/game")
    assert_equal(r.status_code, 400, r.text)

    r = requests.post("http://127.0.0.1:5050/game",
                      json={"user_id": "12345", "p2": ""})
    assert_equal(r.status_code, 400, r.text)
    r = routes.get(routes.Routes.service_casino_port, "external/game")
    assert_equal(r.status_code, 400, r.text)
    # session

    # pay

    # db

    # simulator

def smoke_endpoints(): ...


def invalid_requests_test(): ...


def external_tests():
    login_all(["dd", "d"])
    get_games_all(["dd", "d"])
    get_games_all(["dd", "d"])
    time.sleep(0.5)
    r = routes.get(routes.Routes.service_casino_port, "external/games")
    if r.ok:
        assert_equal(len(r.json()), 1, r.status_code)
        print("\n", "*" * 100, "\n", r.json()[0], "*" * 100, r.json(), "*" * 100, "*" * 100,
              [k for k in r.json()[0]][0], "*" * 100, "\n")
        assert_one([k for k in r.json()[0]][0] == hashlib.md5("dd$d".encode()).hexdigest())
    r = routes.get(routes.Routes.service_casino_port, "external/game", params={"pid": "dd"})
    if r.ok:
        assert_equal(r.json()["p1"], "dd", r.status_code)
    start_games_all(["dd", "d"])
    start_games_all(["dd", "d"])
    time.sleep(0.5)
    r = routes.get(routes.Routes.service_casino_port, "external/goals", params={"n": 1})
    n_goals = len(r.json())
    assert_one(len(r.json()) <= 1)

    r = routes.get(routes.Routes.service_casino_port, "external/goals")
    assert_one(len(r.json()) >= n_goals)
    print(r, r.text)

    r = routes.get(routes.Routes.service_casino_port, "external/players", params={"n": 1})
    n_players = len(r.json())
    assert_one(len(r.json()) <= 1)
    print(r, r.text)
    r = routes.get(routes.Routes.service_casino_port, "external/players")
    assert_one(len(r.json()) >= n_players)
    print(r, r.text)


def session_tests(): ...


def casino_tests(): ...


def pay_service_tests(): ...


def db_tests(): ...


def test_play_game(): ...


def test_simulator():
    fields = ["assists", "goals", "yellow_cards", "red_cards", "timeline", "status", "teams_after"]
    r = routes.get(routes.Routes.service_simulator_port, routes.Routes.service_simulator_match,
                   params={"team_a": "a", "team_b": "b"})
    if r.ok:
        for field in fields:
            assert_one(field in r.json())
    assert_equal(len(r.json()["timeline"]), 90, r.status_code)
    assert_equal(r.json()["teams_after"][0]["name"].split(" ")[0], "a")
    assert_equal(r.json()["teams_after"][1]["name"].split(" ")[0], "a")


if __name__ == '__main__':
    external_tests()
    ...
