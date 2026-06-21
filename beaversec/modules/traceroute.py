"""Módulo de traceroute."""

import subprocess
import re
from typing import Dict, Any
from beaversec.utils.security import validate_target

def run(target: str, **kwargs) -> Dict[str, Any]:
    """Rastreia a rota até o alvo."""
    target_type = validate_target(target)
    if target_type == 'cidr':
        raise ValueError("Traceroute requer um IP ou domínio, não um CIDR")
    
    max_hops = kwargs.get('max_hops', 30)
    timeout = kwargs.get('timeout', 3)
    
    try:
        cmd = ["traceroute", "-m", str(max_hops), "-w", str(timeout), target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout*max_hops)
        
        if result.returncode != 0:
            return {"error": result.stderr.strip() or "Falha no traceroute"}
        
        lines = result.stdout.strip().split('\n')
        hops = []
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 2:
                continue
            
            hop_num = parts[0]
            ip_match = re.search(r'\(([^)]+)\)', line)
            if ip_match:
                ip = ip_match.group(1)
            else:
                ip = parts[1] if '.' in parts[1] or ':' in parts[1] else '*'
            
            time_match = re.search(r'(\d+\.?\d*)\s*ms', line)
            time_ms = float(time_match.group(1)) if time_match else None
            
            hops.append({
                "hop": int(hop_num),
                "ip": ip,
                "time_ms": time_ms,
                "raw": line.strip()
            })
        
        return {
            "target": target,
            "max_hops": max_hops,
            "hops": hops,
            "total_hops": len(hops)
        }
        
    except FileNotFoundError:
        return {"error": "Comando 'traceroute' não encontrado. Instale com: sudo apt install traceroute"}
    except subprocess.TimeoutExpired:
        return {"error": "Timeout no traceroute"}
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}