"""
NeoSpace Concurrency Load Test

Run: locust -f locustfile.py --users 50 --spawn-rate 5

Success Metric:
- Old Setup: Write operations spike read latency to >2000ms
- New Setup: Read latency stays <200ms during writes
"""

from locust import HttpUser, task, between


class NeoSpaceUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def view_feed(self):
        """Read operation - should not block during writes."""
        self.client.get("/wall/public")

    @task(1)
    def post_message(self):
        """Write operation - tests SQLite lock behavior."""
        self.client.post("/api/messages", json={"content": "Stress Test!"})
