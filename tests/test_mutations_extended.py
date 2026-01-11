import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, g
from mutations.profile import update_profile
from mutations.profile_scripts import pin_script_view as pin_script
from mutations.sticker import add_sticker
from core.responses import success_response

import json

def test_update_profile_success():
    app = Flask(__name__)
    with app.test_request_context(method='POST', data=json.dumps({'display_name': 'New Name'}), content_type='application/json'):
        g.user = {'id': 1}
        with patch('mutations.profile.profile_service') as mock_service:
            mock_service.update_profile.return_value = True
            resp = update_profile()
            # In Flask, update_profile returns a Response object if successful
            assert resp.status_code == 200

def test_pin_script_success():
    app = Flask(__name__)
    with app.test_request_context(method='POST', data=json.dumps({'script_id': 10}), content_type='application/json'):
        g.user = {'id': 1}
        with patch('mutations.profile_scripts.pin_script') as mock_logic:
            mock_logic.return_value = {"ok": True}
            resp = pin_script()
            assert resp.status_code == 200

def test_add_sticker_success():
    app = Flask(__name__)
    with app.test_request_context(method='POST', data={'profile_id': '2', 'sticker_type': 'text', 'x_pos': '10', 'y_pos': '20'}):
        g.user = {'id': 1}
        with patch('mutations.sticker.sticker_service') as mock_service:
            result_mock = MagicMock()
            result_mock.success = True
            result_mock.data = {"id": 1} # serializable
            mock_service.add_sticker.return_value = result_mock
            resp = add_sticker()
            assert resp.status_code == 200

from services.sticker_service import add_sticker as service_add_sticker
def test_sticker_service_logic():
    app = Flask(__name__)
    with app.app_context():
        with patch('services.sticker_service.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            # First fetchone: profile, Second fetchone: username
            mock_db.execute.return_value.fetchone.side_effect = [{"id": 2}, {"username": "admin"}]
            
            result = service_add_sticker(user_id=1, profile_id=2, sticker_type="text", x_pos=10.0, y_pos=20.0, text_content="hello")
            assert result.success is True
            assert mock_db.commit.called
