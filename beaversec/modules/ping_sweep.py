"""Enhanced ping_sweep with ICMP and ARP methods and async support.

Falls back to system ping when raw sockets/scapy not available.
"""
from __future__ import annotations

import asyncio
import logging
import platform
from ipaddress import ip_network
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config
from beaversec.modules import arp_scan

logger = logging.getLogger(__name__)


class PingSweepModule(BaseModule):
    """Ping sweep using ICMP or ARP (local networks)."""

    name = "ping_sweep"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self.rate = float(cfg.get("rate_limit", 500.0))
        self.method = cfg.get("ping_method", "icmp")  # icmp or arp
        self._limiter = TokenBucket(rate=self.rate, capacity=self.rate)

    async def _system_ping(self, ip: str, timeout: float = 1.0) -> bool:
        """Fallback to system ping command (platform-dependent)."""
        await self._limiter.acquire(1.0)
        cmd = ["ping", "-c", "1", "-W", str(int(timeout)), ip] if platform.system().lower() != "windows" else ["ping", "-n", "1", ip]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        rc = await proc.wait()
        return rc == 0

    async def sweep(self, cidr: str, method: str | None = None) -> Dict[str, bool]:
        method = method or self.method
        if method == "arp":
            # delegate to arp_scan module if available
            try:
                arp = arp_scan.ArpScanModule()
                res = await arp.scan_network(cidr)
                # convert hwsrc presence to bool
                return {k: True for k in res.keys()}
            except Exception:
                logger.debug("ARP scan delegation failed; falling back to ICMP")
                method = "icmp"
        net = ip_network(cidr)
        hosts = [str(h) for h in net.hosts()]
        out: Dict[str, bool] = {}
        tasks = [asyncio.create_task(self._system_ping(h)) for h in hosts]
        for h, t in zip(hosts, tasks):
            out[h] = await t
        return out

    async def run(self, networks: Iterable[str], method: str | None = None, **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for n in networks:
            out[n] = await self.sweep(n, method)
        return out
