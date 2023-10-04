import requests
class Routes:
    prefix = "http://"
    host_url = "127.0.0.1"
    service_casino_port = 5050
    service_casino_game = "game"
    service_pay_deposit = "deposit"
    service_pay_withdraw = "withdraw"
    service_pay_balance = "balance"
    service_pay_port = 5555
    service_db_account = "account"
    service_db_port = 5556
    service_session_auth_port = 9090
    service_session_auth_login = "login"
    service_session_auth_logout = "logout"
    service_session_auth_sessions = "sessions"
    service_session_auth_register = "register"
    service_simulator_port = 8080
    service_simulator_match = "match"

def post(port,endpoint,**options):
    return fetch("POST",port,endpoint,**options)
def delete(port,endpoint,**options):
    return fetch("DELETE",port,endpoint,**options)
def put(port,endpoint,**options):
    return fetch("PUT",port,endpoint,**options)
def get(port,endpoint,**options):
    return fetch("GET",port,endpoint,**options)

def fetch(method,port,endpoint,**options) -> requests.Response  | None:
    url = f"{Routes.prefix}{Routes.host_url}:{port}/{endpoint}"
    try:
        return requests.request(method,url,**options)
    except Exception as e:
        print(e)

