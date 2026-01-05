
from flask import jsonify
from db import get_db

def backfill_messages():
    rows = get_db().execute("SELECT id,user,content FROM messages").fetchall()
    return jsonify(messages=[dict(r) for r in rows])
