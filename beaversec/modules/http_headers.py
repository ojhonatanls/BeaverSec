"""
Análise de cabeçalhos HTTP de segurança.
"""
import logging

import requests

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class HTTPHeaders(BaseModule):
    """Analisa cabeçalhos HTTP de segurança."""

    name = "http_headers"
    description = "Análise de cabeçalhos HTTP de segurança"

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        proxies = None
        if validated.proxy:
            proxies = {"http": validated.proxy, "https": validated.proxy}

        try:
            session = requests.Session()
            session.proxies = proxies
            session.timeout = validated.timeout

            resp = session.get(target, allow_redirects=True, verify=False)
            headers = dict(resp.headers)

            # Análise de segurança
            security_headers = {
                "Strict-Transport-Security": "HSTS",
                "Content-Security-Policy": "CSP",
                "X-Frame-Options": "Clickjacking",
                "X-Content-Type-Options": "MIME Sniffing",
                "Referrer-Policy": "Referrer",
                "Permissions-Policy": "Permissions",
            }

            analysis = {}
            for hdr, name in security_headers.items():
                if hdr in headers:
                    analysis[name] = {"present": True, "value": headers[hdr]}
                else:
                    analysis[name] = {"present": False, "value": None}

            return ModuleResult(
                module=self.name,
                target=target,
                success=True,
                data={
                    "headers": headers,
                    "security_analysis": analysis,
                    "status_code": resp.status_code,
                    "server": headers.get("Server", "unknown"),
                },
            )

        except Exception as e:
            return ModuleResult(
                module=self.name,
                target=target,
                success=False,
                errors=[str(e)],
            )
