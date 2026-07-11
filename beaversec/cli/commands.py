"""Click commands for BeaverSec CLI."""

from __future__ import annotations

import sys
import click

# Imports internos
from beaversec.core.registry import Registry
from beaversec.core.logging import setup_logging
from beaversec.config import load_config   # se não existir, veja nota abaixo

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", help="Path to config file")
@click.pass_context
def cli(ctx, verbose, config):
    """BeaverSec - Modular Offensive Security Framework."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["CONFIG"] = load_config(config) if config else {}
    setup_logging(verbose)

@cli.command()
def list():
    """List available modules."""
    registry = Registry()
    modules = registry.list_modules()
    if not modules:
        click.echo("No modules found.")
        return
    click.echo("\nAvailable Modules:")
    for name, info in modules.items():
        click.echo(f"  - {name}: {info.get('description', 'No description')}")

@cli.command()
@click.argument("module")
@click.argument("target")
@click.option("--port", "-p", type=int, help="Port number")
@click.option("--output", "-o", help="Output file")
@click.pass_context
def run(ctx, module, target, port, output):
    """Run a module against a target."""
    registry = Registry()
    params = {"target": target}
    if port:
        params["port"] = port
    if output:
        params["output"] = output

    try:
        result = registry.run_module(module, params)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()