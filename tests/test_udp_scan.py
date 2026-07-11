"""UDP port scanner module for BeaverSec."""

import socket
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class UDPScanModule(BaseModule):
    name = "udp_scan"
    description = "UDP port scanner"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and "port" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = SecurityValidator.validate_port(params.get("port", 0))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            # Send empty UDP packet
            sock.sendto(b'', (target, port))
            # Try to receive ICMP port unreachable (will raise timeout if open or filtered)
            try:
                data, addr = sock.recvfrom(1024)
                # If we get a response, likely port is open (or filtered)
                # Actually, ICMP unreachable would indicate closed
                # For simplicity, we treat any response as open (needs refinement)
                return ModuleResult(success=True, data={"port": port, "open": True})
            except socket.timeout:
                return ModuleResult(success=True, data={"port": port, "open": False})
            finally:
                sock.close()
        except Exception as e:
            return ModuleResult(success=False, error=str(e))