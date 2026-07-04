"""CLI entrypoint for BeaverSec.

Uses MODULE_ARGS registry for consistent module parameter handling.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List
from ipaddress import ip_address, ip_network

import click

from beaversec.modules import MODULES
from beaversec.config import get_config, check_config
from beaversec.core.registry import MODULE_ARGS
from beaversec.core.logging import setup_logging, set_correlation_id, get_logger
from beaversec.core.exceptions import ModuleError, ConfigError


def validate_port_range(ports: str) -> List[int]:
    """Validate and parse port specifications.
    
    Args:
        ports: Comma-separated port numbers or ranges
        
    Returns:
        List of valid port numbers
        
    Raises:
        ValueError: If ports are invalid
    """
    valid_ports = []
    
    if not ports:
        return valid_ports
    
    for port_spec in ports.split(","):
        port_spec = port_spec.strip()
        if not port_spec:
            continue
            
        try:
            port_num = int(port_spec)
            if not (1 <= port_num <= 65535):
                raise ValueError(f"Port {port_num} out of range (1-65535)")
            valid_ports.append(port_num)
        except ValueError as e:
            raise ValueError(f"Invalid port format: {port_spec}") from e
    
    return valid_ports


def validate_target(target: str) -> str:
    """Validate target as IP address, CIDR network, or hostname.
    
    Args:
        target: Target IP, CIDR network, or hostname
        
    Returns:
        str: The validated target
        
    Raises:
        ValueError: If target format is invalid
    """
    if not target or not target.strip():
        raise ValueError("Target cannot be empty")
    
    target = target.strip()
    
    # Try to parse as IP address
    try:
        ip_address(target)
        return target
    except ValueError:
        pass
    
    # Try to parse as CIDR network
    try:
        ip_network(target, strict=False)
        return target
    except ValueError:
        pass
    
    # Validate as hostname/domain
    hostname_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
        r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    if hostname_pattern.match(target):
        return target
    
    raise ValueError(f"Invalid target format: {target}")


def validate_method(method: str, valid_methods: List[str]) -> str:
    """Validate method against allowed values.
    
    Args:
        method: Method to validate
        valid_methods: List of allowed methods
        
    Returns:
        str: The validated method
        
    Raises:
        ValueError: If method is not in allowed list
    """
    if not method:
        return method
    
    if method not in valid_methods:
        raise ValueError(
            f"Invalid method '{method}'. Allowed: {', '.join(valid_methods)}"
        )
    
    return method


@click.group()
@click.option("--config", "-c", type=click.Path(), default="config.yaml", help="Path to config.yaml")
@click.option("--debug", is_flag=True, default=False, help="Enable debug logging")
@click.option("--json-logs", is_flag=True, default=False, help="Enable JSON structured logs")
@click.option("--log-file", type=click.Path(), default=None, help="Save logs to file")
@click.pass_context
def cli(ctx: click.Context, config: str, debug: bool, json_logs: bool, log_file: str) -> None:
    """BeaverSec - modular offensive security toolkit."""
    
    # Setup logging estruturado
    cid = set_correlation_id()
    level = "DEBUG" if debug else "INFO"
    setup_logging(level=level, json_output=json_logs, log_file=log_file)
    logger = get_logger("beaversec.cli")
    logger.info("Iniciando BeaverSec", extra={"correlation_id": cid})
    
    # Load config
    try:
        cfg = get_config(config)
    except ConfigError as e:
        logger.error(f"Erro de configuração: {e}")
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg
    ctx.obj["debug"] = debug
    ctx.obj["logger"] = logger
    ctx.obj["config_path"] = config


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List available modules with their arguments."""
    click.echo("\n=== Available Modules ===")
    
    module_args = MODULE_ARGS.get_all()
    
    for module_name in sorted(MODULES.keys()):
        click.echo(f"\n[MODULE] {module_name}")
        
        args = module_args.get(module_name, [])
        if not args:
            click.echo("  (no registered arguments)")
            continue
        
        for arg in args:
            required_mark = "*" if arg.required else ""
            default_str = f" [default: {arg.default}]" if arg.default else ""
            click.echo(f"  {required_mark} {arg.name} ({arg.type.__name__}){default_str}")
            if arg.help:
                click.echo(f"      {arg.help}")
            if arg.choices:
                click.echo(f"      choices: {', '.join(str(c) for c in arg.choices)}")


