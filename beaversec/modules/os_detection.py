"""OS fingerprinting via TCP/IP stack analysis.

This module implements passive/active TCP fingerprinting heuristics using
basic probes. It is a best-effort implementation and intended to complement
other tools (e.g., nmap-like fingerprinting).
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)


class OSDetectionModule(BaseModule):
    """Basic OS detection module."""

    name = "os_detection"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 50.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))

    async def _tcp_timestamp_probe(self, host: str, port: int = 80) -> Dict[str, Any]:
        """Probe TCP behavior such as TTL and window size for heuristics.

        Returns:
            Dict with observed fields.
        """
        await self._limiter.acquire(1.0)
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.write(b"GET / HTTP/1.0\r\n\r\n")
            await writer.drain()
            data = await asyncio.wait_for(reader.read(256), timeout=2.0)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            # heuristics placeholder: analyze data and remote window/ttl via transport is not trivial here
            return {"banner_snippet": data.decode(errors="ignore")[:200]}
        except Exception as exc:
            logger.debug("tcp probe failed for %s:%s: %s", host, port, exc)
            return {"error": str(exc)}

    async def detect(self, host: str) -> Dict[str, Any]:
        """Run multiple probes and correlate heuristics into OS guess."""
        probes = await self._tcp_timestamp_probe(host)
        # Very simple heuristic: look for Linux/Windows strings in banners
        banner = probes.get("banner_snippet", "").lower()
        if "linux" in banner or "nginx" in banner:
            os_guess = "linux-like"
        elif "windows" in banner or "microsoft" in banner:
            os_guess = "windows"
        else:
            os_guess = "unknown"
        return {"host": host, "os_guess": os_guess, "probes": probes}

    async def run(self, targets: Iterable[str], **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        tasks = [asyncio.create_task(self.detect(t)) for t in targets]
        for t in targets:
            out[t] = await asyncio.gather(*[tasks.pop(0)])  # ensure order
        # flatten results
        return {k: v[0] if isinstance(v, list) and v else v for k, v in out.items()}
