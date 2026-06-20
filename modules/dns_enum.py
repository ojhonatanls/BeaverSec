import dns.resolver
import dns.exception
from utils.config_loader import get_setting

def run(target, **kwargs):
    """
    Módulo de enumeração DNS.
    Exemplo: python main.py dns_enum google.com
    """
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    results = {target: {}}
    
    for record in record_types:
        try:
            answers = dns.resolver.resolve(target, record)
            results[target][record] = [str(r) for r in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            results[target][record] = []
        except Exception as e:
            results[target][record] = f"Error: {str(e)}"
    
    # Exibe formatado
    print(f"\n[+] DNS Enumeration for {target}")
    for rec, data in results[target].items():
        if data:
            print(f"  {rec}: {', '.join(data) if isinstance(data, list) else data}")
        else:
            print(f"  {rec}: No records found")
    
    return results