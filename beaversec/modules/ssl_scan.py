"""Módulo de análise SSL/TLS."""

import ssl
import socket
import datetime
from datetime import timezone
from typing import Dict, Any
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from beaversec.utils.security import validate_target

def run(target: str, **kwargs) -> Dict[str, Any]:
    """Analisa certificado SSL/TLS do alvo."""
    target_type = validate_target(target)
    if target_type == 'cidr':
        raise ValueError("SSL scan requer um IP ou domínio, não um CIDR")
    
    port = kwargs.get('port', 443)
    timeout = kwargs.get('timeout', 5)
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                cert_der = ssock.getpeercert(binary_form=True)
                cert = x509.load_der_x509_certificate(cert_der, default_backend())
                
                subject = cert.subject
                issuer = cert.issuer
                not_before = cert.not_valid_before
                not_after = cert.not_valid_after
                
                san = []
                for ext in cert.extensions:
                    if ext.oid._name == 'subjectAltName':
                        san = [str(name) for name in ext.value]
                
                valid_days = (not_after - datetime.datetime.now()).days
                cipher = ssock.cipher()
                
                return {
                    "module_name": "ssl_scan",
                    "target": target,
                    "status": "success",
                    "data": {
                        "cert_info": {
                            "subject": str(subject),
                            "issuer": str(issuer),
                            "valid_from": str(not_before),
                            "valid_to": str(not_after),
                            "subject_alt_names": san
                        },
                        "valid_days": valid_days,
                        "cipher": f"{cipher[0]} ({cipher[1]}, {cipher[2]} bits)"
                    },
                    "timestamp": datetime.datetime.now(timezone.utc).isoformat()
                }
                
    except socket.timeout:
        return {"error": f"Timeout ao conectar em {target}:{port}"}
    except ssl.SSLError as e:
        return {"error": f"Erro SSL: {str(e)}"}
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}