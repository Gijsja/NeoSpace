import requests
import sys

BASE_URL = "http://localhost:5000"
USERNAME = "AuditBot"
PASSWORD = "safe_audit_password" # nosec B105

def login(session):
    print(f"Attempting login/register with {USERNAME}...")
    
    # 1. GET login page to fetch CSRF token
    response = session.get(f"{BASE_URL}/auth/login")
    if response.status_code != 200:
        print(f"[ERR] Failed to fetch login page: {response.status_code}")
        return False
        
    # 2. Extract CSRF Token
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    except Exception as e:
        # Fallback if bs4 not installed (Regex)
        import re
        match = re.search(r'name="csrf-token" content="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
        else:
            print("[ERR] Could not find CSRF token")
            return False

    print(f"Got CSRF Token: {csrf_token[:10]}...")

    headers = {
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/json",
        "Referer": f"{BASE_URL}/auth/login"
    }
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    # 3a. Try Register First (to ensure we have a user)
    print(f"Attempting REGISTRATION for {USERNAME}...")
    reg_response = session.post(f"{BASE_URL}/auth/register", json=payload, headers=headers)
    
    if reg_response.status_code == 200:
        print("Registration SUCCESS - Logged in")
        return True
    elif reg_response.status_code == 400 and "already registered" in reg_response.text:
        print("User exists. Attempting LOGIN...")
    else:
         print(f"Registration Error: {reg_response.status_code} - {reg_response.text}")

    # 3b. Try Login
    response = session.post(f"{BASE_URL}/auth/login", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print("Login SUCCESS")
            return True
        else:
            print(f"Login FAILED: {data.get('error')}")
    else:
        print(f"Login Error: {response.status_code} - {response.text[:100]}")
    
    return False

def check_route(session, path, description):
    url = f"{BASE_URL}{path}"
    try:
        response = session.get(url, allow_redirects=True)
        status = "OK" if response.status_code == 200 else f"FAIL ({response.status_code})"
        size = len(response.text)
        is_blank = size < 500 # Arbitrary threshold for "blank"
        
        print(f"[{status}] {path:<20} | Size: {size:<6} | {description}")
        
        if is_blank:
            print(f"    WARNING: Page seems empty/small!")
            # Save snippet for debug
            with open(f"/tmp/debug_{path.replace('/', '_')}.html", "w") as f: # nosec B108
                f.write(response.text)
                
    except Exception as e:
        print(f"[ERR] {path}: {e}")

def main():
    s = requests.Session()
    
    # 1. Public Routes
    print("--- Public Routes ---")
    check_route(s, "/", "Landing/Home")
    check_route(s, "/auth/login", "Login Page")
    check_route(s, "/auth/register", "Register Page")

    # 2. Login
    print("\n--- Authentication ---")
    if not login(s):
        print("Aborting requires auth.")
        return

    # 3. Authenticated Routes
    print("\n--- Core Authenticated Routes ---")
    check_route(s, "/app", "Main App")
    check_route(s, "/feed/home", "Feed Home")
    check_route(s, "/wall", "Profile Wall") 
    check_route(s, "/directory", "Directory")
    check_route(s, "/components", "UI Kit")
    
    print("\n--- Feature Routes ---")
    check_route(s, "/codeground", "CodeGround")
    check_route(s, "/messages", "Messages")
    check_route(s, "/rooms", "Rooms Index")

if __name__ == "__main__":
    main()
