"""Ping sweep module for BeaverSec."""

import subprocess
import re
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class PingSweepModule(BaseModule):
    name = "ping_sweep"
    description = "ICMP ping sweep for host discovery"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        # Use ping command (Linux)
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", target],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return ModuleResult(success=True, data={"alive": True, "output": result.stdout})
            else:
                return ModuleResult(success=False, error="Host unreachable", data={"alive": False})
        except subprocess.TimeoutExpired:
            return ModuleResult(success=False, error="Ping timeout")
        except Exception as e:
            return ModuleResult(success=False, error=str(e))