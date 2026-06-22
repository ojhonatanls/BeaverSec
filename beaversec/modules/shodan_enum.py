"""Shodan enrichment module.

Uses the shodan library when available; otherwise performs a direct
HTTP request to Shodan REST API.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List, Optional

import aiohttp

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.transport import TransportFactory
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)

try:
    import shodan  # type: ignore
    SHODAN_PY = True
except Exception:
    SHODAN_PY = False


class ShodanEnumModule(BaseModule):
    """Shodan-based IP enrichment."""

    name = "shodan_enum"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self.api_key = cfg.get("shodan", {}).get("api_key")
        rate = cfg.get("rate_limit", 1.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))
        self.transport = TransportFactory(cfg)

    async def query_shodan(self, ip: str) -> Dict[str, Any]:
        await self._limiter.acquire(1.0)
        if SHODAN_PY and self.api_key:
            client = shodan.Shodan(self.api_key)
            try:
                return client.host(ip)
            except Exception as exc:
                logger.debug("shodan client error: %s", exc)
                return {"error": str(exc)}
        # fallback to HTTP
        session = await self.transport.session()
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Key"] = self.api_key
        try:
            kw = TransportFactory.request_kwargs_for_session(session)
            async with session.get(f"https://api.shodan.io/shodan/host/{ip}", headers=headers, params={"key": self.api_key}, **kw) as resp:
                if resp.status != 200:
                    return {"error": f"status {resp.status}"}
                return await resp.json()
        except Exception as exc:
            logger.exception("Shodan query failed: %s", exc)
            return {"error": str(exc)}

    async def run(self, targets: Iterable[str], **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        tasks = [asyncio.create_task(self.query_shodan(t)) for t in targets]
        for t, task in zip(targets, tasks):
            out[t] = await task
        return out
