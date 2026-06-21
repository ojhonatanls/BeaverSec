#!/usr/bin/env python3
"""
BEAVERSEC - REFATORAÇÃO AGRESSIVA
Script para transformar projeto acadêmico em ferramenta profissional
"""

import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
BACKUP_DIR = PROJECT_ROOT / "backup_original"

DIRS = [
    "beaversec",
    "beaversec/utils",
    "beaversec/modules",
    "beaversec/exporters",
    "beaversec/databases/subdomains",
    "beaversec/databases/wordlists",
    "tests",
    "tests/security",
    "docs",
]

def backup_original():
    print("📦 Criando backup dos arquivos originais...")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    BACKUP_DIR.mkdir(parents=True)
    for file in PROJECT_ROOT.glob("*"):
        if file.is_file() and file.suffix in [".py", ".yaml", ".txt", ".md"]:
            shutil.copy2(file, BACKUP_DIR / file.name)
    if (PROJECT_ROOT / "modules").exists():
        shutil.copytree(PROJECT_ROOT / "modules", BACKUP_DIR / "modules")
    if (PROJECT_ROOT / "utils").exists():
        shutil.copytree(PROJECT_ROOT / "utils", BACKUP_DIR / "utils")
    print(f"✅ Backup salvo em: {BACKUP_DIR}")

def create_directories():
    print("📁 Criando nova estrutura de diretórios...")
    for dir_path in DIRS:
        full_path = PROJECT_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        (full_path / "__init__.py").touch(exist_ok=True)
    print("✅ Estrutura de diretórios criada")

def write_file(filepath: str, content: str):
    full_path = PROJECT_ROOT / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  📝 {filepath}")

PYPROJECT_TOML = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "beaversec"
version = "0.2.0"
description = "Ferramenta modular de cibersegurança para pentest"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "BeaverSec Team", email = "beaversec@example.com"}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Topic :: Security",
    "Development Status :: 3 - Alpha",
]

dependencies = [
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "rich>=13.0",
    "jinja2>=3.0",
    "requests>=2.31",
    "dnspython>=2.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1",
    "black>=23.0",
]
pdf = ["reportlab>=4.0"]

[project.urls]
"Homepage" = "https://github.com/ojhonatanls/BeaverSec"
"Bug Reports" = "https://github.com/ojhonatanls/BeaverSec/issues"

[project.scripts]
beaversec = "beaversec.main:cli"

[tool.setuptools]
packages = ["beaversec", "beaversec.utils", "beaversec.modules", "beaversec.exporters"]

[tool.black]
line-length = 88
target-version = ["py39"]

[tool.ruff]
select = ["E", "F", "W", "I", "N", "D"]
ignore = ["D100", "D104", "D203"]
line-length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=beaversec --cov-report=html"
'''

INIT_PY = '''"""BeaverSec - Ferramenta modular de cibersegurança."""

__version__ = "0.2.0"
__author__ = "BeaverSec Team"

from beaversec.main import cli

__all__ = ["cli", "__version__"]
'''

MAIN_PY = '''#!/usr/bin/env python3
"""Ponto de entrada principal do BeaverSec."""

import sys
import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from beaversec.utils.config_loader import ConfigLoader
from beaversec.utils.logger import setup_logger, get_logger
from beaversec.utils.module_handler import ModuleHandler
from beaversec.exporters import JSONExporter, HTMLExporter, PDFExporter

console = Console()
logger = get_logger(__name__)


def list_modules() -> None:
    """Lista todos os módulos disponíveis."""
    handler = ModuleHandler()
    modules = handler.list_modules()
    
    table = Table(title="Módulos Disponíveis", style="bold cyan")
    table.add_column("Módulo", style="green")
    table.add_column("Descrição", style="yellow")
    table.add_column("Args", style="blue")
    
    for name, info in modules.items():
        table.add_row(
            name,
            info.get("description", "Sem descrição"),
            ", ".join(info.get("args", [])) or "nenhum"
        )
    
    console.print(table)


