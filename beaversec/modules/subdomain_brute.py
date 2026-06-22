"""Subdomain bruteforcer with optional SecurityTrails integration.

Reads SecurityTrails API key from config (securitytrails -> api_key).
Uses async transport helper for HTTP requests and respects rate_limit.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.transport import TransportFactory
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)


class SubdomainBruteModule(BaseModule):
    """Subdomain brute force with optional SecurityTrails enrichment."""

    name = "subdomain_brute"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self._st_key = cfg.get("securitytrails", {}).get("api_key")
        self._limiter = TokenBucket(rate=float(cfg.get("rate_limit", 100.0)), capacity=float(cfg.get("rate_limit", 100.0)))
        self.transport = TransportFactory(cfg)

    async def query_securitytrails(self, domain: str) -> Dict[str, Any]:
        """Query SecurityTrails for known subdomains (fallback to HTTP call)."""
        await self._limiter.acquire(1.0)
        session = await self.transport.session()
        headers = {"Accept": "application/json"}
        if self._st_key:
            headers["APIKEY"] = self._st_key
        try:
            kw = TransportFactory.request_kwargs_for_session(session)
            url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
            async with session.get(url, headers=headers, **kw) as resp:
                if resp.status != 200:
                    return {}
                data = await resp.json()
                # SecurityTrails returns list under 'subdomains'
                return {"subdomains": data.get("subdomains", [])}
        except Exception:
            logger.debug("SecurityTrails query failed for %s", domain)
            return {}

    async def brute(self, domain: str, wordlist: Iterable[str]) -> List[str]:
        await self._limiter.acquire(1.0)
        found: List[str] = []
        tasks = []
        for w in wordlist:
            fqdn = f"{w}.{domain}"
            tasks.append(asyncio.create_task(self._resolve(fqdn)))
        for t in tasks:
            ok, fqdn = await t
            if ok:
                found.append(fqdn)
        return found

    async def _resolve(self, fqdn: str) -> tuple[bool, str]:
        await self._limiter.acquire(1.0)
        try:
            # lightweight resolution using asyncio
            await asyncio.get_event_loop().getaddrinfo(fqdn, None)
            return True, fqdn
        except Exception:
            return False, fqdn

    async def run(self, domains: Iterable[str], wordlist: Iterable[str] | None = None, enrich: bool = True, **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for d in domains:
            results = {"found": []}
            # brute
            if wordlist:
                results["found"] = await self.brute(d, wordlist)
            if enrich and self._st_key:
                st = await self.query_securitytrails(d)
                results["securitytrails"] = st
            out[d] = results
        return out
