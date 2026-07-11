"""WHOIS lookup module for BeaverSec."""

import whois
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class WhoisLookup(BaseModule):
    name = "whois_lookup"
    description = "WHOIS domain information"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        try:
            w = whois.whois(target)
            return ModuleResult(success=True, data=w.__dict__)
        except Exception as e:
            return ModuleResult(success=False, error=str(e))