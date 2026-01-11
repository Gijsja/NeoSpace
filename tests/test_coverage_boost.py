
import pytest
import io
import json
from services.cats.brain import CatBrain
from services.cats import semantics
from db import get_db

@pytest.fixture
def test_user_id(app):
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT id FROM users WHERE username = 'testuser'").fetchone()
        return user['id'] if user else None

class TestProfileMutations:
    def test_get_profile_self(self, auth_client):
        res = auth_client.get("/profile/")
        assert res.status_code == 200
        data = res.get_json()
        assert "username" in data
        assert "profile_id" in data

    def test_get_profile_by_id(self, auth_client, app):
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES ('other', 'hash')")
            user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("INSERT INTO profiles (user_id, display_name) VALUES (?, 'Other User')", (user_id,))
            db.commit()

        res = auth_client.get(f"/profile/?user_id={user_id}")
        assert res.status_code == 200
        assert res.get_json()["username"] == "other"

    def test_update_profile_success(self, auth_client):
        res = auth_client.get("/auth/me")
        print(f"DEBUG: auth/me response: {res.get_json()}")
        
        res = auth_client.post("/profile/update", json={
            "display_name": "New Name",
            "bio": "New Bio",
            "status_message": "Chilling"
        })
        if res.status_code != 200:
            print(f"DEBUG: update failure: {res.status_code} - {res.get_data(as_text=True)}")
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

    def test_update_profile_validation_fail(self, auth_client):
        res = auth_client.post("/profile/update", json={
            "display_name": "A" * 100
        })
        assert res.status_code == 400

    def test_upload_avatar_success(self, auth_client):
        data = {
            'avatar': (io.BytesIO(b"fake image data"), 'test.png')
        }
        res = auth_client.post("/profile/avatar", data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

    def test_add_sticker_multipart(self, auth_client):
        data = {
            'image': (io.BytesIO(b"fake sticker"), 'sticker.png'),
            'x': '10',
            'y': '20',
            'rotation': '45'
        }
        res = auth_client.post("/profile/sticker/add", data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

    def test_add_sticker_json(self, auth_client, app):
        # We need to know our own ID
        with app.app_context():
             db = get_db()
             users = db.execute("SELECT * FROM users").fetchall()
             profiles = db.execute("SELECT * FROM profiles").fetchall()
             print(f"DEBUG: users={[dict(u) for u in users]}")
             print(f"DEBUG: profiles={[dict(p) for p in profiles]}")
             u = db.execute("SELECT id FROM users WHERE username = 'testuser'").fetchone()
             u_id = u['id'] if u else 1

        res = auth_client.post("/profile/sticker/add", json={
            "sticker_type": "emoji",
            "target_user_id": u_id,
            "x": 50,
            "y": 60,
            "rotation": 0
        })
        if res.status_code != 200:
             print(f"DEBUG: add_sticker_json fail: {res.status_code} - {res.get_data(as_text=True)}")
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

class TestCatLogic:
    def test_brain_pad_calculations(self):
        brain = CatBrain()
        current = (0.0, 0.0, 0.0)
        impact = (0.5, 0.5, 0.5)
        new_pad = brain.calculate_new_pad(current, impact, decay=0.0)
        assert new_pad == (0.5, 0.5, 0.5)
        
        # Test clamping
        extreme_impact = (2.0, -2.0, 0.0)
        clamped = brain.calculate_new_pad(current, extreme_impact, decay=0.0)
        assert clamped == (1.0, -1.0, 0.0)

    def test_brain_named_states(self):
        brain = CatBrain()
        assert brain.get_named_state((0.5, 0.5, 0.0)) == "Playful"
        assert brain.get_named_state((0.5, -0.5, 0.0)) == "Relaxed"
        assert brain.get_named_state((-0.5, 0.5, 0.0)) == "Irritated"
        assert brain.get_named_state((-0.5, -0.5, 0.0)) == "Grumpy"
        assert brain.get_named_state((0.0, 0.6, 0.0)) == "Alert"
        assert brain.get_named_state((0.0, -0.6, 0.0)) == "Sleepy"
        assert brain.get_named_state((0.0, 0.0, 0.0)) == "Zen"

    def test_brain_deed_impacts(self):
        brain = CatBrain()
        # Test Default
        impact, op = brain.get_deed_impact("login_success", "General")
        assert op == 5.0
        
        # Test Anarchs
        impact, op = brain.get_deed_impact("system_error", "The Velvet Anarchs")
        assert op == 5.0
        assert impact[0] > 0 # They find it funny
        
        # Test Sentinels
        impact, op = brain.get_deed_impact("system_error", "The Concrete Sentinels")
        assert op == -20.0

class TestCatSemantics:
    def test_status_keys(self):
        assert semantics.get_status_key(0, 0) == "stranger"
        assert semantics.get_status_key(0, 5) == "neutral"
        assert semantics.get_status_key(80, 5) == "close"
        assert semantics.get_status_key(-80, 5) == "hostile"

    def test_faction_labels(self):
        label = semantics.get_faction_label("The Neon Claws", 80, 10)
        assert label == "Locked in"
        
        # Fallback
        label = semantics.get_faction_label("Fake Faction", 0, 1)
        assert label == "No issue"

    def test_detailed_status(self):
        assert semantics.get_detailed_status(0, 0) == "Unknown"
        assert semantics.get_detailed_status(0, 1) == "Just Met"
        assert semantics.get_detailed_status(95, 10) == "Respected"
        assert semantics.get_detailed_status(-95, 10) == "Cut Off"
        assert semantics.get_detailed_status(55, 10) == "Trusted"
        assert semantics.get_detailed_status(-55, 10) == "Watching You"

    def test_vocalizations(self):
        voc = semantics.get_idle_vocalization("The Soft Collapse", 99, 10)
        assert voc == "Zzz."
        voc = semantics.get_idle_vocalization("The Neon Claws", -99, 10)
        assert voc == "Snap."
