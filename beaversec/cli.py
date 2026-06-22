"""
Interface de linha de comando usando Click.
"""
import sys
import json
import logging
from pathlib import Path

import click
import yaml

from beaversec.core.beaver import Beaver
from beaversec.modules.ping_sweep import PingSweep
from beaversec.modules.port_scanner import PortScanner
from beaversec.modules.dns_enum import DNSEnum
from beaversec.modules.ssl_scan import SSLScan
from beaversec.modules.http_headers import HTTPHeaders
from beaversec.modules.subdomain_brute import SubdomainBrute
from beaversec.modules.traceroute import Traceroute
from beaversec.modules.whois_lookup import WhoisLookup


def load_config(config_file: str) -> dict:
    """Carrega configuração de arquivo YAML."""
    if config_file and Path(config_file).exists():
        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


@click.group()
@click.option("--config", "-c", type=str, help="Arquivo de configuração YAML")
@click.option("--verbose", "-v", is_flag=True, help="Modo verboso")
@click.pass_context
def cli(ctx, config: str, verbose: bool):
    """BeaverSec - Ferramenta de cibersegurança"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = load_config(config) if config else {}
    beaver = Beaver(verbose=verbose)
    # Registra todos os módulos
    for mod in [
        PingSweep(),
        PortScanner(),
        DNSEnum(),
        SSLScan(),
        HTTPHeaders(),
        SubdomainBrute(),
        Traceroute(),
        WhoisLookup(),
    ]:
        beaver.register_module(mod)
    ctx.obj["beaver"] = beaver


@cli.command()
def list():
    """Lista módulos disponíveis"""
    from beaversec.modules import MODULES
    click.echo("📋 Módulos disponíveis:")
    for name, desc in MODULES.items():
        click.echo(f"  - {name:15} - {desc}")


@cli.command()
@click.argument("module")
@click.option("--target", required=True, help="Alvo (IP/domínio/URL)")
@click.option("--threads", "-t", default=10, help="Número de threads")
@click.option("--timeout", default=5.0, help="Timeout em segundos")
@click.option("--rate-limit", default=0.1, help="Delay entre requisições")
@click.option("--proxy", help="Proxy (ex: http://user:pass@host:port)")
@click.option("--output-file", "-o", help="Salva resultado em arquivo")
@click.option("--format", "-f", type=click.Choice(["json", "html", "csv"]), default="json", help="Formato do relatório")
@click.option("--verbose", is_flag=True, help="Logs detalhados")
@click.option("--dry-run", is_flag=True, help="Simula a execução")
@click.pass_context
def run(ctx, module, target, threads, timeout, rate_limit, proxy, output_file, format, verbose, dry_run):
    """Executa um módulo"""
    beaver = ctx.obj["beaver"]
    config = ctx.obj["config"]

    # Configuração: CLI sobrescreve YAML
    threads = threads or config.get("threads", 10)
    timeout = timeout or config.get("timeout", 5.0)
    rate_limit = rate_limit or config.get("rate_limit", 0.1)
    verbose = verbose or config.get("verbose", False)

    if dry_run:
        click.echo(f"[DRY RUN] Executaria {module} em {target}")
        return

    click.echo(f"[+] Executando {module} em {target}...")
    result = beaver.run_module(
        module,
        target,
        threads=threads,
        timeout=timeout,
        rate_limit=rate_limit,
        proxy=proxy,
        verbose=verbose,
    )

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
