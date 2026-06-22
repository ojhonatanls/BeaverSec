"""
Força bruta para descoberta de subdomínios.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.resolver

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class SubdomainBrute(BaseModule):
    """Descobre subdomínios por força bruta."""

    name = "subdomain_brute"
    description = "Força bruta para subdomínios"

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        # Wordlist básica (poderia ser carregada de arquivo)
        wordlist = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1",
            "webdisk", "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "m",
            "imap", "test", "ns", "blog", "pop3", "dev", "www2", "admin", "forum",
            "news", "vpn", "ns3", "mail2", "new", "mysql", "old", "lists",
            "support", "mobile", "mx", "static", "docs", "beta", "shop", "sql",
            "secure", "demo", "cp", "calendar", "wiki", "web", "media", "email",
            "images", "img", "www1", "intranet", "portal", "video", "sip", "dns",
            "api", "cdn", "stats", "download", "dictionary", "incoming", "support",
            "info", "login", "app", "apps", "dashboard", "monitor", "status",
        ]

        resolver = dns.resolver.Resolver()
        resolver.timeout = validated.timeout
        resolver.lifetime = validated.timeout

        found = []
        total = len(wordlist)
        logger.info(f"Testando {total} subdomínios para {target}")

        # Detecção de wildcard (resolver um subdomínio aleatório)
        wildcard_check = f"wildcard-{hash(target)}-test.{target}"
        try:
            resolver.resolve(wildcard_check, "A")
            wildcard = True
            logger.warning("Wildcard DNS detectado - pode haver falsos positivos")
        except Exception:
            wildcard = False

        def check_sub(sub: str) -> str | None:
            fqdn = f"{sub}.{target}"
            try:
                resolver.resolve(fqdn, "A")
                if wildcard:
                    return fqdn
                return fqdn
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=validated.threads) as executor:
            futures = {executor.submit(check_sub, sub): sub for sub in wordlist}
            for future in as_completed(futures):
                sub = futures[future]
                try:
                    res = future.result()
                    if res:
                        found.append(res)
                        logger.debug(f"Subdomínio encontrado: {res}")
                except Exception as e:
                    logger.warning(f"Erro ao testar {sub}: {e}")

        return ModuleResult(
            module=self.name,
            target=target,
            success=True,
            data={
                "subdomains": found,
                "count": len(found),
                "total_tested": total,
                "wildcard_detected": wildcard,
            },
        )
