
from db import get_db

def test_messages_table_exists(app):
    with app.app_context():
        db = get_db()
        row = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
        ).fetchone()
        assert row is not None
