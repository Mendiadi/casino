import time

import flask
import datetime
import requests
import threading

app = flask.Flask("session_auth")
service_run = True
sessions = {}


def read_sessions():
    return
    while service_run:

        print("current sessions:")
        print(sessions)
        session_copy = sessions.copy()
        for session in session_copy.values():
            session.last_update = time.time()
            if session.last_update - session.start_time > 30:
                print("close session auto")
                session.close()
        sessions = session_copy
        time.sleep(1)


class Session:
    def __init__(self, user_id):
        self.start_time = time.time()
        self.user_id = user_id
        self.last_update = None

    def close(self):
        self.last_update = time.time()
        sessions.pop(self.user_id)
        print(f"session for {self.user_id} closed. after - {self.last_update - self.start_time}")
        return self.__dict__


@app.get("/sessions")
def get_sessions():
    u = flask.request.args.get("user_id", None)
    if not u:
        return "bad request", 400
    if u not in sessions:
        return "Unauthorized", 401
    return sessions, 200


@app.get("/login")
def get_login():
    user_id = flask.request.args.get("user_id", None)
    if not user_id:
        return "bad request", 400
    u = sessions.get(user_id, None)
    if not u:
        return flask.jsonify({"status": False}), 200
    return flask.jsonify({"status": True}), 200


@app.post("/register")
def register():
    user = flask.request.json
    res = requests.post("http://127.0.0.1:5556/account", json=user)
    if not res:
        return res.text, res.status_code
    return "OK", 200


@app.post("/login")
def login():
    user = flask.request.json
    if user["user_id"] in sessions:
        return "user logged in already", 400
    session = Session(user["user_id"])
    res = requests.get("http://127.0.0.1:5556/account", params={"user_id": user["user_id"]})
    if not res.ok:
        return res.text, res.status_code
    sessions[user["user_id"]] = session
    return "OK", 200


@app.put("/logout")
def logout():
    user = flask.request.json
    s = sessions.get(user["user_id"], None)
    if not s:
        return "user not login", 400
    s.close()
    return "ok", 200


if __name__ == '__main__':
    threading.Thread(target=read_sessions, daemon=True).start()
    app.run(port=9090)
    service_run = False
