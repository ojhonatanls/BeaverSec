"""
Enumeração de registros DNS.
"""
import logging

import dns.resolver

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class DNSEnum(BaseModule):
    """Enumera registros DNS de um domínio."""

    name = "dns_enum"
    description = "Enumeração de registros DNS"

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]
        results = {}

        resolver = dns.resolver.Resolver()
        resolver.timeout = validated.timeout
        resolver.lifetime = validated.timeout

        for rtype in record_types:
            try:
                answers = resolver.resolve(target, rtype)
                results[rtype] = [str(r) for r in answers]
                logger.debug(f"{rtype}: {len(answers)} registros")
            except dns.resolver.NoAnswer:
                results[rtype] = []
            except dns.resolver.NXDOMAIN:
                return ModuleResult(
                    module=self.name,
                    target=target,
                    success=False,
                    errors=[f"Domínio {target} não existe"],
                )
            except Exception as e:
                logger.warning(f"Erro ao buscar {rtype}: {e}")
                results[rtype] = []

        return ModuleResult(
            module=self.name,
            target=target,
            success=True,
            data=results,
        )
