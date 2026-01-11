import requests

# We need a session to hold the CSRF secret and logged in status
session = requests.Session()

# 1. Login to get session
res = session.post('http://localhost:5000/auth/login', json={'username': 'gijsja', 'password': ' '})
print(f"Login status: {res.status_code}")

# 2. Get CSRF token from a page (e.g. homepage)
res = session.get('http://localhost:5000/')
from html.parser import HTMLParser
class CSRFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None
    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and dict(attrs).get('name') == 'csrf-token':
            self.token = dict(attrs).get('content')

parser = CSRFParser()
parser.feed(res.text)
csrf_token = parser.token
print(f"CSRF Token: {csrf_token}")

# 3. Call /cats/speak
res = session.post('http://localhost:5000/cats/speak', 
                   headers={'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'},
                   json={'event': 'test_event'})
print(f"Speak status: {res.status_code}")
print(f"Speak response: {res.text}")
