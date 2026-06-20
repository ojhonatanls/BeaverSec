"""
Módulo Scanner de Portas - Varre portas TCP em um host
"""
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from beaversec.utils.logger import setup_logger

# Portas comuns para escanear
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC",
    139: "NETBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 1723: "PPTP", 3306: "MYSQL",
    3389: "RDP", 5432: "POSTGRES", 5900: "VNC", 6379: "REDIS",
    27017: "MONGODB"
}

MAX_WORKERS = 50
TIMEOUT = 1.0

def scan_port(host: str, port: int, verbose: bool = False) -> tuple:
    """Tenta conectar a uma porta específica"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return (port, True)
        return (port, False)
    except Exception:
        return (port, False)

def run(target: str, verbose: bool = False) -> None:
    """Função obrigatória para o ModuleHandler"""
    logger = setup_logger()
    host = target
    ports_to_scan = list(COMMON_PORTS.keys())
    
    print(f"\n🔍 Escaneando {host} - {len(ports_to_scan)} portas comuns...")
    
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scan_port, host, port, verbose): port for port in ports_to_scan}
        
        for future in as_completed(futures):
            port = futures[future]
            try:
                port_num, is_open = future.result()
                if is_open:
                    service = COMMON_PORTS.get(port_num, "DESCONHECIDO")
                    open_ports.append(port_num)
                    print(f"✅ Porta {port_num} ABERTA ({service})")
                elif verbose:
                    print(f"❌ Porta {port_num} FECHADA")
            except Exception as e:
                logger.error(f"Erro ao escanear porta {port}: {e}")
    
    # Relatório
    if open_ports:
        print(f"\n{'='*50}")
        print(f"✅ SCAN CONCLUÍDO!")
        print(f"📊 Total de portas abertas: {len(open_ports)}")
        print(f"\n📋 PORTAS ABERTAS:")
        for port in sorted(open_ports):
            service = COMMON_PORTS.get(port, "DESCONHECIDO")
            print(f"   {port:>5} - {service}")
        print(f"{'='*50}\n")
    else:
        print(f"\n❌ NENHUMA PORTA ABERTA ENCONTRADA em {host}.\n")

if __name__ == "__main__":
    run("scanme.nmap.org", verbose=True)