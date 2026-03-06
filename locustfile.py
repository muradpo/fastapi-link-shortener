from locust import HttpUser, task, between
import uuid


class LinkShortenerUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://127.0.0.1:8000"

    @task
    def create_link(self):
        alias = f"load-{uuid.uuid4().hex[:8]}"

        self.client.post(
            "/links/shorten",
            json={
                "original_url": "https://google.com",
                "custom_alias": alias
            }
        )