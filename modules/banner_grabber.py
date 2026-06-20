import socket
import concurrent.futures
from utils.config_loader import get_setting

def run(target, **kwargs):
    """
    Captura banners de serviços comuns e verifica versões vulneráveis.
    Exemplo: python main.py banner_grabber 192.168.1.1
    """
    ports = kwargs.get('ports') or get_setting('modules.banner_grabber.common_ports', [21, 22, 23, 25, 80, 443, 3306, 3389])
    timeout = get_setting('modules.banner_grabber.grab_timeout', 5.0)
    
    # Banco de dados simples de vulnerabilidades (para demonstração)
    vuln_db = {
        'OpenSSH 7.4': 'CVE-2017-15906 (DoS)',
        'Apache 2.4.29': 'CVE-2019-0211 (PrivEsc)',
        'nginx 1.14.0': 'CVE-2019-9511 (DoS)',
        'vsftpd 2.3.4': 'CVE-2011-2523 (Backdoor)',
        'ProFTPD 1.3.3c': 'CVE-2010-4221 (RCE)'
    }
    
    results = []
    
    def grab_banner(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((target, port))
            # Envia um enter para ativar banners em alguns serviços
            sock.send(b'\n')
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            # Verifica se algum padrão vulnerável aparece
            vuln_found = []
            for pattern, cve in vuln_db.items():
                if pattern.lower() in banner.lower():
                    vuln_found.append(f"{pattern} -> {cve}")
            
            return (port, banner, vuln_found)
        except Exception:
            return (port, None, [])
    
    print(f"[+] Grabbing banners from {target}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(grab_banner, p) for p in ports]
        for future in concurrent.futures.as_completed(futures):
            port, banner, vulns = future.result()
            if banner:
                print(f"\n  Port {port}:")
                print(f"    Banner: {banner[:100]}{'...' if len(banner) > 100 else ''}")
                if vulns:
                    print(f"    ⚠️  Possíveis vulnerabilidades: {', '.join(vulns)}")
                results.append((port, banner, vulns))
    
    return results