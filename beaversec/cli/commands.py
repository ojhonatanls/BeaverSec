"""Refactored Click CLI commands with dependency injection and pydantic validation."""
from __future__ import annotations

import sys
from typing import Any, Dict, Optional

import click
from pydantic import BaseModel, ValidationError

from beaversec.core.registry import Registry
from beaversec.core.logging import setup_logging
from beaversec.bootstrap import warn_missing_dependencies
from beaversec.config import load_config


class RunParams(BaseModel):
    module: str
    target: str
    port: Optional[int] = None
    output: Optional[str] = None


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]):
    """BeaverSec - Modular Offensive Security Framework."""
    warn_missing_dependencies()
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["CONFIG"] = load_config(config) if config else {}
    setup_logging(verbose)


@cli.command(name="list")
def list_modules() -> None:
    """List available modules."""
    registry = Registry()
    modules = registry.list_modules()
    if not modules:
        click.echo("No modules found.")
        return
    click.echo("\nAvailable Modules:")
    for name, info in modules.items():
        click.echo(f"  - {name}: {info.get('description', 'No description')}")


@cli.command(name="run")
@click.argument("module")
@click.argument("target")
@click.option("--port", "-p", type=int, help="Port number")
@click.option("--output", "-o", help="Output file")
@click.pass_context
def run_module_cli(ctx: click.Context, module: str, target: str, port: Optional[int], output: Optional[str]) -> None:
    """Run a module against a target with validated params."""
    try:
        params = RunParams(module=module, target=target, port=port, output=output)
    except ValidationError as e:
        click.echo(f"Invalid parameters: {e}", err=True)
        sys.exit(2)

    registry = Registry()
    try:
        result = registry.run_module(params.module, params.model_dump(exclude={"module"}))
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
