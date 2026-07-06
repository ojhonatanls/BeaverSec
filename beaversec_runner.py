#!/usr/bin/env python3
"""BeaverSec runner adapted to use entry points for module discovery.

This replaces the older modules_working-based runner. It loads modules
registered under the 'beaversec.modules' entry point group.
"""

import sys
import argparse
from importlib.metadata import entry_points, EntryPoint
from typing import Optional


def load_module_by_entrypoint(name: str):
    eps = entry_points(group="beaversec.modules")
    for ep in eps:
        if ep.name == name:
            try:
                obj = ep.load()
                # Expecting a class, instantiate
                return obj()
            except Exception as e:
                print(f"Error loading entry point {name}: {e}")
                return None
    return None


def list_modules():
    eps = entry_points(group="beaversec.modules")
    modules = []
    for ep in eps:
        modules.append(ep.name)
    return modules


def main():
    parser = argparse.ArgumentParser(description="BeaverSec - Modules via entry points")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("list", help="List available modules")
    run_parser = subparsers.add_parser("run", help="Run a module")
    run_parser.add_argument("module", help="Module name")
    run_parser.add_argument("target", help="Target IP or hostname")
    run_parser.add_argument("-p", "--port", type=int, help="Port number (for port_scanner)")

    args = parser.parse_args()

    if args.command == "list":
        modules = list_modules()
        print("\nAvailable Modules:")
        for module in modules:
            print(f"  {module}")
        return

    if args.command == "run":
        mod = load_module_by_entrypoint(args.module)
        if not mod:
            print(f"Error: Module '{args.module}' not found via entry points")
            return

        kwargs = {"target": args.target}
        if args.port:
            kwargs["port"] = args.port

        # Prefer execute(params) if present, else run
        if hasattr(mod, "execute"):
            try:
                result = mod.execute(kwargs)
                print(result)
            except Exception as e:
                print(f"Module execution error: {e}")
        elif hasattr(mod, "run"):
            try:
                result = mod.run(args.target, **({} if not args.port else {"port": args.port}))
                print(result)
            except Exception as e:
                print(f"Module execution error: {e}")
        else:
            print("Module has no executable entrypoint (execute/run)")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
