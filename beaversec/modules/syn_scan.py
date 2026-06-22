"""SYN stealth port scanner module.

This module attempts SYN scans using scapy when available. It is implemented
as an async wrapper: scapy operations run in a ThreadPoolExecutor to avoid
blocking the asyncio loop. Requires root for raw sockets.
"""
from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterable, List, Optional

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.transport import TransportFactory
from beaversec.core.base import BaseModule  # assumes existing base module
from beaversec.config import get_config

logger = logging.getLogger(__name__)

try:
    from scapy.all import IP, TCP, sr1, conf  # type: ignore
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False


class SynScanModule(BaseModule):
    """SYN stealth scanner."""

    name = "syn_scan"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 100.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))
        self._executor = ThreadPoolExecutor(max_workers=10)
        self.transport = TransportFactory(cfg)

    async def scan_host(self, host: str, ports: Iterable[int]) -> Dict[str, str]:
        """Perform SYN scan on `host` for given ports."""
        if not SCAPY_AVAILABLE:
            logger.warning("scapy not available; syn scan will not run for %s", host)
            return {}

        async def _do_scan() -> Dict[str, str]:
            results: Dict[str, str] = {}
            # scapy is blocking; run in executor
            loop = asyncio.get_event_loop()
            for port in ports:
                await self._limiter.acquire(1.0)
                def syn_probe() -> Optional[str]:
                    pkt = IP(dst=host) / TCP(dport=int(port), flags="S")
                    resp = sr1(pkt, timeout=1, verbose=0)
                    if resp is None:
                        return "filtered"
                    if resp.haslayer(TCP):
                        flags = resp.getlayer(TCP).flags
                        # SYN/ACK means open (0x12)
                        if flags & 0x12:
                            return "open"
                        # RST means closed
                        if flags & 0x14:
                            return "closed"
                    return "unknown"
                state = await loop.run_in_executor(self._executor, syn_probe)
                results[str(port)] = state or "unknown"
            return results

        return await _do_scan()

    async def run(self, targets: Iterable[str], ports: Iterable[int], **kwargs: Any) -> Dict[str, Any]:
        """Run SYN scan on targets -> returns mapping host -> port states."""
        out: Dict[str, Any] = {}
        for host in targets:
            logger.debug("Starting syn_scan for %s", host)
            res = await self.scan_host(host, ports)
            out[host] = res
        return out