@cli.command()
@click.argument("module_name", type=str)
@click.argument("target", type=str)
@click.option("--ports", "-p", default="", help="Comma separated ports (e.g., 22,80,443)")
@click.option("--method", "-m", default=None, help="Scan method (where applicable)")
@click.option("--output", "-o", default=None, help="Output file (json/csv/html)")
@click.pass_context
def run(ctx: click.Context, module_name: str, target: str, ports: str, method: str | None, output: str | None) -> None:
    """Run a module by name against a target.
    
    Example:
        beaversec run port_scanner 192.168.1.1 -p 22,80,443
        beaversec run ping_sweep 192.168.1.0/24
    """
    logger = ctx.obj.get("logger", get_logger("beaversec.cli"))
    
    # Validate module exists
    if module_name not in MODULES:
        logger.error(f"Módulo '{module_name}' não encontrado")
        click.echo(f"[ERROR] Module '{module_name}' not found.", err=True)
        click.echo(f"Use 'beaversec list' to see available modules.", err=True)
        raise click.Abort()
    
    # Get module arguments definition
    module_args_def = MODULE_ARGS.get_args(module_name)
    if not module_args_def:
        logger.warning(f"Nenhum argumento registrado para '{module_name}'")
        click.echo(f"[WARNING] No registered arguments for '{module_name}'", err=True)
    
    # Validate target argument
    try:
        target = validate_target(target)
    except ValueError as e:
        logger.error(f"Target validation failed: {e}")
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()
    
    # Parse and validate ports
    port_list: List[int] = []
    if ports:
        try:
            port_list = validate_port_range(ports)
        except ValueError as e:
            logger.error(f"Formato de portas inválido: {e}")
            click.echo(f"[ERROR] {e}", err=True)
            raise click.Abort()
    
    # Validate method if provided
    if method:
        valid_methods = ["tcp", "udp", "syn", "ack", "fin", "null"]
        try:
            method = validate_method(method, valid_methods)
        except ValueError as e:
            logger.error(f"Method validation failed: {e}")
            click.echo(f"[ERROR] {e}", err=True)
            raise click.Abort()
    
    # Prepare module arguments
    module_kwargs: Dict[str, Any] = {}
    
    # Build kwargs based on registry definitions
    if module_args_def:
        for arg_def in module_args_def:
            if arg_def.name in ("targets", "target", "domains", "networks"):
                module_kwargs[arg_def.name] = target
            elif arg_def.name == "ports" and port_list:
                module_kwargs["ports"] = port_list
            elif arg_def.name == "method" and method:
                module_kwargs["method"] = method
    else:
        # Fallback
        module_kwargs["target"] = target
        if port_list:
            module_kwargs["ports"] = port_list
        if method:
            module_kwargs["method"] = method
    
    # Instantiate and run module
    try:
        module_cls = MODULES[module_name]
        module = module_cls()
        
        logger.info(f"Executando {module_name} contra {target}")
        click.echo(f"[INFO] Running {module_name} against {target}...")
        
        # Run async
        result = asyncio.run(module.run(**module_kwargs))
        
        logger.info(f"{module_name} concluído com sucesso")
        click.echo(f"[OK] {module_name} completed successfully.")
        click.echo(f"\nResult:")
        click.echo(str(result))
        
        # Save output if requested
        if output:
            try:
                with open(output, "w") as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"\n[OK] Results saved to {output}")
            except Exception as e:
                logger.error(f"Erro ao salvar arquivo: {e}")
                click.echo(f"[ERROR] Error saving output: {e}", err=True)
    
    except ModuleError as e:
        logger.error(f"Erro no módulo: {e}")
        click.echo(f"[ERROR] Module error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        click.echo(f"[ERROR] Unexpected error: {e}", err=True)
        if ctx.obj.get("debug"):
            import traceback
            traceback.print_exc()
        raise click.Abort()


@cli.command()
@click.pass_context
def check(ctx: click.Context) -> None:
    """Check configuration and API connectivity."""
    config_path = ctx.obj.get("config_path", "config.yaml")
    
    click.echo("[INFO] Checking BeaverSec configuration...\n")
    
    results = check_config(config_path)
    
    # Config file
    status = "[OK]" if results["config_file_exists"] else "[ERROR]"
    click.echo(f"{status} Config file exists: {results['config_file_exists']}")
    
    # Config validity
    status = "[OK]" if results["config_valid"] else "[ERROR]"
    click.echo(f"{status} Config is valid: {results['config_valid']}")
    
    # API keys
    if results.get("api_keys_configured"):
        click.echo("\n[INFO] API Keys:")
        for api_key, configured in results["api_keys_configured"].items():
            status = "[OK]" if configured else "[NOT_CONFIGURED]"
            click.echo(f"  {status} {api_key}: {'Configured' if configured else 'Not configured'}")
    
    # Errors
    if results["errors"]:
        click.echo("\n[ERROR] Errors:")
        for error in results["errors"]:
            click.echo(f"  - {error}")
    else:
        click.echo("\n[OK] All checks passed!")


if __name__ == "__main__":
    cli()
