"""CLI argument parser for BeaverSec."""

import argparse


def create_parser():
    """Create the argument parser for BeaverSec CLI."""
    parser = argparse.ArgumentParser(
        prog="beaversec",
        description="BeaverSec - Modular Offensive Security Framework",
        epilog="Use 'beaversec <module> --help' for module-specific help",
    )

    # Subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # List command
    list_parser = subparsers.add_parser("list", help="List available modules")
    list_parser.add_argument(
        "--detailed", "-d", action="store_true", help="Show detailed module information"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about a module")
    info_parser.add_argument("module", help="Module name")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a module")
    run_parser.add_argument("module_name", help="Module name to run")
    run_parser.add_argument("target", help="Target IP, hostname, or CIDR network")
    run_parser.add_argument(
        "-p", "--port", type=int, help="Port number"
    )
    run_parser.add_argument(
        "-f", "--format", default="json", choices=["json", "yaml", "text"], help="Output format"
    )
    run_parser.add_argument(
        "-o", "--output", help="Output file path"
    )
    run_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    return parser
