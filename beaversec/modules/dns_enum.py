"""DNS enumeration module for BeaverSec."""

import dns.resolver
from typing import Dict, Any, List
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class DNSEnum(BaseModule):
    name = "dns_enum"
    description = "DNS record enumeration (A, AAAA, MX, NS, TXT, etc.)"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        results = {}

        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(target, rtype)
                results[rtype] = [str(r) for r in answers]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                results[rtype] = []
            except Exception as e:
                results[rtype] = [f"Error: {e}"]

        return ModuleResult(success=True, data=results)