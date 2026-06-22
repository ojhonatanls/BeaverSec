"""DNS zone transfer (AXFR) tester.

Attempts AXFR against authoritative name servers for a domain.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List

import dns.resolver
import dns.query
import dns.zone

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)


class DNSZoneTransferModule(BaseModule):
    """DNS zone transfer tester."""

    name = "dns_zone_transfer"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 10.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))

    async def attempt_axfr(self, domain: str) -> Dict[str, Any]:
        await self._limiter.acquire(1.0)
        results: Dict[str, Any] = {}
        try:
            answers = dns.resolver.resolve(domain, "NS")
            nameservers = [str(r.target).rstrip(".") for r in answers]
        except Exception as exc:
            logger.debug("Failed to resolve NS for %s: %s", domain, exc)
            return {"error": str(exc)}
        for ns in nameservers:
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns, domain, timeout=5))
                if zone is None:
                    results[ns] = {"axfr": False}
                else:
                    results[ns] = {"axfr": True, "zonesize": len(zone.nodes)}
            except Exception as exc:
                results[ns] = {"axfr": False, "error": str(exc)}
        return results

    async def run(self, domains: Iterable[str], **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for d in domains:
            out[d] = await self.attempt_axfr(d)
        return out
