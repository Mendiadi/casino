import flask
import requests

app = flask.Flask("payement service")


@app.get("/balance")
def get_balance():
    user = flask.request.args.get("user_id", None, type=str)
    print(user)
    if not user:
        return "Bad Request", 400

    res = requests.get("http://127.0.0.1:5556/account", params={"user_id": user})
    if not user:
        return "User Not Found", 404
    if res.ok:
        return res.json().get("balance", None), 200
    return res.text, res.status_code


@app.put("/deposit")
def deposit():
    cash = flask.request.args.get("cash", None, type=int)
    acc = flask.request.args.get("user_id", None, type=str)
    if not acc:
        return "Bad Request", 400
    if not cash or type(cash) is not int:
        return "Bad Request", 400
    user = requests.get("http://127.0.0.1:5556/account", params={"user_id": acc})
    if not user:
        return "User Not Found", 404
    user.json()["balance"] += cash
    requests.put("http://127.0.0.1:5556/account", json=user.json())
    return "OK", 200


@app.put("/withdraw")
def withdraw():
    acc = flask.request.args.get("user_id", None, type=str)
    if not acc:
        return "Bad Request", 400
    user = requests.get("http://127.0.0.1:5556/account", params={"user_id": acc})
    if not user:
        return "User Not Found", 404
    cash = flask.request.args.get("cash", None, type=int)
    if not cash or type(cash) is not int:
        return "Bad Request", 400
    if user.json()["balance"] < cash:
        return "Bad balance", 400
    user.json()["balance"] -= cash
    requests.put("http://127.0.0.1:5556/account", json=user.json())
    return "OK", 200


def check_login():
    u = flask.request.args.get("user_id", None)
    if u:
        r = requests.get("http://127.0.0.1:9090/login", params={"user_id": u})
        if r.ok:
            if r.json()["status"]:
                return None
            return "Unauthorized", 401


if __name__ == '__main__':
    app.before_request(check_login)
    app.run(debug=True, port=5555)
