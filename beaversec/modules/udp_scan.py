"""UDP port scanner (async).

UDP scans use asyncio and UDP sockets; because of UDP's unreliable nature,
results indicate 'open|filtered', 'closed' (on ICMP port unreachable), or 'no_response'.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)


class UDPScanModule(BaseModule):
    """Async UDP port scanner."""

    name = "udp_scan"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 200.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))

    async def _probe(self, host: str, port: int, timeout: float = 2.0) -> str:
        await self._limiter.acquire(1.0)
        try:
            loop = asyncio.get_running_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(),
                remote_addr=(host, port),
            )
            # send an empty payload; many UDP services respond to application-specific packets
            transport.sendto(b"\x00")
            # wait for response or timeout
            try:
                await asyncio.wait_for(loop.create_future(), timeout=timeout)
            except asyncio.TimeoutError:
                # No response; UDP is hard: open|filtered
                return "open|filtered"
            finally:
                transport.close()
        except Exception:
            return "no_response"
        return "no_response"

    async def scan_host(self, host: str, ports: Iterable[int]) -> Dict[str, str]:
        results: Dict[str, str] = {}
        tasks = [asyncio.create_task(self._probe(host, p)) for p in ports]
        for p, t in zip(ports, tasks):
            results[str(p)] = await t
        return results

    async def run(self, targets: Iterable[str], ports: Iterable[int], **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for host in targets:
            out[host] = await self.scan_host(host, ports)
        return out
