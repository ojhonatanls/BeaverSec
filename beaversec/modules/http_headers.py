"""HTTP header grabbing module for BeaverSec."""

import http.client
import socket
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class HTTPHeadersModule(BaseModule):
    name = "http_headers"
    description = "Retrieve HTTP response headers"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = params.get("port", 80)
        try:
            conn = http.client.HTTPConnection(target, port, timeout=5)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            headers = dict(response.getheaders())
            status = response.status
            conn.close()
            return ModuleResult(success=True, data={
                "status": status,
                "headers": headers
            })
        except Exception as e:
            return ModuleResult(success=False, error=str(e))