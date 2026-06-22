"""Basic CVE scanner using NVD API.

This module queries the NVD API for CVEs related to discovered service banners.
It expects an NVD API key under config.yaml -> nvd -> api_key (optional).
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


class VulnScannerModule(BaseModule):
    """Basic vulnerability scanner using NVD."""

    name = "vuln_scanner"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self._nvd_key = cfg.get("nvd", {}).get("api_key")
        rate = cfg.get("rate_limit", 5.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))
        self.transport = TransportFactory(cfg)

    async def query_nvd(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query NVD API for `query` string. Returns list of CVE hits."""
        await self._limiter.acquire(1.0)
        session = await self.transport.session()
        headers = {}
        if self._nvd_key:
            headers["apiKey"] = self._nvd_key
        params = {"keyword": query, "resultsPerPage": str(limit)}
        try:
            kw = TransportFactory.request_kwargs_for_session(session)
            async with session.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params=params, headers=headers, **kw) as resp:
                if resp.status != 200:
                    logger.debug("NVD query failed: %s", resp.status)
                    return []
                data = await resp.json()
                return data.get("vulnerabilities", [])[:limit]
        except Exception as exc:
            logger.exception("NVD query error: %s", exc)
            return []

    async def run(self, targets: Iterable[str], banners: Dict[str, List[str]] | None = None, **kwargs: Any) -> Dict[str, Any]:
        """Run vuln scans for service banners per target.

        Args:
            targets: hosts to enrich.
            banners: optional mapping host->list of banner strings to query.
        """
        out: Dict[str, Any] = {}
        for host in targets:
            queries = banners.get(host, []) if banners else []
            results = {}
            for q in queries:
                hits = await self.query_nvd(q)
                results[q] = hits
            out[host] = results
        return out
