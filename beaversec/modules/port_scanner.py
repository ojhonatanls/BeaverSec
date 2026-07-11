"""Port scanner module for BeaverSec."""

import socket
from typing import Dict, Any, List
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class PortScannerModule(BaseModule):
    name = "port_scanner"
    description = "TCP port scanner"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and "port" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = SecurityValidator.validate_port(params.get("port", 0))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target, port))
            sock.close()
            if result == 0:
                return ModuleResult(success=True, data={"port": port, "open": True})
            else:
                return ModuleResult(success=True, data={"port": port, "open": False})
        except Exception as e:
            return ModuleResult(success=False, error=str(e))