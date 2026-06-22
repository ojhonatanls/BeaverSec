"""beaversec.core.transport

Async transport helpers using aiohttp with proxy and Tor support.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

from beaversec.config import get_config

logger = logging.getLogger(__name__)


class TransportFactory:
    """Create and manage aiohttp ClientSession with proxy / Tor integration.

    Usage:
        async with TransportFactory().session() as session:
            await session.get(...)
    """

    def __init__(self, cfg: Optional[Dict[str, Any]] = None) -> None:
        self.cfg = cfg or get_config()
        self._session: Optional[aiohttp.ClientSession] = None

    def _client_kwargs(self) -> Dict[str, Any]:
        kw: Dict[str, Any] = {
            "timeout": aiohttp.ClientTimeout(total=self.cfg.get("http_timeout", 30)),
        }
        proxy_cfg = self.cfg.get("proxy", {})
        if proxy_cfg:
            proxy = proxy_cfg.get("url")
            proxy_auth = None
            if proxy_cfg.get("username") and proxy_cfg.get("password"):
                proxy_auth = aiohttp.BasicAuth(
                    proxy_cfg["username"], proxy_cfg["password"]
                )
            if proxy:
                kw["trust_env"] = False
                kw["connector"] = aiohttp.TCPConnector(ssl=False)
                kw["_proxy"] = proxy  # stored for usage below
                kw["_proxy_auth"] = proxy_auth
        if self.cfg.get("use_tor"):
            # by convention expect Tor SOCKS5 proxy at 127.0.0.1:9050
            tor_addr = self.cfg.get("tor_proxy", "socks5://127.0.0.1:9050")
            kw["trust_env"] = False
            kw["connector"] = aiohttp.TCPConnector(ssl=False)
            kw["_proxy"] = tor_addr
            kw["_proxy_auth"] = None
        return kw

    async def session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp ClientSession honoring proxy settings."""
        if self._session and not self._session.closed:
            return self._session
        kw = self._client_kwargs()
        proxy = kw.pop("_proxy", None)
        proxy_auth = kw.pop("_proxy_auth", None)
        # create session without direct proxy args because we pass proxies per-request
        self._session = aiohttp.ClientSession(**kw)
        # store proxy info for convenience
        self._session.__dict__.setdefault("_beaversec_proxy", proxy)
        self._session.__dict__.setdefault("_beaversec_proxy_auth", proxy_auth)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @staticmethod
    def request_kwargs_for_session(session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Return dict with proxy kwargs for use with session.request."""
        return {
            "proxy": session.__dict__.get("_beaversec_proxy"),
            "proxy_auth": session.__dict__.get("_beaversec_proxy_auth"),
        }
