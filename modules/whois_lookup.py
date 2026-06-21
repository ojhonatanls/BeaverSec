import whois
from datetime import datetime, timezone

def run(target, **kwargs):
    """
    Consulta informações WHOIS de um domínio.
    Exemplo: python main.py whois_lookup google.com
    """
    try:
        w = whois.whois(target)
        
        print(f"\n[+] WHOIS Lookup for {target}")
        print(f"  Registrar: {w.registrar}")
        print(f"  Creation Date: {w.creation_date}")
        print(f"  Expiration Date: {w.expiration_date}")
        print(f"  Name Servers: {w.name_servers}")
        print(f"  Status: {w.status}")
        print(f"  Emails: {w.emails}")
        
        # Verifica se está expirando (corrigido para timezone)
        if w.expiration_date:
            if isinstance(w.expiration_date, list):
                exp = w.expiration_date[0]
            else:
                exp = w.expiration_date
            
            # Se a data não tiver timezone, adiciona o timezone UTC
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            days_left = (exp - now).days
            
            if days_left < 30:
                print(f"  ⚠️ Domínio expira em {days_left} dias!")
        
        return w
        
    except Exception as e:
        print(f"[-] WHOIS lookup failed: {e}")
        return None