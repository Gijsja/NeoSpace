
import unittest
import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

    def test_authenticated_category_traversal_blocked(self):
        """Test that authenticated users cannot use '..' in category to traverse directories."""
        # Mock authenticated session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        # Request with category='..'
        # URL structure: /files/user_<id>/<category>/<filename>
        # /files/user_1/../filename
        response = self.client.get('/files/user_1/../fakefile')

        # Assert that the request was blocked (400) rather than processed (404/200)
        self.assertEqual(response.status_code, 400, "Path traversal attempt in category should return 400 Bad Request")

    def test_filename_dots_blocked(self):
        """Test that '..' in filename is also blocked (extra defense)."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        # This matches the route: user_1 / images / suspicious..file
        response = self.client.get('/files/user_1/images/suspicious..file')
        self.assertEqual(response.status_code, 400, "Filename containing '..' should return 400 Bad Request")

if __name__ == '__main__':
    unittest.main()
