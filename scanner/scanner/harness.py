import httpx


class TargetClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(self, query: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/chat",
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()