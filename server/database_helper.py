import sqlite3
from flask import g, Flask

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
