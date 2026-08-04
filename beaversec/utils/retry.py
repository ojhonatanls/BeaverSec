"""Retry decorator with exponential backoff."""

import time
import functools
from typing import Callable, Any


def with_retry(attempts: int = 3, backoff: float = 2.0):
    def decorator(obj):
        # Support decorating classes (apply to execute) and functions
        if isinstance(obj, type):
            # Decorate the execute method if present
            exec_fn = getattr(obj, "execute", None)
            if exec_fn and callable(exec_fn):
                @functools.wraps(exec_fn)
                def wrapped_execute(self, *args, **kwargs):
                    last_exc = None
                    for attempt in range(1, attempts + 1):
                        try:
                            return exec_fn(self, *args, **kwargs)
                        except Exception as e:
                            last_exc = e
                            if attempt < attempts:
                                time.sleep(backoff * (2 ** (attempt - 1)))
                            else:
                                raise
                setattr(obj, "execute", wrapped_execute)
            return obj
        else:
            @functools.wraps(obj)
            def wrapped(*args, **kwargs):
                last_exc = None
                for attempt in range(1, attempts + 1):
                    try:
                        return obj(*args, **kwargs)
                    except Exception as e:
                        last_exc = e
                        if attempt < attempts:
                            time.sleep(backoff * (2 ** (attempt - 1)))
                        else:
                            raise
            return wrapped
    return decorator
