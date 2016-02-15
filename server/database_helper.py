import sqlite3

def _read_schema_file():
    f = open('database.schema', 'r')
    s = f.read()
    f.close()

    return s

def _create_database_structure():
    script = _read_schema_file()

    conn = sqlite3.connect('database.db')
    
    c = conn.cursor()
    c.executescript(script)
    conn.commit()
    conn.close()
