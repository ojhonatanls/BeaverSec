"""OS detection module (using TTL and other heuristics) for BeaverSec."""

import subprocess
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class OSDetectionModule(BaseModule):
    name = "os_detection"
    description = "Guess operating system by TTL and other fingerprints"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        try:
            result = subprocess.run(
                ["ping", "-c", "1", target],
                capture_output=True,
                text=True,
                timeout=3
            )
            # Parse TTL from output (simplified)
            import re
            ttl_match = re.search(r'ttl=(\d+)', result.stdout, re.I)
            if ttl_match:
                ttl = int(ttl_match.group(1))
                if ttl <= 64:
                    os_guess = "Linux/Unix"
                elif ttl <= 128:
                    os_guess = "Windows"
                else:
                    os_guess = "Unknown"
                return ModuleResult(success=True, data={"ttl": ttl, "os_guess": os_guess})
            else:
                return ModuleResult(success=False, error="TTL not found")
        except Exception as e:
            return ModuleResult(success=False, error=str(e))