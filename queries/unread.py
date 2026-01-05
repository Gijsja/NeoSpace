
from flask import jsonify
from db import get_db

def unread_count():
    row = get_db().execute("SELECT COUNT(*) as c FROM messages WHERE deleted_at IS NULL").fetchone()
    return jsonify(count=row["c"])
