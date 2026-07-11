"""Subdomain brute-force module for BeaverSec."""

import dns.resolver
from typing import Dict, Any, List
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class SubdomainBruteModule(BaseModule):
    name = "subdomain_brute"
    description = "Subdomain brute-force using a wordlist"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        # Default wordlist (small sample)
        wordlist = ['www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'test', 'api', 'vpn', 'ns1']
        found = []
        for sub in wordlist:
            domain = f"{sub}.{target}"
            try:
                dns.resolver.resolve(domain, 'A')
                found.append(domain)
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                continue
            except Exception:
                continue
        return ModuleResult(success=True, data={"subdomains": found})