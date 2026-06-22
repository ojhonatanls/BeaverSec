"""
Módulo de varredura ICMP (ping sweep).
"""
import logging
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_address, ip_network

from icmplib import ping

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class PingSweep(BaseModule):
    """Varredura de hosts ativos via ICMP."""

    name = "ping_sweep"
    description = "Varredura ICMP para hosts ativos"

    def _ping_host(self, ip: str, timeout: float) -> bool:
        """Tenta pingar um host. Fallback para subprocess se icmplib falhar."""
        try:
            # Tenta usar icmplib (mais rápido, mas precisa de permissões)
            result = ping(ip, count=1, timeout=timeout, privileged=False)
            return result.is_alive
        except Exception as e:
            logger.debug(f"icmplib falhou para {ip}: {e}, usando fallback")
            # Fallback com subprocess sanitizado
            cmd = ["ping", "-c", "1", "-W", str(int(timeout)), ip]
            try:
                subprocess.run(cmd, check=False, capture_output=True, timeout=timeout + 1)
                return True
            except Exception:
                return False

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)
        hosts = []

        try:
            # Suporta CIDR ou IP único
            if "/" in target:
                network = ip_network(target, strict=False)
                ip_list = [str(ip) for ip in network.hosts()]
            else:
                # Valida IP único
                ip_address(target)
                ip_list = [target]
        except ValueError as e:
            return ModuleResult(
                module=self.name,
                target=target,
                success=False,
                errors=[f"Alvo inválido: {e}"],
            )

        active = []
        total = len(ip_list)
        logger.info(f"Varrendo {total} hosts com {validated.threads} threads")

        with ThreadPoolExecutor(max_workers=validated.threads) as executor:
            futures = {
                executor.submit(self._ping_host, ip, validated.timeout): ip
                for ip in ip_list
            }
            for future in as_completed(futures):
                ip = futures[future]
                try:
                    if future.result():
                        active.append(ip)
                        logger.debug(f"Host ativo: {ip}")
                except Exception as e:
                    logger.warning(f"Erro ao pingar {ip}: {e}")

        return ModuleResult(
            module=self.name,
            target=target,
            success=True,
            data={"total": total, "active": active, "active_count": len(active)},
        )
