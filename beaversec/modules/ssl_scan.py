"""
Análise de certificados SSL/TLS.
"""
import logging
import socket
import ssl
from datetime import datetime

from beaversec.core.base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


class SSLScan(BaseModule):
    """Analisa certificados SSL/TLS de um host."""

    name = "ssl_scan"
    description = "Análise de certificados SSL/TLS"

    def run(self, target: str, **kwargs) -> ModuleResult:
        self._log_start(target)
        validated = self.validate_input(target, **kwargs)

        # Suporta host:port ou apenas host (porta 443)
        if ":" in target:
            host, port_str = target.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                return ModuleResult(
                    module=self.name,
                    target=target,
                    success=False,
                    errors=[f"Porta inválida: {port_str}"],
                )
        else:
            host, port = target, 443

        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=validated.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()

            if not cert:
                return ModuleResult(
                    module=self.name,
                    target=target,
                    success=False,
                    errors=["Nenhum certificado obtido"],
                )

            # Extrair informações
            data = {
                "subject": dict(x[0] for x in cert.get("subject", [])),
                "issuer": dict(x[0] for x in cert.get("issuer", [])),
                "version": cert.get("version"),
                "serial_number": cert.get("serialNumber"),
                "not_before": cert.get("notBefore"),
                "not_after": cert.get("notAfter"),
                "subject_alt_name": [x[1] for x in cert.get("subjectAltName", [])],
                "ocsp": cert.get("OCSP"),
                "ca_issuers": cert.get("caIssuers"),
            }

            # Validar datas
            try:
                not_after = datetime.strptime(data["not_after"], "%b %d %H:%M:%S %Y %Z")
                data["days_until_expiry"] = (not_after - datetime.utcnow()).days
            except Exception:
                data["days_until_expiry"] = None

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
