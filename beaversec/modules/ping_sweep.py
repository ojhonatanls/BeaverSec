"""Módulo de ping sweep com segurança."""

import subprocess
import re
from typing import Dict, Any

def run(target: str, **kwargs) -> Dict[str, Any]:
    """
    Realiza ping sweep no alvo.
    
    Args:
        target: IP ou domínio para ping
        **kwargs: timeout (int), count (int)
    
    Returns:
        Dict com resultados
    """
    timeout = kwargs.get("timeout", 3)
    count = kwargs.get("count", 1)
    
    print(f"📡 Pingando {target}...")
    
    try:
        # Comando seguro com lista de argumentos
        cmd = ["ping", "-c", str(count), "-W", str(timeout), target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+1)
        
        alive = result.returncode == 0
        
        # Extrai RTT
        rtt = None
        if alive:
            match = re.search(r"time=(\d+\.?\d*)", result.stdout)
            if match:
                rtt = float(match.group(1))
        
        return {
            "host": target,
            "alive": alive,
            "rtt": rtt,
            "output": result.stdout.strip()
        }
        
    except subprocess.TimeoutExpired:
        return {"host": target, "alive": False, "error": "timeout"}
    except Exception as e:
        return {"host": target, "alive": False, "error": str(e)}
