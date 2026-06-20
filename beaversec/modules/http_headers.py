import requests
from utils.config_loader import get_setting

def run(target, **kwargs):
    """
    Analisa headers HTTP em busca de boas práticas de segurança.
    Exemplo: python main.py http_headers https://google.com
    """
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    
    try:
        user_agent = get_setting('modules.http_headers.user_agent', 'BeaverSec-Scanner')
        allow_redirects = get_setting('modules.http_headers.redirect', False)
        timeout = get_setting('settings.timeout', 5.0)
        
        response = requests.get(target, timeout=timeout, headers={'User-Agent': user_agent}, allow_redirects=allow_redirects)
        
        print(f"\n[+] HTTP Headers for {target} (Status: {response.status_code})")
        
        # Headers de segurança importantes
        security_headers = {
            'Strict-Transport-Security': 'HSTS (Previne downgrade HTTP)',
            'Content-Security-Policy': 'CSP (Previene XSS)',
            'X-Frame-Options': 'Protege contra Clickjacking',
            'X-Content-Type-Options': 'Previne MIME-sniffing',
            'Referrer-Policy': 'Controla envio de referer',
            'Permissions-Policy': 'Controla recursos do navegador'
        }
        
        for header, description in security_headers.items():
            value = response.headers.get(header)
            status = "✅ Present" if value else "❌ Missing"
            print(f"  {header}: {status} -> {value if value else 'Not Set'}")
        
        # Mostra todos os headers (opcional)
        print("\n[+] Full Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
            
        return response.headers
        
    except requests.exceptions.RequestException as e:
        print(f"[-] HTTP request failed: {e}")
        return None