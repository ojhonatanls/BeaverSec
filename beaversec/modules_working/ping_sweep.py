"""Ping sweep module for BeaverSec."""

import subprocess
import platform
from typing import Dict, Any


class Module:
    """Simple ping sweep module."""

    name = "ping_sweep"
    description = "Simple ICMP ping sweep"

    def __init__(self):
        self.options = {
            "target": {"required": True, "description": "Target IP or hostname"},
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        """Run the ping sweep."""
        target = kwargs.get("target")

        result = {
            "target": target,
            "alive": False,
            "output": None,
        }

        try:
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", target]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", target]

            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=2)
            result["alive"] = True
            result["output"] = output.decode('utf-8', errors='ignore').strip()
        except subprocess.CalledProcessError:
            result["alive"] = False
        except Exception as e:
            result["error"] = str(e)

        return result
