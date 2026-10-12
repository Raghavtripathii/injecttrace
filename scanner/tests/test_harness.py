import httpx
import pytest

from scanner.harness import TargetClient


def make_response(status, body=None, headers=None):
    request = httpx.Request("POST", "http://target/chat")
    return httpx.Response(status, json=body or {}, headers=headers or {}, request=request)


def test_retries_after_rate_limit(monkeypatch):
    responses = [
        make_response(429, headers={"Retry-After": "2"}),
        make_response(200, {"answer": "ok"}),
    ]
    sleeps = []
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: responses.pop(0))
    monkeypatch.setattr("scanner.harness.time.sleep", sleeps.append)

    result = TargetClient("http://target").chat("hello")

    assert result == {"answer": "ok"}
    assert sleeps == [3.0]


def test_gives_up_after_max_retries(monkeypatch):
    monkeypatch.setattr(
        httpx, "post", lambda *args, **kwargs: make_response(429, headers={"Retry-After": "1"})
    )
    monkeypatch.setattr("scanner.harness.time.sleep", lambda seconds: None)

    with pytest.raises(httpx.HTTPStatusError):
        TargetClient("http://target", max_retries=2).chat("hello")


def test_other_server_errors_are_not_retried(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(1)
        return make_response(500)

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr("scanner.harness.time.sleep", lambda seconds: None)

    with pytest.raises(httpx.HTTPStatusError):
        TargetClient("http://target").chat("hello")

    assert len(calls) == 1


def test_paces_consecutive_calls(monkeypatch):
    sleeps = []
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: make_response(200, {"answer": "ok"}))
    monkeypatch.setattr("scanner.harness.time.sleep", sleeps.append)

    client = TargetClient("http://target", delay=10)
    client.chat("first")
    client.chat("second")

    assert len(sleeps) == 1
    assert 9 < sleeps[0] <= 10