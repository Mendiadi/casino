import flask
import requests
import routes
app = flask.Flask("payement service")


@app.get("/balance")
def get_balance():
    user = flask.request.args.get("user_id", None, type=str)
    print(user)
    if not user:
        return "Bad Request", 400

    res = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_db_port}/{routes.Routes.service_db_account}", params={"user_id": user})
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
    user = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_db_port}/{routes.Routes.service_db_account}", params={"user_id": acc})
    user_balance = int(user.json()["balance"])
    if not user:
        return "User Not Found", 404
    user_data = user.json().copy()
    user_data["balance"] = str(cash+user_balance)
    print(f"deposit user balance - {user_data['balance']} to {str(cash+user_balance)}")
    r=requests.put(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_db_port}/{routes.Routes.service_db_account}", json=user_data)
    return r.text,r.status_code


@app.put("/withdraw")
def withdraw():
    acc = flask.request.args.get("user_id", None, type=str)
    if not acc:
        return "Bad Request", 400
    user = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_db_port}/{routes.Routes.service_db_account}", params={"user_id": acc})
    if not user:
        return "User Not Found", 404
    cash = int(flask.request.args.get("cash", None, type=int))
    if not cash or type(cash) is not int:
        return "Bad Request", 400
    user_balance = int(user.json()["balance"])
    if user_balance < cash:
        return "Bad balance", 400
    user_data = user.json().copy()
    user_data["balance"] = str(user_balance - cash)
    print(f"deposit user balance - {user_data['balance']} to {str(user_balance-cash)}")

    r=requests.put(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_db_port}/{routes.Routes.service_db_account}", json=user_data)
    return r.text,r.status_code



def check_login():
    u = flask.request.args.get("user_id", None)
    if u:

        r = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_login}",
                         params={"user_id": u})
        if r.ok:
            if r.json()["status"]:
                return None
            return "Unauthorized", 401


if __name__ == '__main__':
    app.before_request(check_login)
    app.run(debug=True, port=routes.Routes.service_pay_port,host=routes.Routes.host_url)
