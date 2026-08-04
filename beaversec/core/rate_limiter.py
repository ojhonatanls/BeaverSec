"""Rate limiter for BeaverSec modules (sliding window)."""

import time
from collections import deque
from typing import Optional

class RateLimiter:
    """Simple rate limiter using a sliding window."""

    def __init__(self, max_calls: int, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def acquire(self, block: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire a permit to make a call."""
        start = time.time()
        while True:
            now = time.time()
            # Remove calls older than the period
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True

            if not block:
                return False

            # Calculate how long to wait for the oldest call to expire
            sleep_time = self.calls[0] + self.period - now
            if timeout is not None:
                elapsed = now - start
                if elapsed + sleep_time > timeout:
                    return False

            time.sleep(max(0.0, sleep_time))
            # Loop again to re-check availability
