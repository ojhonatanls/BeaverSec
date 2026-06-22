"""SNMP enumeration with common community strings.

Uses pysnmp if installed; otherwise logs a warning. Attempts read-only GET
for SNMPv2 community strings.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Iterable, List

from beaversec.core.rate_limiter import TokenBucket
from beaversec.core.base import BaseModule
from beaversec.config import get_config

logger = logging.getLogger(__name__)

try:
    from pysnmp.hlapi.asyncio import getCmd, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity  # type: ignore
    PYSNMP_AVAILABLE = True
except Exception:
    PYSNMP_AVAILABLE = False


COMMON_COMMUNITIES = ["public", "private", "community", "default"]


class SNMPEnumModule(BaseModule):
    """SNMP enumeration module."""

    name = "snmp_enum"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cfg = get_config()
        rate = cfg.get("rate_limit", 5.0)
        self._limiter = TokenBucket(rate=float(rate), capacity=float(rate))

    async def probe(self, host: str, community: str, timeout: int = 2) -> Dict[str, Any]:
        await self._limiter.acquire(1.0)
        if not PYSNMP_AVAILABLE:
            logger.warning("pysnmp not available; SNMP enumeration skipped for %s", host)
            return {"error": "pysnmp not installed"}
        try:
            iterator = getCmd(
                CommunityData(community, mpModel=1),
                UdpTransportTarget((host, 161), timeout=timeout, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.1.1.0")),  # sysDescr
            )
            errorIndication, errorStatus, errorIndex, varBinds = await iterator
            if errorIndication:
                return {"error": str(errorIndication)}
            if errorStatus:
                return {"error": f"{errorStatus.prettyPrint()}"}
            # parse varBinds
            return {"sysDescr": str(varBinds[0][1])}
        except Exception as exc:
            logger.debug("SNMP probe failed for %s:%s -> %s", host, community, exc)
            return {"error": str(exc)}

    async def run(self, targets: Iterable[str], communities: Iterable[str] | None = None, **kwargs: Any) -> Dict[str, Any]:
        communities = list(communities or COMMON_COMMUNITIES)
        out: Dict[str, Any] = {}
        for host in targets:
            host_results = {}
            for c in communities:
                host_results[c] = await self.probe(host, c)
            out[host] = host_results
        return out
