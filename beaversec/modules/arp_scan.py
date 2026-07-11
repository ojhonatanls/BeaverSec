"""ARP scan module for local network discovery."""

import subprocess
import re
from typing import Dict, Any, List
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class ArpScanModule(BaseModule):
    name = "arp_scan"
    description = "ARP scan for local network host discovery"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        # Use arp-scan if available, else fallback to ping sweep
        try:
            result = subprocess.run(
                ["arp-scan", target],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse output (simplified)
                hosts = []
                for line in result.stdout.splitlines():
                    if ":" in line and "(" in line:  # likely a MAC and IP
                        parts = line.split()
                        if len(parts) >= 2:
                            hosts.append({"ip": parts[0], "mac": parts[1]})
                return ModuleResult(success=True, data={"hosts": hosts})
            else:
                # Fallback to ping sweep (if no arp-scan)
                return ModuleResult(success=False, error="arp-scan not available")
        except FileNotFoundError:
            return ModuleResult(success=False, error="arp-scan command not found")
        except Exception as e:
            return ModuleResult(success=False, error=str(e))