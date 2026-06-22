"""
Interface de linha de comando usando Click.
"""
import sys
import json
from pathlib import Path

import click

from beaversec.core.beaver import Beaver
from beaversec.modules.ping_sweep import PingSweep
from beaversec.modules.port_scanner import PortScanner
from beaversec.modules.dns_enum import DNSEnum
from beaversec.modules.ssl_scan import SSLScan
from beaversec.modules.http_headers import HTTPHeaders
from beaversec.modules.subdomain_brute import SubdomainBrute
from beaversec.modules.traceroute import Traceroute
from beaversec.modules.whois_lookup import WhoisLookup


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """BeaverSec - Ferramenta de cibersegurança"""
    pass


@cli.command()
def list():
    """Lista módulos disponíveis"""
    modules = {
        "ping_sweep": "Verifica hosts ativos via ICMP",
        "port_scanner": "Escaneia portas TCP abertas",
        "dns_enum": "Enumera registros DNS",
        "ssl_scan": "Analisa certificados SSL/TLS",
        "http_headers": "Analisa headers HTTP de segurança",
        "subdomain_brute": "Descobre subdomínios por brute force",
        "traceroute": "Rastreia a rota até o alvo",
        "whois_lookup": "Consulta WHOIS de domínios",
    }
    click.echo("📋 Módulos disponíveis:")
    for name, desc in modules.items():
        click.echo(f"  - {name:15} - {desc}")


@cli.command()
@click.argument("module")
@click.option("--target", required=True, help="Alvo (IP/domínio/URL)")
@click.option("--args", help="Argumentos extras em formato JSON")
@click.option("--output-file", help="Salva resultado em arquivo")
@click.option("--format", type=click.Choice(["json", "html"]), default="json", help="Formato do relatório")
@click.option("--verbose", is_flag=True, help="Logs detalhados")
@click.option("--timeout", default=5.0, help="Timeout em segundos")
def run(module, target, args, output_file, format, verbose, timeout):
    """Executa um módulo"""
    # Mapeamento de módulos
    module_map = {
        "ping_sweep": PingSweep,
        "port_scanner": PortScanner,
        "dns_enum": DNSEnum,
        "ssl_scan": SSLScan,
        "http_headers": HTTPHeaders,
        "subdomain_brute": SubdomainBrute,
        "traceroute": Traceroute,
        "whois_lookup": WhoisLookup,
    }
    
    if module not in module_map:
        click.echo(f"[-] Módulo '{module}' não encontrado.")
        click.echo("Use 'beaversec list' para ver os módulos disponíveis.")
        sys.exit(1)
    
    # Instancia o orquestrador
    beaver = Beaver(verbose=verbose)
    
    # Registra o módulo
    mod_instance = module_map[module]()
    beaver.register_module(mod_instance)
    
    # Executa
    click.echo(f"[+] Executando {module} em {target}...")
    result = beaver.run_module(module, target, timeout=timeout)
    
    if output_file:
        beaver.export(format, output_file)
        click.echo(f"[+] Resultado salvo em {output_file}")
    
    if result.success:
        click.echo("[+] Sucesso!")
        if verbose:
            click.echo(json.dumps(result.data, indent=2))
    else:
        click.echo(f"[-] Falha: {', '.join(result.errors)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
