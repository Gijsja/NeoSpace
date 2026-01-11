import requests
import os
import sqlite3

BASE_URL = "http://127.0.0.1:5000"

def test_upload():
    print("Testing /upload...")
    # Create dummy image
    img_path = "test_image.png"
    with open(img_path, "wb") as f:
        f.write(os.urandom(1024))
    
    try:
        with open(img_path, "rb") as f:
            files = {'file': (img_path, f, 'image/png')}
            res = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        
        if res.status_code == 200 and res.json().get('ok'):
            print("✅ Upload Success")
        else:
            print("❌ Upload Failed")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

def test_timestamp():
    print("\nTesting Message Timestamp...")
    try:
        res = requests.post(f"{BASE_URL}/send", json={"user": "tester", "content": "timestamp check"})
        mid = res.json().get('id')
        print(f"Sent message ID: {mid}")
        
        # Check DB
        conn = sqlite3.connect("neospace.db")
        row = conn.execute("SELECT created_at FROM messages WHERE id=?", (mid,)).fetchone()
        conn.close()
        
        if row and row[0]:
            print(f"✅ Timestamp found: {row[0]}")
        else:
            print("❌ Timestamp MISSING")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_upload()
    test_timestamp()
