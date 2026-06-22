"""HTTP headers scanner with CSP evaluation and security scoring.

Uses aiohttp via TransportFactory. Produces a simple security score based on
presence/absence of recommended headers.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.transport import TransportFactory
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)


RECOMMENDED_HEADERS = [
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "strict-transport-security",
    "referrer-policy",
]


class HTTPHeadersModule(BaseModule):
    """HTTP header inspection and CSP evaluation."""

    name = "http_headers"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        self._limiter = TokenBucket(rate=float(cfg.get("rate_limit", 50.0)), capacity=float(cfg.get("rate_limit", 50.0)))
        self.transport = TransportFactory(cfg)

    async def fetch(self, url: str) -> Dict[str, Any]:
        await self._limiter.acquire(1.0)
        session = await self.transport.session()
        try:
            kw = TransportFactory.request_kwargs_for_session(session)
            async with session.get(url, **kw) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                body = await resp.text()
                return {"status": resp.status, "headers": headers, "body_snippet": body[:1024]}
        except Exception as exc:
            logger.debug("HTTP fetch failed for %s: %s", url, exc)
            return {"error": str(exc)}

    def _evaluate_csp(self, csp_value: str) -> Dict[str, Any]:
        # Very small CSP heuristic evaluator (presence/unsafe keywords)
        score = 100
        issues = []
        if "unsafe-inline" in csp_value:
            score -= 30
            issues.append("unsafe-inline")
        if "unsafe-eval" in csp_value:
            score -= 30
            issues.append("unsafe-eval")
        if "data:" in csp_value:
            score -= 10
            issues.append("data-scheme")
        return {"csp_score": max(score, 0), "csp_issues": issues}

    async def inspect(self, url: str) -> Dict[str, Any]:
        data = await self.fetch(url)
        headers = data.get("headers", {})
        score = 0
        missing = []
        for h in RECOMMENDED_HEADERS:
            if h in headers:
                score += 20
            else:
                missing.append(h)
        csp_info = {}
        if "content-security-policy" in headers:
            csp_info = self._evaluate_csp(headers["content-security-policy"])
        return {"url": url, "status": data.get("status"), "score": score, "missing": missing, "csp": csp_info, "raw": data}

    async def run(self, targets: Iterable[str], **kwargs: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        tasks = [asyncio.create_task(self.inspect(t)) for t in targets]
        for t, task in zip(targets, tasks):
            out[t] = await task
        return out
