"""Shodan enumeration module for BeaverSec."""

import shodan
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class ShodanEnumModule(BaseModule):
    name = "shodan_enum"
    description = "Query Shodan for host information (requires API key)"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        api_key = params.get("shodan_api_key", "")
        if not api_key:
            return ModuleResult(success=False, error="Shodan API key required (set in config)")

        try:
            api = shodan.Shodan(api_key)
            host = api.host(target)
            return ModuleResult(success=True, data=host)
        except shodan.APIError as e:
            return ModuleResult(success=False, error=str(e))