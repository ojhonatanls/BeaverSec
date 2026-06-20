import socket
import ssl
import datetime
from utils.config_loader import get_setting

def run(target, **kwargs):
    """
    Obtém informações do certificado SSL/TLS.
    Exemplo: python main.py ssl_scan google.com
    """
    port = kwargs.get('port', 443)
    if ':' in target:
        target, port = target.split(':')
        port = int(port)
        
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, port), timeout=10.0) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()
                
        print(f"\n[+] SSL/TLS Info for {target}:{port}")
        print(f"  Subject: {dict(cert['subject'][0])}")
        print(f"  Issuer: {dict(cert['issuer'][0])}")
        print(f"  Version: {cert.get('version', 'N/A')}")
        
        not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        
        print(f"  Valid From: {not_before}")
        print(f"  Valid To: {not_after}")
        
        days_left = (not_after - datetime.datetime.now()).days
        if days_left < 0:
            print(f"  ⚠️ EXPIRADO há {-days_left} dias!")
        elif days_left < get_setting('modules.ssl_scan.warn_expiry_days', 30):
            print(f"  ⚠️ Atenção: Expira em {days_left} dias!")
        else:
            print(f"  ✅ Válido por mais {days_left} dias.")
            
        # Cipher suite
        print(f"  Cipher: {ssock.cipher()}")
        return cert
        
    except Exception as e:
        print(f"[-] SSL Scan failed: {e}")
        return None