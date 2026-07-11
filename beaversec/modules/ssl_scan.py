"""SSL/TLS scan module for BeaverSec."""

import socket
import ssl
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class SSLScanModule(BaseModule):
    name = "ssl_scan"
    description = "SSL/TLS certificate information and cipher suite check"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and "port" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = SecurityValidator.validate_port(params.get("port", 443))

        try:
            context = ssl.create_default_context()
            with socket.create_connection((target, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=target) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    return ModuleResult(success=True, data={
                        "certificate": cert,
                        "cipher": cipher,
                        "version": ssock.version()
                    })
        except Exception as e:
            return ModuleResult(success=False, error=str(e))