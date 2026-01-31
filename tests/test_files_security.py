
import unittest
import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, session
from routes.files import bp as files_bp
from app import create_app

class TestPathTraversal(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'UPLOAD_FOLDER': 'uploads',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test',
            'RATELIMIT_ENABLED': True,
            'RATELIMIT_STORAGE_URI': 'memory://'
        })
        self.client = self.app.test_client()

    def test_authenticated_traversal(self):
        # Mock authenticated session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        # Request with category='..'
        # This should resolve to .../uploads/user_1/.. -> .../uploads/
        # Then we try to access a file in uploads/.
        # But we need to know a filename that exists or just see if we get 404 (file not found in directory) vs 400 (bad request/blocked).

        response = self.client.get('/files/user_1/../nonexistent')
        print(f"Auth Response status: {response.status_code}")

        if response.status_code == 404:
            print("VULNERABLE: Code 404 means it tried to look up the file (traversal worked)")
        elif response.status_code == 400:
            print("SECURE: Code 400 means it was blocked")

    def test_avatars_traversal(self):
        # Avatars are public, no auth needed.
        response = self.client.get('/files/user_1/avatars/../nonexistent')
        # Wait, if category is avatars, then path is .../user_1/avatars/nonexistent
        # If I want traversal, I need category to BE '..'
        # But if category is '..', then it's NOT 'avatars', so I need auth.

        # So unauthenticated traversal is only possible if I can trick it to think category is 'avatars' but actually traverse.
        # e.g. category = 'avatars/..' -> forbidden by slash in route
        pass

if __name__ == '__main__':
    unittest.main()
