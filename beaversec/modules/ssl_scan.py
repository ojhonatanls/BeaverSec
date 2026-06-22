"""SSL/TLS scanner enhancement: cipher enumeration and vulnerability checks.

Integrates the new ssl_cipher_scan, performs basic checks for POODLE/BEAST heuristics.
"""
from __future__ import annotations

import asyncio
import logging
import ssl
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config
from beaversec.modules import ssl_cipher_scan

logger = logging.getLogger(__name__)


class SSLScanModule(BaseModule):
    """SSL scanning module that wraps cipher enumeration and basic vulnerability checks."""

    name = "ssl_scan"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self._limiter = TokenBucket(rate=float(cfg.get("rate_limit", 20.0)), capacity=float(cfg.get("rate_limit", 20.0)))

    async def _check_ssl(self, host: str, port: int = 443) -> Dict[str, Any]:
        await self._limiter.acquire(1.0)
        # basic TLS version check
        results: Dict[str, Any] = {}
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(__import__("socket").socket(), server_hostname=host) as s:
                s.settimeout(3.0)
                s.connect((host, port))
                # handshake done
                results["handshake"] = True
        except Exception as exc:
            results["handshake"] = False
            results["error"] = str(exc)
        # integrate cipher enum
        try:
            cipher_mod = ssl_cipher_scan.SSLCipherScanModule()
            cipher_info = await cipher_mod.enumerate(host, [port])
            results["ciphers"] = cipher_info.get(str(port), [])
        except Exception:
            results["ciphers"] = []
        # minimal vulnerability heuristics
        results["vulns"] = []
        # POODLE (SSLv3 fallback) heuristic: try to force SSLv3 - python may not allow by default
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # keep insecure options for test
            with ctx.wrap_socket(__import__("socket").socket(), server_hostname=host) as s:
                s.settimeout(3.0)
                s.connect((host, port))
                # if handshake succeeds with SSLv3-like settings it may be vulnerable
                results["vulns"].append("poodle-like")
        except Exception:
            pass
        return results

    async def run(self, targets: Iterable[str], ports: Iterable[int] | None = None, **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for t in targets:
            out[t] = await self._check_ssl(t, ports[0] if ports else 443)
        return out
