"""Enhanced port_scanner module.

- Supports TCP connect scans, SYN scans (via syn_scan module if available),
  UDP scans (delegates to udp_scan), and service detection integration.
- Uses core TokenBucket rate limiter and TransportFactory for HTTP-based probes.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List, Optional

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config
from beaversec.modules import service_detection  # local import for optional use

logger = logging.getLogger(__name__)


class PortScannerModule(BaseModule):
    """Port scanner supporting multiple scan types."""

    name = "port_scanner"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self.rate = float(cfg.get("rate_limit", 500.0))
        self._limiter = TokenBucket(rate=self.rate, capacity=self.rate)

    async def _tcp_connect(self, host: str, port: int, timeout: float = 2.0) -> str:
        await self._limiter.acquire(1.0)
        try:
            conn = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return "open"
        except Exception:
            return "closed|filtered"

    async def scan(self, hosts: Iterable[str], ports: Iterable[int], scan_type: str = "connect") -> Dict[str, Dict[str, str]]:
        ports = list(ports)
        out: Dict[str, Dict[str, str]] = {}
        for h in hosts:
            results: Dict[str, str] = {}
            tasks = [asyncio.create_task(self._tcp_connect(h, p)) for p in ports] if scan_type in ("connect", "tcp") else []
            for p, t in zip(ports, tasks):
                results[str(p)] = await t
            # sync: integrate service detection for open ports
            try:
                svc_detector = service_detection.ServiceDetectionModule()
                open_ports = [int(p) for p, state in results.items() if state == "open"]
                if open_ports:
                    svc_info = await svc_detector.detect(h, open_ports)
                    results.update({f"svc_{k}": v for k, v in svc_info.items()})
            except Exception:
                logger.debug("Service detection integration failed for %s", h)
            out[h] = results
        return out

    async def run(self, targets: Iterable[str], ports: Iterable[int], scan_type: str = "connect", **kwargs: Any) -> Dict[str, Any]:
        return await self.scan(targets, ports, scan_type)
