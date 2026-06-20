"""
Módulo Ping Sweep - Descoberta de hosts ativos via ICMP (ping)
Suporta IP único (ex: 8.8.8.8) e rede CIDR (ex: 192.168.1.0/24)
"""
import ipaddress
import subprocess
import platform
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from beaversec.utils.logger import setup_logger

# Constantes ajustáveis
MAX_WORKERS = 100
PING_TIMEOUT = 1.5
PING_COUNT = 1

class PingSweep:
    """
    Classe responsável pela lógica de varredura ICMP.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = setup_logger()
        self.hosts_ativos: List[str] = []
        self.sistema = platform.system().lower()
        
    def _build_ping_command(self, ip: str) -> List[str]:
        if self.sistema == "windows":
            return [
                "ping", 
                "-n", str(PING_COUNT), 
                "-w", str(int(PING_TIMEOUT * 1000)),
                str(ip)
            ]
        else:
            return [
                "ping", 
                "-c", str(PING_COUNT), 
                "-W", str(int(PING_TIMEOUT)), 
                str(ip)
            ]
    
    def _ping_host(self, ip: str) -> bool:
        cmd = self._build_ping_command(ip)
        
        try:
            if self.verbose:
                result = subprocess.run(
                    cmd, 
                    capture_output=False, 
                    timeout=PING_TIMEOUT + 0.5
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    timeout=PING_TIMEOUT + 0.5,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return result.returncode == 0
                
        except subprocess.TimeoutExpired:
            return False
        except FileNotFoundError:
            self.logger.error("Comando 'ping' não encontrado no sistema.")
            return False
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Erro ao pingar {ip}: {e}")
            return False
    
    def _validate_target(self, target: str) -> List[str]:
        ips: List[str] = []
        
        if '/' in target:
            try:
                rede = ipaddress.ip_network(target, strict=False)
                ips = [str(ip) for ip in rede.hosts()]
                self.logger.info(f"Rede {target} contém {len(ips)} hosts para escanear.")
            except ValueError as e:
                raise ValueError(f"CIDR inválido: {e}")
        else:
            try:
                ipaddress.ip_address(target)
                ips = [target]
                self.logger.info(f"Host único: {target}")
            except ValueError as e:
                raise ValueError(f"IP inválido: {e}")
        
        if not ips:
            raise ValueError("Nenhum IP válido encontrado para escanear.")
        
        return ips
    
    def scan(self, target: str) -> List[str]:
        ips = self._validate_target(target)
        
        self.hosts_ativos = []
        print(f"\n🔍 Escaneando {len(ips)} host(s)... (use -v para ver cada tentativa)")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_ip = {
                executor.submit(self._ping_host, ip): ip 
                for ip in ips
            }
            
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    if future.result():
                        self.hosts_ativos.append(ip)
                        print(f"✅ {ip} está ATIVO")
                    elif self.verbose:
                        print(f"❌ {ip} inativo ou não respondeu")
                except Exception as e:
                    self.logger.error(f"Erro inesperado em {ip}: {e}")
        
        return self.hosts_ativos
    
    def report(self) -> None:
        if self.hosts_ativos:
            print(f"\n{'='*50}")
            print(f"✅ SCAN CONCLUÍDO COM SUCESSO!")
            print(f"📊 Total de hosts ativos: {len(self.hosts_ativos)}")
            print(f"\n📋 LISTA DE HOSTS ATIVOS:")
            for idx, ip in enumerate(self.hosts_ativos, 1):
                print(f"   {idx:>3}. {ip}")
            print(f"{'='*50}\n")
        else:
            print(f"\n{'='*40}")
            print(f"❌ NENHUM HOST ATIVO ENCONTRADO.")
            print(f"   Verifique sua conectividade ou o alvo informado.")
            print(f"{'='*40}\n")


def run(target: str, verbose: bool = False) -> None:
    try:
        scanner = PingSweep(verbose=verbose)
        scanner.scan(target)
        scanner.report()
    except ValueError as e:
        print(f"\n[ERRO] {e}")
        print("   Formato aceito: IP (8.8.8.8) ou CIDR (192.168.1.0/24)")
    except KeyboardInterrupt:
        print("\n\n[!] Varredura interrompida pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        if verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    run("8.8.8.8", verbose=True)