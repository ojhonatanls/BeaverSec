import socket
import concurrent.futures
from utils.config_loader import get_setting

def run(target, **kwargs):
    """
    Brute force de subdomínios.
    Exemplo: python main.py subdomain_brute google.com
    """
    # Wordlist simples embutida (ou você pode carregar de um arquivo)
    wordlist = ["www", "mail", "ftp", "admin", "dev", "api", "test", "staging", 
                "blog", "shop", "support", "vpn", "remote", "ns1", "ns2", "mx",
                "pop", "smtp", "imap", "cloud", "server", "web", "app", "git"]
    
    # Tenta carregar do config se existir
    config_wordlist = get_setting('modules.subdomain_brute.wordlist', None)
    # Se quiser implementar leitura de arquivo externo, adicione aqui
    
    found = []
    timeout = get_setting('modules.subdomain_brute.resolve_timeout', 2.0)
    
    def check_sub(sub):
        subdomain = f"{sub}.{target}"
        try:
            ip = socket.gethostbyname(subdomain)
            return (subdomain, ip)
        except socket.gaierror:
            return None
    
    print(f"[+] Brute-forcing subdomains for {target}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_sub, sub): sub for sub in wordlist}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
                print(f"  Found: {result[0]} -> {result[1]}")
    
    return found