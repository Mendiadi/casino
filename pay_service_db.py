import executor as simpleSQL
import flask

app = flask.Flask("pay_db")


# db model class
class Account:
    # define columns in constructor
    def __init__(self, user_id, balance=5000, history=None):
        self.user_id = user_id
        self.balance = balance
        self.history = history


# create db with serverless means use sqlite
def create_db():
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        db.commit()


def create_table():
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        model = Account(
            db.types.column(db.types.varchar(50), nullable=False, unique=True),
            db.types.column(db.types.varchar(50), nullable=False),
            db.types.column(db.types.objType(1000), True)
        )
        db.create_table(Account, model, "user_id")
        db.commit()


def insert(model):
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        db.insert_to(type(model), model)
        db.commit()


def update(model):
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        db.query_update_table(type(model), model)
        db.commit()
    print(f"account {model.__dict__} updated.")


def get_all(model):
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        res = db.query_all(type(model))
        return res


def get_by_id(model, id_):
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        return db.query_filter_by(type(model), "user_id", id_, first=True)


def delete(model, col, value):
    with simpleSQL.connect(serverless=True, database="pay.db") as db:
        db.query_delete_by(type(model), (col, value))
        db.commit()


@app.put("/account")
def update_account():
    acc = flask.request.json
    print(acc , " account")
    if not acc:
        return "Bad Request", 400
    user = get_by_id(Account(0, 0, 0), acc["user_id"])
    print("user ",user)
    if not user:
        return "User Not Found", 404
    user = Account(**acc)
    update(user)
    return "OK", 200


@app.get("/account")
def get_account():
    acc = flask.request.args.get("user_id", None, type=str)
    print(acc)
    if not acc:
        return "Bad Request", 400
    user = get_by_id(Account(0, 0, 0), acc)

    if not user:
        return "User Not Found", 404
    return flask.jsonify(user.__dict__), 200


@app.post("/account")
def post_account():
    data = flask.request.json
    try:
        acc = Account(**data)
        if get_by_id(acc, acc.user_id):
            return "User Already In", 400
        insert(acc)
        return "OK", 200
    except Exception as e:
        print(e)
        return "Bad Request", 400


def main():
    create_db()
    create_table()
    app.run(debug=True, port=5556)


if __name__ == '__main__':
    main()
