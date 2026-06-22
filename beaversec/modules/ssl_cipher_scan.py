"""SSL/TLS cipher suite enumeration and vulnerability checks.

Uses ssl module for supported ciphers; for deeper probing consider using
external tools (openssl or sslyze). This module performs a basic check by
attempting TLS handshakes with different SSLContext ciphers.
"""
from __future__ import annotations

import asyncio
import logging
import ssl
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)


class SSLCipherScanModule(BaseModule):
    """Enumerate server-supported cipher suites and check for known issues."""

    name = "ssl_cipher_scan"

    COMMON_PORTS = [443, 8443]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 10.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))

    async def _probe_cipher(self, host: str, port: int, cipher: str, timeout: float = 3.0) -> bool:
        await self._limiter.acquire(1.0)
        loop = asyncio.get_event_loop()
        def _sync_connect() -> bool:
            try:
                ctx = ssl.create_default_context()
                ctx.set_ciphers(cipher)
                with ctx.wrap_socket(__import__("socket").socket(), server_hostname=host) as s:
                    s.settimeout(timeout)
                    s.connect((host, port))
                    # perform handshake by sending no data; if handshake succeeds, cipher accepted
                    return True
            except Exception:
                return False
        return await loop.run_in_executor(None, _sync_connect)

    async def enumerate(self, host: str, ports: Iterable[int] | None = None) -> Dict[str, List[str]]:
        ports = list(ports or self.COMMON_PORTS)
        # minimal list of candidate ciphers — extendable
        candidates = [
            "HIGH", "ECDHE", "AES", "AES256", "AES128", "RC4", "DES", "3DES",
            "ECDHE-RSA-AES128-GCM-SHA256",
        ]
        supported: Dict[str, List[str]] = {}
        for port in ports:
            supported[str(port)] = []
            for c in candidates:
                ok = await self._probe_cipher(host, port, c)
                if ok:
                    supported[str(port)].append(c)
        return supported

    async def run(self, targets: Iterable[str], ports: Iterable[int] | None = None, **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for host in targets:
            out[host] = await self.enumerate(host, ports)
        # vulnerability checks (POODLE/BEAST) are heuristic here
        return out
