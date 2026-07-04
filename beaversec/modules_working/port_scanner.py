"""Port scanning module for BeaverSec."""

import socket
from typing import Dict, Any


class Module:
    """Simple TCP port scanner."""

    name = "port_scanner"
    description = "Simple TCP port scanner"

    def __init__(self):
        self.options = {
            "target": {"required": True, "description": "Target IP or hostname"},
            "port": {"required": True, "description": "Port to scan"},
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        """Run the port scan."""
        target = kwargs.get("target")
        port = int(kwargs.get("port", 80))

        result = {
            "target": target,
            "port": port,
            "open": False,
            "service": None,
        }

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            conn = sock.connect_ex((target, port))
            if conn == 0:
                result["open"] = True
                try:
                    result["service"] = socket.getservbyport(port)
                except:
                    result["service"] = "unknown"
            sock.close()
        except Exception as e:
            result["error"] = str(e)

        return result
