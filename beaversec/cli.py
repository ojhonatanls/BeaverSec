"""CLI entrypoint for BeaverSec.

Enhances existing CLI by registering new modules and preserving backward compatibility.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Iterable, List

import click

from beaversec.modules import MODULES
from beaversec.config import get_config

logger = logging.getLogger("beaversec.cli")


@click.group()
@click.option("--config", "-c", type=click.Path(), default="config.yaml", help="Path to config.yaml")
@click.option("--debug", is_flag=True, default=False, help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, config: str, debug: bool) -> None:
    """BeaverSec - modular offensive security toolkit."""
    cfg = get_config(config)
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg


@cli.command()
def list() -> None:
    """List available modules."""
    click.echo("Available modules:")
    for name in sorted(MODULES.keys()):
        click.echo(f" - {name}")


@cli.command()
@click.argument("module_name", type=str)
@click.argument("targets", nargs=-1)
@click.option("--ports", "-p", default="", help="Comma separated ports (e.g., 22,80,443)")
@click.option("--output", "-o", default=None, help="Output file (json/csv/html)")
@click.pass_context
def run(ctx: click.Context, module_name: str, targets: List[str], ports: str, output: str | None) -> None:
    """Run a module by name against given targets."""
    if module_name not in MODULES:
        click.echo(f"Module {module_name} not found. Use `list` to view available modules.")
        raise click.Abort()
    if not targets:
        click.echo("No targets provided.")
        raise click.Abort()

    module_cls = MODULES[module_name]
    # instantiate module (BaseModule signature assumed to accept config)
    module = module_cls(config=ctx.obj.get("config"))

    # parse ports
    port_list: List[int] = []
    if ports:
        port_list = [int(p.strip()) for p in ports.split(",") if p.strip()]

    # maintain backward compatibility: allow sync run and async run
    async def _run_async() -> Any:
        if hasattr(module, "run"):
            res = await module.run(targets=targets, ports=port_list) if "ports" in module.run.__annotations__.get("return", {}) else await module.run(targets, port_list)
            return res
        elif hasattr(module, "execute"):
            # older modules might expose execute(targets, **kwargs)
            if asyncio.iscoroutinefunction(module.execute):
                return await module.execute(targets=targets, ports=port_list)
            else:
                # run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: module.execute(targets, port_list))
        else:
            raise RuntimeError("Module has no run/execute method")

    click.echo(f"Running {module_name} against {len(targets)} target(s)...")
    result = asyncio.run(_run_async())
    # basic printing; exporters will be used in later steps
    click.echo("Result:")
    click.echo(str(result))
