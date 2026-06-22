"""beaversec/utils/output.py

Utility helpers to format and print module results.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

try:
    from rich import print as rich_print
    from rich.console import Console
    from rich.table import Table
    _RICH_AVAILABLE = True
    _console = Console()
except Exception:
    _RICH_AVAILABLE = False


def print_result(result: Dict[str, Any], verbose: bool = False) -> None:
    """Print standardized result to stdout.

    If rich is available, prints a nice table; otherwise falls back to JSON.
    """
    logger = logging.getLogger("BeaverSec")

    if result.get("status") == "error":
        logger.error("Module %s failed for %s: %s", result.get("module_name"), result.get("target"), result.get("error"))

    if _RICH_AVAILABLE:
        table = Table(title=f"Result - {result.get('module_name')} - {result.get('target')}")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("status", str(result.get("status")))
        table.add_row("timestamp", str(result.get("timestamp")))
        if result.get("error"):
            table.add_row("error", str(result.get("error")))
        data = result.get("data")
        if isinstance(data, dict):
            for k, v in data.items():
                table.add_row(k, str(v))
        else:
            table.add_row("data", str(data))
        _console.print(table)
    else:
        if verbose:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            summary = {
                "module": result.get("module_name"),
                "target": result.get("target"),
                "status": result.get("status"),
            }
            print(json.dumps(summary, ensure_ascii=False, indent=2))


def to_json(result: Dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)
