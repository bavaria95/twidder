import sqlite3
from flask import g, Flask
import os
import binascii

app = Flask(__name__)

database_file = 'database.db'

def connect_db():
    rv = sqlite3.connect(database_file)
    rv.row_factory = sqlite3.Row
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

    db = get_db()
    c = db.cursor()

    try:
        c.execute("INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?)", data)
        db.commit()
    except:
        return {"success": False, "message": "User already exists."}

    return {"success": True, "message": "Successfully created a new user."}

def generate_token():
    token_length = 36
    return binascii.hexlify(os.urandom(token_length))

def sign_in_user(d):
    return ''


