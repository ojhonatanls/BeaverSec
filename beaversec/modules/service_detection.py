"""Service version detection via banner grabbing and simple probing.

Connects to common ports and attempts to read service banners or perform protocol
handshakes to identify service and version strings.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List, Tuple

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)

COMMON_PORTS: List[int] = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5900]


class ServiceDetectionModule(BaseModule):
    """Service version detection module."""

    name = "service_detection"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 200.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))

    async def probe_port(self, host: str, port: int, timeout: float = 2.0) -> Tuple[int, str]:
        await self._limiter.acquire(1.0)
        try:
            reader, writer = await asyncio.open_connection(host, port)
            # Send protocol-specific probe for HTTP/HTTPS
            if port == 80:
                writer.write(b"GET / HTTP/1.0\r\nHost: %b\r\n\r\n" % host.encode())
            elif port == 443:
                # TLS handshake would be required — skip here and report that TLS exists
                writer.write(b"\r\n")
            else:
                writer.write(b"\r\n")
            await writer.drain()
            data = await asyncio.wait_for(reader.read(512), timeout=timeout)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            banner = data.decode(errors="ignore").strip()[:512]
            return port, banner or "no_banner"
        except Exception as exc:
            logger.debug("probe_port %s:%d failed: %s", host, port, exc)
            return port, f"error: {exc}"

    async def detect(self, host: str, ports: Iterable[int] | None = None) -> Dict[str, str]:
        ports = list(ports or COMMON_PORTS)
        tasks = [asyncio.create_task(self.probe_port(host, p)) for p in ports]
        results: Dict[str, str] = {}
        for t in tasks:
            port, banner = await t
            results[str(port)] = banner
        return results

    async def run(self, targets: Iterable[str], ports: Iterable[int] | None = None, **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for host in targets:
            out[host] = await self.detect(host, ports)
        return out
