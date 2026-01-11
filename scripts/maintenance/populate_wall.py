
import requests
import random
import json

BASE_URL = "http://localhost:5000"
USERNAME = "vibecoder"
PASSWORD = "password"

def get_session():
    s = requests.Session()
    # Login
    res = s.post(f"{BASE_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
    try:
        data = res.json()
        if not data.get("ok"):
            print(f"Login failed: {data.get('error')}")
            return None
    except Exception:
        print(f"Login failed (non-JSON): {res.text}")
        return None
        
    return s

def populate():
    s = get_session()
    if not s: return

    print(f"Logged in as {USERNAME}. Generating 50 posts...")
    
    types = ['text', 'image', 'link']
    
    # Random content data
    texts = [
        "# Hello World\nJust a test note.",
        "**Bold move**\n> Quote of the day.",
        "```python\nprint('Code block')\n```",
        "Short text.",
        "A very long note that goes on and on to test the height of the card in the masonry layout. It mimics a rant or a blog post.",
        "## Section Header\nList:\n- Item 1\n- Item 2"
    ]
    
    images = [
        "https://picsum.photos/400/300",
        "https://picsum.photos/300/500", # Tall
        "https://picsum.photos/500/300", # Wide
        "https://picsum.photos/400/400"  # Square
    ]
    
    links = [
        {"url": "https://google.com", "title": "Google Search"},
        {"url": "https://github.com", "title": "GitHub"},
        {"url": "https://news.ycombinator.com", "title": "Hacker News"},
        {"url": "https://example.com", "title": "Example Domain"}
    ]

    for i in range(50):
        t = random.choice(types)
        payload = {
            "module_type": t,
            "content": {},
            "display_order": i + 100 # Append
        }
        
        if t == 'text':
            payload["content"]["text"] = f"{random.choice(texts)}\n\n*Item #{i+1}*"
        elif t == 'image':
            # Add random query param to avoid cache and ensure unique images
            payload["content"]["url"] = f"{random.choice(images)}?random={i}"
        elif t == 'link':
            l = random.choice(links)
            payload["content"]["url"] = l["url"]
            payload["content"]["title"] = f"{l['title']} (#{i+1})"

        res = s.post(f"{BASE_URL}/wall/post/add", json=payload)
        if res.status_code == 200:
            print(f"[{i+1}/50] Added {t} post.")
        else:
            print(f"[{i+1}/50] Failed: {res.text}")

if __name__ == "__main__":
    populate()
