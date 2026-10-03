import random
from locust import HttpUser, task, between

class URLShortenerLoadTest(HttpUser):
    wait_time = between(0.01, 0.05)  # High concurrency simulated
    created_codes = []

    def on_start(self):
        """Seed initial short links for the load test."""
        for i in range(3):
            resp = self.client.post("/api/urls", json={
                "url": f"https://example.com/page-{random.randint(1000, 99999)}"
            })
            if resp.status_code == 201:
                self.created_codes.append(resp.json()["short_code"])

    @task(10)
    def test_redirect_cache_hit(self):
        """Simulate high-volume read traffic (10:1 Read-to-Write ratio)."""
        if self.created_codes:
            code = random.choice(self.created_codes)
            self.client.get(f"/{code}", allow_redirects=False, name="/[short_code] (Redirect)")

    @task(1)
    def test_create_short_link(self):
        """Simulate URL shortening writes."""
        resp = self.client.post("/api/urls", json={
            "url": f"https://benchmark.org/test-{random.randint(100000, 999999)}"
        }, name="/api/urls (Create Link)")
        if resp.status_code == 201:
            code = resp.json()["short_code"]
            if len(self.created_codes) < 100:
                self.created_codes.append(code)

    @task(1)
    def test_health_check(self):
        """Probe telemetry and health readiness."""
        self.client.get("/health", name="/health")
