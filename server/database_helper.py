import sqlite3
from flask import g, Flask
import helper

app = Flask(__name__)

database_file = 'database.db'

def connect_db():
    rv = sqlite3.connect(database_file)
    # rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db

@app.teardown_appcontext
def close_db():
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def _create_database_structure():
    schema_file = 'database.schema'

    db = get_db()
    with app.open_resource(schema_file, mode='r') as f:
        db.cursor().executescript(f.read())

def sign_up_user(d):
    try:
        data = (d['email'], d['password'], d['firstname'], d['familyname'], d['gender'], d['city'], d['country'])
    except:
        return {"success": False, "message": "Form data missing or incorrect type."}

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    try:
        c.execute("INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?)", data)
        db.commit()
    except:
        return {"success": False, "message": "User already exists."}

    return {"success": True, "message": "Successfully created a new user."}


def sign_in_user(d):
    data = (d['email'], d['password'])

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    c.execute("SELECT COUNT(*) FROM User WHERE Email=? AND Password=?", data)
    if c.fetchone()[0] == 1:
        token = helper.generate_random_token()
        return {"success": True, "message": "Successfully signed in.", "data": token}
    else:
        return {"success": False, "message": "Wrong username or password."}

