
import requests
import json

BASE_URL = "http://localhost:5000"
USERNAME = "vibecoder"
PASSWORD = "password"

def add_audio():
    s = requests.Session()
    # Login
    print("Logging in...")
    res = s.post(f"{BASE_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
    try:
        data = res.json()
        if not data.get("ok"):
            print(f"Login failed: {data.get('error')}")
            return
    except Exception:
        print(f"Login failed (non-JSON): {res.text}")
        return

    print("Logged in. Adding Audio module...")
    
    payload = {
        "module_type": "audio",
        "content": {
            "url": "https://cdn.pixabay.com/audio/2022/03/10/audio_55a297e28b.mp3",
            "title": "Chill VibesLofi"
        },
        "display_order": 99999
    }

    res = s.post(f"{BASE_URL}/wall/post/add", json=payload)
    if res.status_code == 200:
        print("Success! Audio module added.")
    else:
        print(f"Failed: {res.text}")

if __name__ == "__main__":
    add_audio()