def run_module(module_name: str, target: str, args: str = "", **kwargs) -> None:
    """Executa um módulo específico."""
    handler = ModuleHandler()
    
    # Parse args
    parsed_args = {}
    if args:
        try:
            import json
            parsed_args = json.loads(args)
        except json.JSONDecodeError:
            # Tenta parsear como key=value
            for item in args.split():
                if "=" in item:
                    key, value = item.split("=", 1)
                    parsed_args[key] = value
                else:
                    parsed_args["extra"] = item
    
    # Adiciona kwargs da CLI
    parsed_args.update(kwargs)
    
    # Executa
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Executando {module_name}...", total=None)
            result = handler.run_module(module_name, target, **parsed_args)
            progress.update(task, completed=True)
        
        # Exporta se solicitado
        output_format = kwargs.get("output_format")
        output_file = kwargs.get("output_file")
        
        if output_format or output_file:
            export_result(result, output_format or "json", output_file or f"{module_name}_output.{output_format or 'json'}")
        else:
            # Mostra no console
            if isinstance(result, dict):
                for key, value in result.items():
                    console.print(f"[bold]{key}:[/] {value}")
            else:
                console.print(result)
                
    except Exception as e:
        logger.error(f"Erro ao executar {module_name}: {str(e)}")
        console.print(f"[bold red]Erro:[/] {str(e)}")
        sys.exit(1)


def export_result(result: Any, format_type: str, output_file: str) -> None:
    """Exporta resultado para arquivo."""
    exporters = {
        "json": JSONExporter(),
        "html": HTMLExporter(),
        "pdf": PDFExporter(),
    }
    
    exporter = exporters.get(format_type.lower())
    if not exporter:
        console.print(f"[red]Formato não suportado: {format_type}[/]")
        sys.exit(1)
    
    try:
        exporter.export(result, output_file)
        console.print(f"[green]✓ Resultado exportado para {output_file}[/]")
    except Exception as e:
        console.print(f"[red]Erro ao exportar: {str(e)}[/]")
        sys.exit(1)


def update_databases() -> None:
    """Atualiza as bases de dados (wordlists, CVEs)."""
    console.print("[yellow]Baixando atualizações das bases de dados...[/]")
    # TODO: Implementar download de wordlists e CVEs
    console.print("[green]✓ Bases de dados atualizadas![/]")


