"""Módulo de análise de headers HTTP."""

import requests
from typing import Dict, Any
from beaversec.utils.security import validate_target

SECURITY_HEADERS = {
    'Strict-Transport-Security': 'HSTS',
    'Content-Security-Policy': 'CSP',
    'X-Frame-Options': 'Clickjacking protection',
    'X-Content-Type-Options': 'MIME sniffing protection',
    'Referrer-Policy': 'Referrer policy',
    'Permissions-Policy': 'Permissions policy',
}

def run(target: str, **kwargs) -> Dict[str, Any]:
    """Analisa headers HTTP de segurança do alvo."""
    if not target.startswith(('http://', 'https://')):
        target = f"https://{target}"
    
    timeout = kwargs.get('timeout', 5)
    
    try:
        response = requests.get(target, timeout=timeout, allow_redirects=True)
        headers = response.headers
        results = {}
        
        for header, desc in SECURITY_HEADERS.items():
            if header in headers:
                results[header] = {
                    'present': True,
                    'value': headers[header],
                    'description': desc
                }
            else:
                results[header] = {
                    'present': False,
                    'description': desc
                }
        
        results['_server'] = headers.get('Server', 'Desconhecido')
        results['_status_code'] = response.status_code
        results['_url_final'] = response.url
        
        return results
        
    except requests.exceptions.Timeout:
        return {"error": f"Timeout ao conectar em {target}"}
    except requests.exceptions.ConnectionError:
        return {"error": f"Falha de conexão com {target}"}
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}