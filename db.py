
import sqlite3
from flask import g

DB_PATH = "app.db"

SCHEMA = '''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    content TEXT,
    edited_at TEXT,
    deleted_at TEXT
);
'''

def get_db():
    if "db" not in g:
        db = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL;")
        g.db = db
    return g.db

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()

def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()
