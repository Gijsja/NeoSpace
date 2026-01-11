
import pytest
from flask import session, url_for

def test_register_success(client, app):
    res = client.post("/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    # auth.register returns success_response(redirect=...)
    # which is { "ok": True, "redirect": "/..." }
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    
    with client.session_transaction() as sess:
        assert sess["username"] == "newuser"

def test_register_duplicate(client, app):
    client.post("/auth/register", json={
        "username": "dup",
        "password": "password123"
    })
    res = client.post("/auth/register", json={
        "username": "dup",
        "password": "password123"
    })
    assert res.status_code == 200
    assert res.get_json()["ok"] is False
    assert "already registered" in res.get_json()["error"]

def test_login_success(client, app):
    client.post("/auth/register", json={
        "username": "testlogin",
        "password": "correct"
    })
    client.get("/auth/logout") # Clear registration session
    
    res = client.post("/auth/login", json={
        "username": "testlogin",
        "password": "correct"
    })
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    
    with client.session_transaction() as sess:
        assert sess["username"] == "testlogin"

def test_login_fail(client, app):
    client.post("/auth/register", json={
        "username": "testfail",
        "password": "correct"
    })
    
    # Wrong password
    res = client.post("/auth/login", json={
        "username": "testfail",
        "password": "wrong"
    })
    assert res.status_code == 401
    assert res.get_json()["ok"] is False
    
    # Non-existent user
    res_none = client.post("/auth/login", json={
        "username": "nobody",
        "password": "password"
    })
    assert res_none.status_code == 401

def test_logout(client, app):
    client.post("/auth/register", json={
        "username": "logoutuser",
        "password": "password"
    })
    res = client.get("/auth/logout")
    assert res.status_code == 302 # Redirect to login
    
    with client.session_transaction() as sess:
        assert "user_id" not in sess

def test_me_endpoint(client, app):
    # Guest
    res = client.get("/auth/me")
    assert res.get_json()["logged_in"] is False
    
    # Logged in
    client.post("/auth/register", json={
        "username": "meuser",
        "password": "password"
    })
    res_in = client.get("/auth/me")
    assert res_in.get_json()["logged_in"] is True
    assert res_in.get_json()["username"] == "meuser"
