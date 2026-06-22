"""
beaversec/modules/ping_sweep.py

Refactored to use BaseModule and provide a compatibility run() function.
"""
from __future__ import annotations

import platform
import re
import subprocess
import logging
from typing import Any, Dict, Optional

from beaversec.core.base_module import BaseModule, ModuleExecutionError


class PingSweep(BaseModule):
    """Ping sweep module that uses the BaseModule interface."""

    __module_name__ = "ping_sweep"

    def validate_target(self, target: str) -> None:
        if not target:
            raise ValueError("Target não pode ser vazio")
        # For ping we accept IPs, domains, CIDRs; further validation can be added

    def execute(self, target: str, timeout: int = 3, count: int = 1, **kwargs) -> Dict[str, Optional[Any]]:
        system = platform.system()
        if system == "Windows":
            # -n count, -w timeout in milliseconds
            cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), target]
        else:
            # Unix-like: -c count, -W timeout (seconds) on many distros
            cmd = ["ping", "-c", str(count), "-W", str(timeout), target]

        self.log(f"Executando: {' '.join(cmd)}", level=logging.DEBUG)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        except subprocess.TimeoutExpired:
            raise ModuleExecutionError("timeout")
        except Exception as e:
            raise ModuleExecutionError(str(e))

        alive = (result.returncode == 0)
        rtt = None
        if result.stdout:
            match = re.search(r"(?:time[=<]\s*|tempo=)\s*([0-9]+(?:\.[0-9]+)?)", result.stdout)
            if match:
                try:
                    rtt = float(match.group(1))
                except Exception:
                    rtt = None

        return {
            "host": target,
            "alive": alive,
            "rtt": rtt,
            "output": result.stdout.strip() if result.stdout else None,
            "stderr": result.stderr.strip() if result.stderr else None,
        }

    def format_output(self, raw_result: Dict[str, Optional[Any]]) -> Dict[str, Any]:
        return {
            "target": raw_result.get("host"),
            "status": "alive" if raw_result.get("alive") else "down",
            "data": {
                "rtt": raw_result.get("rtt"),
                "raw_output": raw_result.get("output"),
            },
        }


# Compatibility function expected by CLI (module.run)
def run(target: str, **kwargs) -> Dict[str, Any]:
    logger = logging.getLogger("BeaverSec")
    module = PingSweep(verbose=bool(kwargs.get("verbose", False)), logger=logger)
    return module.run(target, **kwargs)
