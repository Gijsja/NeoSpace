import requests
import time

BASE_URL = "http://127.0.0.1:5000"
SESSION = requests.Session()

def test_redirect():
    print("Testing Redirect...")
    res = requests.get(f"{BASE_URL}/")
    print(f"Root status: {res.status_code} (Expect 200 after redirect to login?? No, requests follows redirects)")
    print(f"Final URL: {res.url}")
    if "/auth/login" in res.url:
        print("✅ Redirects to login")
    else:
        print("❌ Did not redirect to login")

def test_register():
    print("\nTesting Register...")
    ts = int(time.time())
    username = f"user_{ts}"
    password = "securepassword"
    
    res = SESSION.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "password": password
    })
    
    print(f"Register status: {res.status_code}")
    print(f"Response: {res.json()}")
    
    if res.ok and res.json().get('ok'):
        print("✅ Register Success")
        return username, password
    else:
        print("❌ Register Failed")
        return None, None

def test_me(username):
    print("\nTesting /auth/me...")
    res = SESSION.get(f"{BASE_URL}/auth/me")
    data = res.json()
    print(f"Me: {data}")
    
    if data.get('logged_in') and data.get('username') == username:
        print("✅ Correctly logged in")
    else:
        print("❌ Not logged in or wrong user")

def test_logout():
    print("\nTesting Logout...")
    res = SESSION.get(f"{BASE_URL}/auth/logout")
    
    # Check if session is cleared
    res = SESSION.get(f"{BASE_URL}/auth/me")
    data = res.json()
    
    if not data.get('logged_in'):
        print("✅ Successfully logged out")
    else:
        print("❌ Still logged in")

if __name__ == "__main__":
    test_redirect()
    u, p = test_register()
    if u:
        test_me(u)
        test_logout()
