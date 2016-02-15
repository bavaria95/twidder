import sqlite3

def _read_schema_file():
    f = open('database.schema', 'r')
    s = f.read()
    f.close()

    return s