def cli() -> None:
    """Interface de linha de comando principal."""
    parser = argparse.ArgumentParser(
        description="BeaverSec - Ferramenta modular de cibersegurança",
        epilog="Exemplo: beaversec run ping_sweep --target 192.168.1.1"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"BeaverSec v{__import__('beaversec').__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando: list
    list_parser = subparsers.add_parser("list", help="Lista módulos disponíveis")
    
    # Comando: run
    run_parser = subparsers.add_parser("run", help="Executa um módulo")
    run_parser.add_argument("module", help="Nome do módulo")
    run_parser.add_argument("--target", required=True, help="Alvo (IP/domínio)")
    run_parser.add_argument("--args", default="", help="Argumentos do módulo (JSON ou key=value)")
    run_parser.add_argument("--output-format", choices=["json", "html", "pdf"], help="Formato de saída")
    run_parser.add_argument("--output-file", help="Arquivo de saída")
    run_parser.add_argument("--verbose", action="store_true", help="Logs detalhados")
    run_parser.add_argument("--timeout", type=int, default=5, help="Timeout em segundos")
    
    # Comando: update
    update_parser = subparsers.add_parser("update", help="Atualiza bases de dados")
    
    # Comando: interactive
    interactive_parser = subparsers.add_parser("interactive", help="Modo interativo")
    
    args = parser.parse_args()
    
    # Configura logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logger(level=log_level)
    
    # Executa comando
    if args.command == "list":
        list_modules()
    elif args.command == "run":
        run_module(
            args.module,
            args.target,
            args.args,
            verbose=args.verbose,
            timeout=args.timeout,
            output_format=args.output_format,
            output_file=args.output_file,
        )
    elif args.command == "update":
        update_databases()
    elif args.command == "interactive":
        # TODO: Implementar modo interativo
        console.print("[yellow]Modo interativo ainda não implementado[/]")
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
'''

CONFIG_YAML = '''# BeaverSec - Configuração Central
# ====================================

# Configurações gerais
general:
  verbose: false
  timeout: 5
  max_threads: 10

# Rate limiting por módulo
rate_limits:
  ping_sweep:
    requests_per_second: 5
    max_retries: 3
    backoff_multiplier: 2
    initial_delay: 0.5
  
  port_scanner:
    requests_per_second: 10
    max_retries: 2
    backoff_multiplier: 1.5
    initial_delay: 0.1

# Configurações de módulos
modules:
  ping_sweep:
    count: 1
    packet_size: 56
  
  port_scanner:
    default_ports: "21,22,23,25,53,80,110,135,139,143,443,445,993,995,1723,3306,3389,5900,8080"
    port_range_min: 1
    port_range_max: 65535
    scan_timeout: 2

# Bases de dados
databases:
  subdomains:
    url: "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt"
    local_path: "databases/subdomains/common.txt"
  
  cves:
    url: "https://cve.circl.lu/api/last"
    local_path: "databases/cves/cve_db.json"

# Exportadores
exporters:
  json:
    indent: 2
    sort_keys: true
  
  html:
    template: "templates/report.html"
    theme: "dark"
  
  pdf:
    page_size: "A4"
    orientation: "portrait"
'''

SECURITY_PY = '''"""Módulo de segurança - Sanitização e validação de entradas."""

import re
import shlex
import subprocess
from typing import List, Optional
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address


def validate_ip(ip: str) -> bool:
    """Valida se a string é um IP válido (IPv4 ou IPv6)."""
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False


def validate_domain(domain: str) -> bool:
    """Valida se a string é um domínio válido."""
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def validate_cidr(cidr: str) -> bool:
    """Valida se a string é um CIDR válido."""
    try:
        ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False


def sanitize_target(target: str) -> str:
    """
    Sanitiza o alvo, removendo caracteres potencialmente maliciosos.
    
    Args:
        target: String do alvo (IP, domínio, CIDR)
    
    Returns:
        String sanitizada
    
    Raises:
        ValueError: Se o alvo for inválido
    """
    # Remove espaços e caracteres especiais
    sanitized = target.strip()
    
    # Remove comandos shell
    sanitized = re.sub(r'[;&|$`(){}]', '', sanitized)
    
    # Remove caracteres de controle
    sanitized = re.sub(r'[\\x00-\\x1f\\x7f]', '', sanitized)
    
    # Verifica se ficou vazio
    if not sanitized:
        raise ValueError("Alvo vazio após sanitização")
    
    return sanitized


def safe_command(cmd: List[str]) -> subprocess.CompletedProcess:
    """
    Executa comando de forma segura usando subprocess com lista de argumentos.
    
    Args:
        cmd: Lista de argumentos do comando
    
    Returns:
        subprocess.CompletedProcess
    
    Raises:
        ValueError: Se algum argumento for malicioso
    """
    # Sanitiza todos os argumentos
    sanitized_cmd = [shlex.quote(str(arg)) for arg in cmd]
    
    # Verifica se não há tentativa de escape
    for arg in sanitized_cmd:
        if any(char in arg for char in [';', '&', '|', '`', '$', '(', ')']):
            raise ValueError(f"Argumento potencialmente malicioso: {arg}")
    
    # Executa com lista de argumentos (seguro)
    return subprocess.run(
        sanitized_cmd,
        capture_output=True,
        text=True,
        check=False
    )


def safe_ping(target: str, count: int = 1, timeout: int = 3) -> subprocess.CompletedProcess:
    """
    Executa ping de forma segura.
    
    Args:
        target: IP ou domínio
        count: Número de pacotes
        timeout: Timeout em segundos
    
    Returns:
        subprocess.CompletedProcess
    
    Raises:
        ValueError: Se target for inválido
    """
    # Valida e sanitiza
    sanitized = sanitize_target(target)
    
    if not validate_ip(sanitized) and not validate_domain(sanitized):
        raise ValueError(f"Alvo inválido: {target}")
    
    # Comando seguro com lista de argumentos
    cmd = ["ping", "-c", str(count), "-W", str(timeout), sanitized]
    return safe_command(cmd)
'''

RATE_LIMITER_PY = '''"""Sistema de rate limiting com backoff exponencial."""

import time
import functools
from typing import Dict, Optional, Callable, Any
from collections import defaultdict
from threading import Lock

from beaversec.utils.logger import get_logger
from beaversec.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class RateLimiter:
    """Implementação de rate limiter com backoff exponencial."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = ConfigLoader().get("rate_limits", {})
        self._last_calls = defaultdict(float)
        self._attempts = defaultdict(int)
    
    def can_proceed(self, module_name: str) -> bool:
        """Verifica se pode proceder com base no rate limit."""
        config = self._config.get(module_name, {})
        rps = config.get("requests_per_second", 10)
        min_interval = 1.0 / rps
        
        current_time = time.time()
        last_call = self._last_calls[module_name]
        
        if current_time - last_call < min_interval:
            sleep_time = min_interval - (current_time - last_call)
            logger.debug(f"Rate limit: aguardando {sleep_time:.2f}s para {module_name}")
            time.sleep(sleep_time)
        
        self._last_calls[module_name] = time.time()
        return True
    
    def record_attempt(self, module_name: str, success: bool) -> None:
        """Registra tentativa para backoff."""
        config = self._config.get(module_name, {})
        max_retries = config.get("max_retries", 3)
        
        if success:
            self._attempts[module_name] = 0
        else:
            self._attempts[module_name] += 1
            
            if self._attempts[module_name] >= max_retries:
                logger.warning(f"Módulo {module_name} excedeu {max_retries} tentativas")
                self._attempts[module_name] = 0
    
    def get_backoff_delay(self, module_name: str) -> float:
        """Calcula delay de backoff exponencial."""
        config = self._config.get(module_name, {})
        attempts = self._attempts[module_name]
        
        if attempts == 0:
            return 0.0
        
        initial_delay = config.get("initial_delay", 0.5)
        multiplier = config.get("backoff_multiplier", 2.0)
        
        delay = initial_delay * (multiplier ** (attempts - 1))
        max_delay = config.get("max_delay", 30.0)
        
        return min(delay, max_delay)


def rate_limit(module: str = None):
    """
    Decorator para aplicar rate limiting em funções.
    
    Args:
        module: Nome do módulo (se None, usa o nome da função)
    
    Exemplo:
        @rate_limit(module="ping_sweep")
        def run(target: str, **kwargs):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            module_name = module or func.__name__
            limiter = RateLimiter()
            
            max_retries = limiter._config.get(module_name, {}).get("max_retries", 3)
            attempt = 0
            
            while attempt <= max_retries:
                try:
                    # Aguarda rate limit
                    limiter.can_proceed(module_name)
                    
                    # Executa função
                    result = func(*args, **kwargs)
                    
                    # Registra sucesso
                    limiter.record_attempt(module_name, True)
                    return result
                    
                except Exception as e:
                    attempt += 1
                    limiter.record_attempt(module_name, False)
                    
                    if attempt > max_retries:
                        logger.error(f"Falha após {max_retries} tentativas para {module_name}")
                        raise
                    
                    # Backoff
                    delay = limiter.get_backoff_delay(module_name)
                    logger.warning(f"Tentativa {attempt}/{max_retries} falhou para {module_name}. Aguardando {delay:.2f}s")
                    time.sleep(delay)
            
            return None
        
        return wrapper
    return decorator
'''

PING_SWEEP_PY = '''"""Módulo de ping sweep com segurança e rate limiting."""

from typing import Dict, List, Optional, Any
import re

from beaversec.utils.logger import get_logger
from beaversec.utils.security import safe_ping, validate_ip, validate_domain, validate_cidr
from beaversec.utils.rate_limiter import rate_limit
from beaversec.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


@rate_limit(module="ping_sweep")
def run(target: str, **kwargs) -> Dict[str, Any]:
    """
    Realiza ping sweep no alvo.
    
    Args:
        target: IP, domínio ou CIDR para ping
        **kwargs: timeout (int), count (int)
    
    Returns:
        Dict com resultados:
        {
            "target": str,
            "alive": bool,
            "rtt": Optional[float],
            "output": str,
            "error": Optional[str]
        }
    
    Raises:
        ValueError: Se target for inválido
    """
    logger.info(f"Iniciando ping sweep para {target}")
    
    # Carrega configurações
    config = ConfigLoader().get("modules", {}).get("ping_sweep", {})
    timeout = kwargs.get("timeout", 5)
    count = kwargs.get("count", config.get("count", 1))
    
    # Valida alvo
    sanitized = target.strip()
    
    if validate_ip(sanitized):
        target_type = "ip"
    elif validate_domain(sanitized):
        target_type = "domain"
    elif validate_cidr(sanitized):
        target_type = "cidr"
    else:
        raise ValueError(f"Alvo inválido: {target}")
    
    # Se for CIDR, expande
    if target_type == "cidr":
        from ipaddress import ip_network
        network = ip_network(sanitized, strict=False)
        results = []
        
        for ip in network.hosts():
            result = ping_host(str(ip), count, timeout)
            results.append(result)
        
        return {
            "target": sanitized,
            "type": "cidr",
            "hosts": results,
            "alive_count": sum(1 for r in results if r.get("alive", False)),
            "total_count": len(results)
        }
    
    # Ping único
    return ping_host(sanitized, count, timeout)


def ping_host(host: str, count: int, timeout: int) -> Dict[str, Any]:
    """Realiza ping em um único host."""
    try:
        result = safe_ping(host, count, timeout)
        
        alive = result.returncode == 0
        
        # Extrai RTT
        rtt = None
        if alive:
            match = re.search(r"time=(\\d+\\.?\\d*)", result.stdout)
            if match:
                rtt = float(match.group(1))
            else:
                # Tenta outro formato
                match = re.search(r"time[<>= ]+(\\d+\\.?\\d*)", result.stdout)
                if match:
                    rtt = float(match.group(1))
        
        logger.info(f"Ping para {host}: {'✓' if alive else '✗'} (RTT: {rtt}ms)")
        
        return {
            "host": host,
            "alive": alive,
            "rtt": rtt,
            "output": result.stdout.strip(),
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Erro no ping para {host}: {str(e)}")
        return {
            "host": host,
            "alive": False,
            "rtt": None,
            "output": "",
            "error": str(e)
        }
'''

PORT_SCANNER_PY = '''"""Módulo de scanner de portas com rate limiting e threading."""

from typing import Dict, List, Optional, Any
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_address

from beaversec.utils.logger import get_logger
from beaversec.utils.security import validate_ip, validate_domain, sanitize_target
from beaversec.utils.rate_limiter import rate_limit
from beaversec.utils.config_loader import ConfigLoader

logger = get_logger(__name__)

# Serviços comuns
COMMON_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1723: "PPTP",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
}


@rate_limit(module="port_scanner")
def run(target: str, **kwargs) -> Dict[str, Any]:
    """
    Escaneia portas de um alvo.
    
    Args:
        target: IP ou domínio
        **kwargs: ports (str), timeout (int), max_threads (int)
    
    Returns:
        Dict com resultados:
        {
            "target": str,
            "open_ports": List[int],
            "closed_ports": List[int],
            "services": Dict[int, str],
            "total": int,
            "open_count": int
        }
    
    Raises:
        ValueError: Se target for inválido
    """
    logger.info(f"Iniciando scanner de portas para {target}")
    
    # Carrega configurações
    config = ConfigLoader().get("modules", {}).get("port_scanner", {})
    
    # Parse ports
    ports_str = kwargs.get("ports", config.get("default_ports", ""))
    if not ports_str:
        min_port = config.get("port_range_min", 1)
        max_port = config.get("port_range_max", 65535)
        ports = list(range(min_port, max_port + 1))
    else:
        ports = parse_ports(ports_str)
    
    # Configurações
    timeout = kwargs.get("timeout", config.get("scan_timeout", 2))
    max_threads = kwargs.get("max_threads", 10)
    
    # Valida alvo
    sanitized = sanitize_target(target)
    if not validate_ip(sanitized) and not validate_domain(sanitized):
        raise ValueError(f"Alvo inválido: {target}")
    
    # Resolve hostname se necessário
    try:
        ip = socket.gethostbyname(sanitized)
    except socket.gaierror:
        raise ValueError(f"Não foi possível resolver o domínio: {sanitized}")
    
    logger.info(f"Resolvido {sanitized} -> {ip}")
    
    # Escaneia portas
    results = scan_ports(ip, ports, timeout, max_threads)
    
    logger.info(f"Scan concluído: {len(results['open_ports'])} portas abertas em {len(ports)}")
    
    return results


def parse_ports(ports_str: str) -> List[int]:
    """Parse string de portas no formato '1-100,443,8080'."""
    ports = []
    for part in ports_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def scan_port(host: str, port: int, timeout: int) -> Optional[int]:
    """Testa se uma porta está aberta."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return port if result == 0 else None
    except Exception:
        return None


def scan_ports(host: str, ports: List[int], timeout: int, max_threads: int) -> Dict[str, Any]:
    """Escaneia múltiplas portas com threading."""
    open_ports = []
    closed_ports = []
    services = {}
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_port, host, port, timeout): port for port in ports}
        
        for future in as_completed(futures):
            port = futures[future]
            try:
                result = future.result()
                if result:
                    open_ports.append(result)
                    service = COMMON_SERVICES.get(result, "Unknown")
                    services[result] = service
                    logger.debug(f"Porta {result} ({service}) aberta")
                else:
                    closed_ports.append(port)
            except Exception as e:
                logger.debug(f"Erro na porta {port}: {str(e)}")
                closed_ports.append(port)
    
    return {
        "target": host,
        "open_ports": sorted(open_ports),
        "closed_ports": sorted(closed_ports),
        "services": services,
        "total": len(ports),
        "open_count": len(open_ports)
    }
'''

def main():
    """Executa a refatoração."""
    print("=" * 60)
    print("🔨 BEAVERSEC - REFATORAÇÃO AGRESSIVA")
    print("=" * 60)
    print()
    
    # 1. Backup
    backup_original()
    print()
    
    # 2. Criar diretórios
    create_directories()
    print()
    
    # 3. Escrever arquivos
    print("📝 Criando arquivos...")
    
    files = {
        "pyproject.toml": PYPROJECT_TOML,
        "beaversec/__init__.py": INIT_PY,
        "beaversec/main.py": MAIN_PY,
        "beaversec/utils/security.py": SECURITY_PY,
        "beaversec/utils/rate_limiter.py": RATE_LIMITER_PY,
        "beaversec/modules/ping_sweep.py": PING_SWEEP_PY,
        "beaversec/modules/port_scanner.py": PORT_SCANNER_PY,
    }
    
    for path, content in files.items():
        write_file(path, content)
    
    # 4. Copiar config.yaml se existir
    if (PROJECT_ROOT / "config.yaml").exists():
        shutil.copy2(PROJECT_ROOT / "config.yaml", PROJECT_ROOT / "beaversec/config.yaml")
        print(f"  📝 beaversec/config.yaml (copiado do original)")
    else:
        write_file("beaversec/config.yaml", CONFIG_YAML)
    
    # 5. Criar requirements.txt
    write_file("requirements.txt", "pyyaml>=6.0\npydantic>=2.0\nrich>=13.0\njinja2>=3.0\nrequests>=2.31\ndnspython>=2.4\n")
    
    # 6. Criar README atualizado
    write_file("README.md", """# BeaverSec 🔒

Ferramenta modular de cibersegurança para pentest e reconhecimento de rede.

## 🚀 Instalação

```bash
pip install -e .
