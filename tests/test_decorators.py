import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from flask import Flask, g
from utils.decorators import mutation_handler, log_admin_action
from core.responses import success_response

def test_mutation_handler_success():
    @mutation_handler
    def success_op():
        return success_response()
    
    app = Flask(__name__)
    with app.test_request_context():
        resp = success_op()
        assert resp[1] == 200

def test_mutation_handler_db_lock():
    @mutation_handler
    def locked_op():
        raise sqlite3.OperationalError("database is locked")
    
    app = Flask(__name__)
    with app.test_request_context():
        resp, code = locked_op()
        assert code == 503
        assert "busy" in resp.get_json()["error"]

def test_mutation_handler_generic_error():
    @mutation_handler
    def error_op():
        raise ValueError("Something went wrong")
    
    app = Flask(__name__)
    with app.test_request_context():
        resp, code = error_op()
        assert code == 500
        assert "Server error" in resp.get_json()["error"]

def test_log_admin_action():
    app = Flask(__name__)
    with app.test_request_context(method='POST', data={'target': 'user_1'}):
        g.user = {'id': 1, 'is_staff': True}
        
        mock_db = MagicMock()
        with patch('utils.decorators.get_db', return_value=mock_db):
            @log_admin_action("test_action")
            def admin_op():
                return success_response()
            
            admin_op()
            
            # Verify DB call
            mock_db.execute.assert_called_once()
            args = mock_db.execute.call_args[0]
            assert "INSERT INTO admin_ops" in args[0]
            assert args[1][1] == "test_action"
            assert args[1][2] == "user_1"
            mock_db.commit.assert_called_once()
