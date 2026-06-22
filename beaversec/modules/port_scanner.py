"""
Módulo de escaneamento de portas TCP.
"""
import logging
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_address

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class PortScanner(BaseModule):
    """Escaneamento de portas TCP com threading."""

    name = "port_scanner"
    description = "Escaneamento de portas TCP"

    def _scan_port(self, ip: str, port: int, timeout: float) -> int | None:
        """Tenta conectar a uma porta."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return port if result == 0 else None
        except Exception:
            return None

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        try:
            ip_address(target)  # valida
        except ValueError as e:
            return ModuleResult(
                module=self.name,
                target=target,
                success=False,
                errors=[f"Alvo inválido: {e}"],
            )

        # Lista de portas comuns (1-1024 + algumas conhecidas)
        ports = list(range(1, 1025)) + [3306, 5432, 27017, 6379, 9200, 9300]
        open_ports = []

        logger.info(f"Escaneando {len(ports)} portas em {target}")

        with ThreadPoolExecutor(max_workers=validated.threads) as executor:
            futures = {
                executor.submit(self._scan_port, target, p, validated.timeout): p
                for p in ports
            }
            for future in as_completed(futures):
                port = futures[future]
                try:
                    res = future.result()
                    if res:
                        open_ports.append(res)
                        logger.debug(f"Porta aberta: {res}")
                except Exception as e:
                    logger.warning(f"Erro na porta {port}: {e}")

        return ModuleResult(
            module=self.name,
            target=target,
            success=True,
            data={"open_ports": sorted(open_ports), "count": len(open_ports)},
        )
