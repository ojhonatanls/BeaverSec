"""
Consulta WHOIS para domínios.
"""
import logging

import whois

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class WhoisLookup(BaseModule):
    """Consulta WHOIS de domínios."""

    name = "whois_lookup"
    description = "Consulta WHOIS de domínios"

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        try:
            w = whois.whois(target)
            data = {
                "domain_name": w.domain_name,
                "registrar": w.registrar,
                "whois_server": w.whois_server,
                "creation_date": str(w.creation_date) if w.creation_date else None,
                "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                "name_servers": w.name_servers,
                "status": w.status,
                "emails": w.emails,
                "dnssec": w.dnssec,
            }
            return ModuleResult(
                module=self.name,
                target=target,
                success=True,
                data=data,
            )
        except Exception as e:
            return ModuleResult(
                module=self.name,
                target=target,
                success=False,
                errors=[str(e)],
            )
