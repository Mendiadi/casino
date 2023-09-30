import inspect
import random
import time
import requests

def login_all(players):
    res = []
    for p in players:
        r = requests.post("http://127.0.0.1:9090/login", json={"user_id": p})
        print(r, r.text)
        res.append((r.text,r.status_code))
    return res

def log_out_all(players):
    res = []
    for p in players:
        r = requests.put("http://127.0.0.1:9090/logout", json={"user_id": p})
        print(r, r.text)

        res.append((r.text,r.status_code))
    return res
players = ("12345","2222","1111","3333","5555")

def get_games_all(players):
    res =[]
    for p in players:
        time.sleep(float(f"0.{random.randint(1,9)}"))
        r = requests.get("http://127.0.0.1:5050/game",
                        params={"p1":p, "action":2, "bet":2, "cash_pot":233,"p2":True})
        print(r,r.text)
        res.append((r.text,r.status_code))
    return res
def start_games_all(players):
    res =[]
    for p in players:
        time.sleep(float(f"0.{random.randint(1, 9)}"))
        r = requests.post("http://127.0.0.1:5050/game",
                        json={"user_id":p,"team":p})

        print(r,r.text)
        res.append((r.text,r.status_code))
    return res

def assert_all(it,v,c):

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
            with open("test_result.txt","a") as f:
                f.write(f"{inspect.stack()[-2].function}:{inspect.stack()[-1].function}: {e} \n {v} in {s} and {i[1]} == {c}\n{'*'*200}\n")
def test():

    ua401_1 = get_games_all(players)
    assert_all(ua401_1,"Unauthorized",401)
    ua401_2 = start_games_all(players)
    assert_all(ua401_2,"Unauthorized",401)
    login_r = login_all(players)
    assert_all(login_r,"OK",200)
    login_er = login_all(players)
    assert_all(login_er,"logged",400)
    er_start_games_1 = start_games_all(players)
    assert_all(er_start_games_1,"ready",400)
    get_games_1 = get_games_all(players)
    assert_all(get_games_1, "OK", 200)
    get_games_2 = get_games_all(players)
    assert_all(get_games_2, ("OK", "{"), 200)
    get_games_3 = get_games_all(players)
    assert_all(get_games_3, ("OK", "{"), 200)
    start_games_1 = start_games_all(players)
    assert_all(start_games_1, ("OK","}"), 200)
    start_games_2 = start_games_all(players)
    assert_all(start_games_2, ("OK", "{"), 200)
    get_games_1_1 = get_games_all(players)
    assert_all(get_games_1_1, ("OK", "{"), 200)
    get_games_2_2 = get_games_all(players)
    assert_all(get_games_2_2, ("OK", "{"), 200)
    get_games_3_3 = get_games_all(players)
    assert_all(get_games_3_3, ("OK", "{"), 200)
    start_games_1_1 = start_games_all(players)
    assert_all(start_games_1_1,("ok","{"),200)
    logout = log_out_all(players)
    assert_all(logout,"ok",200)
    logout_2 = log_out_all(players)
    assert_all(logout_2,"user",400)
    get_games_er = get_games_all(players)
    assert_all(get_games_er, "Unauthorized", 401)
    start_games_2 = start_games_all(players)
    assert_all(start_games_2, "Unauthorized", 401)

if __name__ == '__main__':
    # get_games_all(["1111","2222"])
    # start_games_all(["1111","2222"])
    # quit()
    # log_out_all(["2222"])
    for i in range(50):
        test()
        time.sleep(random.randint(1,5))
    # login_all(["1111","2222"])
    # get_games_all(["1111","2222"])
    # get_games_all(["1111","2222"])
    # get_games_all(["1111","2222"])
    # start_games_all("1111")
    # start_games_all("1111")
    # start_games_all("1111")
    #
    # log_out_all("2222")
    # start_games_all("1111")
    # start_games_all("1111")
    # start_games_all("1111")
    # start_games_all("1111")
    #
    # test()
