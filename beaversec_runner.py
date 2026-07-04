#!/usr/bin/env python3
"""BeaverSec runner with working modules."""

import sys
import argparse
import importlib
from pathlib import Path


def load_module(module_name):
    """Load a module from modules_working."""
    try:
        module_path = Path(__file__).parent / "beaversec" / "modules_working" / f"{module_name}.py"
        if not module_path.exists():
            return None

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.Module()
    except Exception as e:
        print(f"Error loading module {module_name}: {e}")
        return None


def list_modules():
    """List all available modules."""
    modules_dir = Path(__file__).parent / "beaversec" / "modules_working"
    modules = []
    for py_file in modules_dir.glob("*.py"):
        if py_file.stem != "__init__":
            modules.append(py_file.stem)
    return modules


def main():
    parser = argparse.ArgumentParser(description="BeaverSec - Working Modules")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    list_parser = subparsers.add_parser("list", help="List available modules")
    run_parser = subparsers.add_parser("run", help="Run a module")
    run_parser.add_argument("module", help="Module name")
    run_parser.add_argument("target", help="Target IP or hostname")
    run_parser.add_argument("-p", "--port", type=int, help="Port number (for port_scanner)")

    args = parser.parse_args()

    if args.command == "list":
        modules = list_modules()
        print("\nAvailable Modules:")
        for module in modules:
            mod = load_module(module)
            if mod:
                print(f"  {module:20} - {mod.description}")
        return

    if args.command == "run":
        module = load_module(args.module)
        if not module:
            print(f"Error: Module '{args.module}' not found")
            return

        kwargs = {"target": args.target}
        if args.port:
            kwargs["port"] = args.port

        result = module.run(**kwargs)
        print(result)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
