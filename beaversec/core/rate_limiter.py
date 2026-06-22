"""beaversec.core.rate_limiter

Async token-bucket rate limiter used across modules.
"""
from __future__ import annotations

import asyncio
import time
from typing import Optional


class TokenBucket:
    """Simple async token-bucket rate limiter.

    Attributes:
        rate: tokens added per second.
        capacity: maximum tokens in bucket.
    """

    def __init__(self, rate: float, capacity: Optional[float] = None) -> None:
        self.rate = float(rate)
        self.capacity = capacity if capacity is not None else self.rate
        self._tokens = float(self.capacity)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        """Wait until at least `tokens` are available then consume them.

        Args:
            tokens: Tokens required (default 1.0).
        """
        if tokens <= 0:
            return
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now
                self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                # compute sleep time until tokens available
                needed = tokens - self._tokens
                sleep_time = needed / self.rate if self.rate > 0 else 0.1
                await asyncio.sleep(sleep_time)

    def try_acquire_now(self, tokens: float = 1.0) -> bool:
        """Attempt a non-blocking acquire. Returns True if success."""
        now = time.monotonic()
        elapsed = now - self._last
        self._last = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False
