import pytest
from unittest.mock import MagicMock, patch
from sockets import backfill
from flask import Flask


@pytest.fixture
def mock_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


def test_backfill_initial_load_has_limit(mock_app):
    """Verify that initial backfill (after_id=0) uses LIMIT 100."""
    with mock_app.test_request_context():
        with patch("sockets.request") as mock_request, patch(
            "sockets.get_db"
        ) as mock_get_db, patch("sockets.emit") as mock_emit, patch(
            "sockets.authenticated_sockets", {"sid1": {"room_id": 1}}
        ):

            mock_request.sid = "sid1"
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_db.execute.return_value.fetchall.return_value = []

            # Call backfill directly
            backfill({"after_id": 0})

            # Check SQL
            call_args = mock_db.execute.call_args
            sql = call_args[0][0]

            # This assertion should FAIL currently, verifying the need for the fix
            assert "LIMIT 100" in sql, "Query should limit initial load to 100"
            assert "ORDER BY id DESC" in sql, "Query should fetch latest messages first"


def test_backfill_sync_has_limit(mock_app):
    """Verify that sync backfill (after_id>0) uses LIMIT."""
    with mock_app.test_request_context():
        with patch("sockets.request") as mock_request, patch(
            "sockets.get_db"
        ) as mock_get_db, patch("sockets.emit") as mock_emit, patch(
            "sockets.authenticated_sockets", {"sid1": {"room_id": 1}}
        ):

            mock_request.sid = "sid1"
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_db.execute.return_value.fetchall.return_value = []

            # Call backfill directly
            backfill({"after_id": 100})

            # Check SQL
            call_args = mock_db.execute.call_args
            sql = call_args[0][0]

            # This assertion should FAIL currently
            assert "LIMIT" in sql, "Query should limit sync load"
