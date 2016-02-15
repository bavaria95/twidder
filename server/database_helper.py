import sqlite3

database_file = 'database.db'

def _read_schema_file():
    schema_file = 'database.schema'

    f = open(schema_file, 'r')
    s = f.read()
    f.close()

    return s

def _create_database_structure():
    script = _read_schema_file()

    conn = sqlite3.connect(database_file)
    
    c = conn.cursor()
    c.executescript(script)
    conn.commit()
    conn.close()
