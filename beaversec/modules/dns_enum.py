"""Módulo de enumeração DNS."""

import dns.resolver
from typing import Dict, Any
from beaversec.utils.security import validate_target

def run(target: str, **kwargs) -> Dict[str, Any]:
    """Enumera registros DNS do alvo."""
    target_type = validate_target(target)
    if target_type != 'domain':
        raise ValueError(f"DNS enumeração requer um domínio, não {target_type}")
    
    record_types = kwargs.get('record_type', 'ALL')
    if record_types == 'ALL':
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    else:
        record_types = [record_types.upper()]
    
    results = {}
    for record in record_types:
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = kwargs.get('timeout', 5)
            answers = resolver.resolve(target, record)
            results[record] = [str(r) for r in answers]
        except dns.resolver.NoAnswer:
            results[record] = []
        except dns.resolver.NXDOMAIN:
            raise ValueError(f"Domínio {target} não existe")
        except Exception as e:
            results[record] = [f"Erro: {str(e)}"]
    
    return {
        "target": target,
        "records": results,
        "total_records": sum(len(v) for v in results.values())
    }