
import pytest
from app import create_app
from sockets import socketio
from flask import session

@pytest.fixture
def app():
    app = create_app(test_config={
        'TESTING': True,
        'SECRET_KEY': 'test',
        'DATABASE': ':memory:'
    })
    return app

def test_latency_check(app):
    flask_client = app.test_client()
    
    # Establish session
    with flask_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'tester'
        
    # Pass flask_client to socketio test client to share session/cookies
    client = socketio.test_client(app, flask_test_client=flask_client)
    
    # Should connect successfully now
    assert client.is_connected()
    
    # Check latency_check event
    start_ts = 123456789
    ack = client.emit('latency_check', {'ts': start_ts}, callback=True)
    
    assert ack == {'ts': start_ts}
    
    client.disconnect()

