import pytest
import io
import time
from flask import url_for

@pytest.fixture
def rate_limit_app(app):
    """
    Override the app fixture to enable rate limiting.
    We modify the existing app config.
    """
    app.config["RATELIMIT_ENABLED"] = True
    app.config["RATELIMIT_STORAGE_URI"] = "memory://"
    # Ensure limiter is aware of the config change if possible,
    # but usually init_app attaches to config.
    # Flask-Limiter checks config at runtime for enabled status.
    yield app

def test_search_rate_limit(auth_client, rate_limit_app):
    """
    Verify that /search endpoint is rate limited.
    Expectation: Currently UNLIMITED (pass), will become LIMITED (fail after N).
    """
    # We want to verify that we CAN make many requests currently (Pre-fix)
    # OR that we get 429 if the fix is applied.
    # Since I am writing this BEFORE the fix, I expect NO 429s yet.
    # But to make this test useful for verification, I will structure it to
    # assert 429s eventually.

    # However, for the PLAN, I said "Initially assert that all requests return 200".

    limit = 35 # Planned limit is 30/minute
    blocked = False

    for i in range(limit):
        res = auth_client.get(f'/search/?q=test{i}')
        if res.status_code == 429:
            blocked = True
            break

    # CURRENT STATE: blocked should be False
    # FUTURE STATE: blocked should be True

    # Assert blocked is True to verify the fix
    assert blocked, "Search should be rate limited (>30/minute)"

def test_upload_rate_limit(auth_client, rate_limit_app):
    """
    Verify that /wall/post/upload is rate limited.
    """
    limit = 15 # Planned limit is 10/minute
    blocked = False

    for i in range(limit):
        data = {
            'file': (io.BytesIO(b"dummy content"), f'test{i}.jpg')
        }
        res = auth_client.post('/wall/post/upload', data=data, content_type='multipart/form-data')

        if res.status_code == 429:
            blocked = True
            break

    # Assert blocked is True to verify the fix
    assert blocked, "Uploads should be rate limited (>10/minute)"
