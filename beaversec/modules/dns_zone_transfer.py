"""DNS zone transfer module for BeaverSec."""

import dns.query
import dns.zone
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class DNSZoneTransferModule(BaseModule):
    name = "dns_zone_transfer"
    description = "Attempt DNS zone transfer (AXFR)"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        # Try to find NS servers first
        try:
            import dns.resolver
            ns_answers = dns.resolver.resolve(target, 'NS')
            ns_servers = [str(r) for r in ns_answers]
        except Exception:
            ns_servers = [target]  # fallback

        for ns in ns_servers:
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns, target))
                if zone:
                    records = {name.to_text(): [rdata.to_text() for rdata in rdset]
                               for name, rdset in zone.items()}
                    return ModuleResult(success=True, data={"server": ns, "records": records})
            except Exception:
                continue

        return ModuleResult(success=False, error="Zone transfer failed on all NS servers")