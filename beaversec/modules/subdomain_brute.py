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
    description = "Descobre subdomínios por brute force"

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        # Wordlist expandida com 250+ subdomínios comuns
        wordlist = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1",
            "webdisk", "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "m",
            "imap", "test", "ns", "blog", "pop3", "dev", "www2", "admin", "forum",
            "news", "vpn", "ns3", "mail2", "new", "mysql", "old", "lists",
            "support", "mobile", "mx", "static", "docs", "beta", "shop", "sql",
            "secure", "demo", "cp", "calendar", "wiki", "web", "media", "email",
            "images", "img", "www1", "intranet", "portal", "video", "sip", "dns",
            "api", "cdn", "stats", "download", "incoming", "info", "login", "app",
            "apps", "dashboard", "monitor", "status", "help", "remote", "server",
            "service", "cloud", "storage", "backup", "files", "file", "data",
            "db", "database", "mysql", "postgres", "redis", "mongo", "elastic",
            "kibana", "grafana", "prometheus", "jenkins", "gitlab", "github",
            "bitbucket", "jira", "confluence", "slack", "teams", "zoom", "meet",
            "calendar", "contacts", "drive", "docs", "sheets", "slides", "forms",
            "sites", "groups", "classroom", "meet", "chat", "messages", "inbox",
            "outlook", "exchange", "sharepoint", "onedrive", "teams", "skype",
            "whatsapp", "telegram", "signal", "discord", "reddit", "twitter",
            "facebook", "instagram", "linkedin", "youtube", "vimeo", "dailymotion",
            "twitch", "spotify", "netflix", "amazon", "ebay", "aliexpress",
            "mercadolivre", "shopify", "magento", "woocommerce", "wordpress",
            "joomla", "drupal", "moodle", "canvas", "blackboard", "schoology",
            "edmodo", "zoom", "webex", "gotomeeting", "teamviewer", "anydesk",
            "remote", "rdp", "ssh", "telnet", "ftp", "sftp", "scp", "rsync",
            "nfs", "smb", "cifs", "ldap", "radius", "tacacs", "kerberos",
            "dns", "dhcp", "ntp", "smtp", "pop3", "imap", "sieve", "managesieve",
            "sieve", "sogo", "roundcube", "rainloop", "snappy", "mailman",
            "sympa", "majordomo", "list", "listserv", "groups", "group", "team",
            "project", "projects", "task", "tasks", "todo", "todos", "agenda",
            "schedule", "scheduler", "planner", "planning", "milestone", "release",
            "build", "deploy", "staging", "stage", "prod", "production", "qa",
            "quality", "assurance", "testing", "test", "dev", "development",
            "sandbox", "playground", "demo", "demo2", "demo3", "example", "sample",
            "trial", "free", "premium", "enterprise", "business", "corporate",
            "internal", "external", "public", "private", "restricted", "confidential"
        ]

        resolver = dns.resolver.Resolver()
        resolver.timeout = validated.timeout
        resolver.lifetime = validated.timeout

        found = []
        total = len(wordlist)
        logger.info(f"Testando {total} subdomínios para {target}")

        # Detecção de wildcard
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
