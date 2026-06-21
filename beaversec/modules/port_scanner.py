"""Módulo de scanner de portas."""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 135: "RPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP",
    5900: "VNC", 8080: "HTTP-Alt"
}

def run(target: str, **kwargs) -> Dict[str, Any]:
    """
    Escaneia portas de um alvo.
    
    Args:
        target: IP ou domínio
        **kwargs: ports (str), timeout (int), max_threads (int)
    """
    ports_str = kwargs.get("ports", "21,22,23,25,53,80,443,3306,3389,8080")
    timeout = kwargs.get("timeout", 2)
    max_threads = kwargs.get("max_threads", 10)
    
    # Parse ports
    ports = []
    for part in ports_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    ports = sorted(set(ports))
    
    print(f"🔍 Escaneando {target} - {len(ports)} portas...")
    
    # Resolve hostname
    try:
        ip = socket.gethostbyname(target)
        print(f"   Resolvido: {ip}")
    except:
        ip = target
    
    # Escaneia
    open_ports = []
    
    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return port if result == 0 else None
        except:
            return None
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_port, port): port for port in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
                service = COMMON_SERVICES.get(result, "Unknown")
                print(f"   ✅ Porta {result} ({service}) aberta")
    
    return {
        "target": ip,
        "open_ports": sorted(open_ports),
        "open_count": len(open_ports),
        "total_scanned": len(ports)
    }
