import os
import sys

# Ensure we can import app
sys.path.append(os.getcwd())

from app import create_app
from db import get_db

app = create_app()

def verify():
    with app.test_client() as client:
        with app.app_context():
            db = get_db()
            # Ensure user tester exists
            db.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES ('tester', 'pbkdf2:sha256:123')")
            db.commit()
            
            # Get user id
            user = db.execute("SELECT id FROM users WHERE username = 'tester'").fetchone()
            user_id = user['id']
            print(f"User ID: {user_id}")
            
        # Login (We need to bypass CSRF or use a helper that simulates login session)
        # Since we are using test_client, we can directly set the session transaction?
        # Or just disable WTF_CSRF_CHECK in config for this test instance.
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Helper to simulate login
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            
        # Now trigger event
        # Test 1: login_success for 'beans' (Bot)
        # Beans is in 'The Concrete Sentinels'? No, Beans is usually "The Concrete Sentinels" or similar.
        # Let's check Beans' faction.
        print("\n--- TEST: Asking Beans ---")
        resp = client.post('/cats/speak', json={"cat": "beans", "event": "login_success"})
        print(f"Status: {resp.status_code}")
        print(f"Data: {resp.json}")
        
        # Test 2: System Error for 'root' (Pirate/Velvet Anarchs)
        print("\n--- TEST: Asking Root (Anarch) about Error ---")
        resp = client.post('/cats/speak', json={"cat": "root", "event": "system_error"})
        print(f"Data: {resp.json}")

        # Test 3: Idle for 'miso' (Static Monk)
        print("\n--- TEST: Asking Miso (Monk) to Idle ---")
        resp = client.post('/cats/speak', json={"cat": "miso", "event": "idle"})
        print(f"Data: {resp.json}")

if __name__ == "__main__":
    verify()
