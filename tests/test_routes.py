import pytest

class TestScriptsRoutes:
    def test_save_script(self, auth_client, app):
        res = auth_client.post("/scripts/save", json={
            "title": "My Script",
            "content": "console.log('hi')",
            "script_type": "js"
        })
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

    def test_list_scripts(self, auth_client, app):
        auth_client.post("/scripts/save", json={"title": "S1", "content": "c", "script_type": "js"})
        res = auth_client.get("/scripts/list")
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["scripts"]) >= 1
        assert data["scripts"][0]["title"] == "S1"

class TestDirectoryRoutes:
    def test_list_users(self, auth_client, app):
        res = auth_client.get("/users/")
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data["users"], list)

class TestMessagesRoutes:
    def test_dm_flow(self, app):
        # Create two users
        c1 = app.test_client()
        c2 = app.test_client()
        
        # Register them
        c1.post('/auth/register', json={'username': 'alice_dm', 'password': 'p'})
        c2.post('/auth/register', json={'username': 'bob_dm', 'password': 'p'})
        
        # Get IDs (hacky via directory lookup)
        res = c1.get('/users/lookup?username=bob_dm')
        bob_id = res.get_json()['id']
        
        # Alice sends DM to Bob
        res = c1.post('/dm/send', json={'recipient_id': bob_id, 'content': 'Secret'})
        assert res.status_code == 200
        
        # Bob checks conversation
        # Login bob again just to be sure
        c2.post('/auth/login', json={'username': 'bob_dm', 'password': 'p'})
        
        # Need alice ID
        res = c2.get('/users/lookup?username=alice_dm')
        alice_id = res.get_json()['id']
        
        res = c2.get(f'/dm/conversation?with_user={alice_id}')
        assert res.status_code == 200
        msgs = res.get_json()['messages']
        assert len(msgs) == 1
        assert msgs[0]['content'] == 'Secret'
