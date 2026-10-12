import time

import httpx

DEFAULT_RETRY_SECONDS = 15.0
MAX_RETRY_SECONDS = 90.0


class TargetClient:
    def __init__(self, base_url: str, timeout: float = 60.0, delay: float = 0.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.delay = delay
        self.max_retries = max_retries
        self._last_call = None

    def _wait_for_turn(self):
        if self.delay and self._last_call is not None:
            elapsed = time.monotonic() - self._last_call
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        self._last_call = time.monotonic()

    def _retry_after(self, response: httpx.Response) -> float:
        try:
            seconds = float(response.headers.get("Retry-After", DEFAULT_RETRY_SECONDS))
        except ValueError:
            seconds = DEFAULT_RETRY_SECONDS
        return min(seconds, MAX_RETRY_SECONDS) + 1

    def chat(self, query: str) -> dict:
        self._wait_for_turn()

        for attempt in range(self.max_retries + 1):
            response = httpx.post(
                f"{self.base_url}/chat",
                json={"query": query},
                timeout=self.timeout,
            )
            if response.status_code == 429 and attempt < self.max_retries:
                time.sleep(self._retry_after(response))
                continue
            response.raise_for_status()
            return response.json()