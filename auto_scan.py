#!/usr/bin/env python3
"""
BeaverSec - Script de Varredura Automática
Permite escanear múltiplos alvos de uma vez
"""

import subprocess
import sys
import time

def scan_target(target, verbose=False):
    """Executa varredura em um alvo"""
    cmd = ["python3", "main.py", "ping_sweep", target]
    if verbose:
        cmd.append("-v")
    
    print(f"\n{'='*50}")
    print(f"🔍 Escaneando: {target}")
    print(f"{'='*50}\n")
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao escanear {target}: {e}")
        return False

def main():
    """Função principal"""
    # Lista de alvos para escanear
    targets = [
        "8.8.8.8",           # Google DNS
        "1.1.1.1",           # Cloudflare DNS
        "192.168.1.0/24",    # Rede local
    ]
    
    print("🦫 BeaverSec - Varredura Automática")
    print("="*50)
    
    # Verifica modo verbose
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    
    for target in targets:
        scan_target(target, verbose)
        time.sleep(1)  # Pequena pausa entre varreduras
    
    print("\n✅ Todas as varreduras concluídas!")

if __name__ == "__main__":
    main()