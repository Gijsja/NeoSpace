from locust import HttpUser, task, between

class NeoSpaceUser(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        """Login before starting tasks."""
        # Note: auth prefix is used in app.py
        # Data must be JSON for msgspec
        self.client.post("/auth/login", json={
            "username": "admin",
            "password": "password"
        })

    @task(3)
    def view_posts(self):
        """Read operation - hits the JSON posts endpoint."""
        # Using a valid profile ID
        self.client.get("/wall/posts/1")

    @task(1)
    def send_chat(self):
        """Write operation - hits the chat send endpoint."""
        # SendMessageRequest: {content: str}
        # Note: /send uses msgspec.json.decode(request.get_data())
        self.client.post("/send", json={
            "content": "Stress Test Message"
        })
