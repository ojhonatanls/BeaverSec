import time
from beaversec.core.rate_limiter import RateLimiter


def test_non_blocking_acquire(monkeypatch):
    current = {"t": 0.0}

    def fake_time():
        return current["t"]

    def fake_sleep(s):
        current["t"] += s

    monkeypatch.setattr("beaversec.core.rate_limiter.time.time", fake_time)
    monkeypatch.setattr("beaversec.core.rate_limiter.time.sleep", fake_sleep)

    rl = RateLimiter(max_calls=2, period=1.0)
    assert rl.acquire(block=False) is True
    assert rl.acquire(block=False) is True
    # third should be rejected when non-blocking
    assert rl.acquire(block=False) is False


def test_blocking_with_timeout_and_wait(monkeypatch):
    current = {"t": 0.0}

    def fake_time():
        return current["t"]

    def fake_sleep(s):
        current["t"] += s

    monkeypatch.setattr("beaversec.core.rate_limiter.time.time", fake_time)
    monkeypatch.setattr("beaversec.core.rate_limiter.time.sleep", fake_sleep)

    # Case 1: timeout too short -> False
    rl = RateLimiter(max_calls=1, period=5.0)
    assert rl.acquire(block=False) is True
    # next acquire with timeout smaller than wait should return False
    assert rl.acquire(block=True, timeout=2.0) is False

    # Case 2: enough timeout -> waits and returns True
    rl2 = RateLimiter(max_calls=1, period=2.0)
    # acquire first at t=0
    assert rl2.acquire(block=False) is True
    # second with timeout 5 should wait until slot free (2s) and succeed
    assert rl2.acquire(block=True, timeout=5.0) is True
