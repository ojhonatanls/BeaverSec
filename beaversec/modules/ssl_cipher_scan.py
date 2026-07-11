"""SSL cipher suite scanning module for BeaverSec."""

import socket
import ssl
from typing import Dict, Any, List
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class SSLCipherScanModule(BaseModule):
    name = "ssl_cipher_scan"
    description = "Enumerate supported SSL/TLS cipher suites"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and "port" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = SecurityValidator.validate_port(params.get("port", 443))

        # Common cipher suites to test (simplified)
        ciphers = [
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA256',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES128-GCM-SHA256',
            'ECDHE-RSA-AES256-SHA384',
            'ECDHE-RSA-AES128-SHA256',
            'ECDHE-RSA-AES256-SHA',
            'ECDHE-RSA-AES128-SHA',
        ]
        supported = []
        for cipher in ciphers:
            try:
                context = ssl.create_default_context()
                context.set_ciphers(cipher)
                with socket.create_connection((target, port), timeout=3) as sock:
                    with context.wrap_socket(sock, server_hostname=target) as ssock:
                        supported.append(cipher)
            except Exception:
                continue

        return ModuleResult(success=True, data={"supported_ciphers": supported})