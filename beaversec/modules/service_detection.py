"""Service detection module for BeaverSec."""

import socket
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class ServiceDetectionModule(BaseModule):
    name = "service_detection"
    description = "Detect service/application on open port"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and "port" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = SecurityValidator.validate_port(params.get("port", 0))

        # Try to connect and read banner
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((target, port))
            sock.send(b'HEAD / HTTP/1.0\r\n\r\n')  # For HTTP
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            return ModuleResult(success=True, data={"banner": banner})
        except Exception as e:
            return ModuleResult(success=False, error=str(e))