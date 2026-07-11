#!/usr/bin/env python3
"""BeaverSec runner using entry points for module discovery."""
import sys
import argparse
from importlib.metadata import entry_points
from typing import Dict, Any, Optional

def load_module_by_entrypoint(name: str) -> Optional[Any]:
    """Load a module by its entry point name."""
    eps = entry_points(group="beaversec.modules")
    for ep in eps:
        if ep.name == name:
            try:
                module_class = ep.load()
                # Instantiate the module class
                return module_class()
            except Exception as e:
                print(f"Error loading module '{name}': {e}", file=sys.stderr)
                return None
    return None

def list_modules() -> list:
    """Return list of available module names."""
    eps = entry_points(group="beaversec.modules")
    return [ep.name for ep in eps]

def main() -> None:
    parser = argparse.ArgumentParser(description="BeaverSec - Modules via entry points")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # List command
    subparsers.add_parser("list", help="List available modules")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a module")
    run_parser.add_argument("module", help="Module name")
    run_parser.add_argument("target", help="Target IP or hostname")
    run_parser.add_argument("-p", "--port", type=int, help="Port number (for port_scanner)")
    run_parser.add_argument("-o", "--output", help="Output file for results")

    args = parser.parse_args()

    if args.command == "list":
        modules = list_modules()
        if not modules:
            print("No modules found.")
            return
        print("\nAvailable Modules:")
        for module in modules:
            print(f"  - {module}")
        return

    if args.command == "run":
        mod = load_module_by_entrypoint(args.module)
        if not mod:
            print(f"Error: Module '{args.module}' not found.", file=sys.stderr)
            sys.exit(1)

        # Build parameters dictionary
        params: Dict[str, Any] = {"target": args.target}
        if args.port:
            params["port"] = args.port
        if args.output:
            params["output"] = args.output

        # Execute module
        try:
            if hasattr(mod, "execute"):
                result = mod.execute(params)
            elif hasattr(mod, "run"):
                # Fallback to legacy run method
                result = mod.run(**params)
            else:
                print("Module has no executable method (execute/run).", file=sys.stderr)
                sys.exit(1)
            print(result)
        except Exception as e:
            print(f"Module execution error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()