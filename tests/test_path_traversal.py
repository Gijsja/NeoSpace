import pytest
from flask import session, url_for

class TestPathTraversal:

    def test_unsharded_path_traversal_attempt(self, app, client):
        """
        Test that we can potentially access files outside the intended directory
        if the category parameter allows '..'.

        This test attempts to verify that the Code *would* accept '..' if the router passed it.
        """
        # We need a user session to pass the auth check (unless category is avatars)
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        # We try to access the root directory (where config.py likely lives or verify a known file)
        # The route is: /files/user_<id>/<category>/<filename>
        # We want directory to resolve to something that contains the target file.
        # directory = uploads/user_1/<category>
        # If category is '..', directory = uploads.
        # We want to access a file in uploads.

        # Let's see if we can trigger the function with category='..'
        # We bypass the router to test the function logic directly if possible,
        # but let's try via client first with encoded dot-dot.

        # %2e%2e is ..
        # If we use %2e%2e, the router might match it to <category>.
        # Then Flask decodes it to '..' before passing to the function.

        # We'll try to access a file that shouldn't be accessible via this route pattern
        # if restricted to user_1.

        # Assuming 'uploads' is empty or we don't know file names.
        # But we know this function constructs path with 'category'.

        res = client.get('/files/user_1/%2e%2e/test_file.txt')

        # If vulnerable, it tries to serve uploads/test_file.txt
        # If protected (by our fix later), it should abort(400) because '..' is in category.
        # Currently, it might 404 if file not found, but NOT 400.

        # Note: 404 means the code executed and tried to find the file (Vulnerable logic ran).
        # 400 means it was caught by security check.

        assert res.status_code == 400

    def test_sharded_is_protected(self, app, client):
        """
        Verify that the sharded route IS protected.
        Route: /files/<shard>/user_<id>/<category>/<filename>
        """
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        res = client.get('/files/shard1/user_1/%2e%2e/file.txt')
        assert res.status_code == 400
