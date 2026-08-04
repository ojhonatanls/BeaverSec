"""Port scanner module for BeaverSec with threaded scanning."""

import socket
from typing import Dict, Any, List, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator
from beaversec.utils.retry import with_retry

def _scan_port(target: str, port: int, timeout: float = 2.0) -> bool:
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        res = sock.connect_ex((target, port))
        return res == 0
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass

@with_retry(attempts=3, backoff=2)
class PortScannerModule(BaseModule):
    name = "port_scanner"
    description = "TCP port scanner (threaded)"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and ("ports" in params or "port" in params)

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        # Accept list of ports or single port
        ports = params.get("ports", params.get("port"))
        if ports is None:
            return ModuleResult(success=False, error="No ports provided")
        if isinstance(ports, int):
            ports = [ports]
        if isinstance(ports, str):
            ports = [int(p.strip()) for p in ports.split(",") if p.strip()]

        # Validate ports and reject 0
        validated_ports: List[int] = []
        try:
            for p in ports:
                p_int = SecurityValidator.validate_port(p)
                if p_int == 0:
                    raise ValueError("Port 0 is invalid")
                validated_ports.append(p_int)
        except ValueError as e:
            return ModuleResult(success=False, error=str(e))

        threads = int(params.get("threads", 50))
        results: Dict[int, bool] = {}
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_port = {executor.submit(_scan_port, target, p): p for p in validated_ports}
            for fut in as_completed(future_to_port):
                p = future_to_port[fut]
                try:
                    open_ = fut.result()
                except Exception:
                    open_ = False
                results[p] = open_

        return ModuleResult(success=True, data={"ports": results})
