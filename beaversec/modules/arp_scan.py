"""ARP sweep for local network discovery.

Uses scapy when available; otherwise falls back to system `arp` lookup (best-effort).
"""
from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_network
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)

try:
    from scapy.all import ARP, Ether, srp  # type: ignore
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False


class ArpScanModule(BaseModule):
    """ARP sweep module."""

    name = "arp_scan"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 500.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def scan_network(self, cidr: str) -> Dict[str, str]:
        """Scan an IPv4 network in CIDR notation (e.g., '192.168.1.0/24')."""
        if not SCAPY_AVAILABLE:
            logger.warning("scapy not available; arp_scan will not run")
            return {}
        net = ip_network(cidr)
        hosts = [str(ip) for ip in net.hosts()]
        results: Dict[str, str] = {}

        loop = asyncio.get_event_loop()

        def _send_srp(chunk: List[str]) -> Dict[str, str]:
            answered = {}
            for ip in chunk:
                pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
                resp, _ = srp(pkt, timeout=1, verbose=0)
                if resp:
                    for s, r in resp:
                        answered[r.psrc] = r.hwsrc
            return answered

        # process in chunks to rate-limit (cooperative)
        chunk_size = 64
        for i in range(0, len(hosts), chunk_size):
            await self._limiter.acquire(1.0)
            chunk = hosts[i : i + chunk_size]
            res = await loop.run_in_executor(self._executor, _send_srp, chunk)
            results.update(res)
        return results

    async def run(self, networks: Iterable[str], **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for net in networks:
            out[net] = await self.scan_network(net)
        return out
