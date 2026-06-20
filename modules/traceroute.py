import subprocess
import platform
import sys

def run(target, **kwargs):
    """
    Executa traceroute para o alvo (usa comando do sistema).
    Exemplo: python main.py traceroute google.com
    """
    system = platform.system()
    try:
        if system == "Windows":
            cmd = ["tracert", "-d", "-h", "30", target]
        else:  # Linux/Mac
            cmd = ["traceroute", "-n", "-m", "30", target]
        
        print(f"[+] Running traceroute to {target}...")
        print("    (Aguarde, pode levar alguns segundos)")
        
        # Executa e mostra a saída em tempo real
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in process.stdout:
            print(f"    {line.strip()}")
            
        process.wait()
        if process.returncode != 0:
            print(f"[-] Traceroute failed with code {process.returncode}")
            stderr = process.stderr.read()
            if stderr:
                print(f"    Error: {stderr}")
        
        return
        
    except FileNotFoundError:
        print("[-] Comando 'traceroute' ou 'tracert' não encontrado no sistema.")
        print("    Instale com: apt-get install traceroute (Linux) ou utilize WSL.")
    except Exception as e:
        print(f"[-] Erro inesperado: {e}")