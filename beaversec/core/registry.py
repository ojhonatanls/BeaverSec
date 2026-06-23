"""Module argument registry for BeaverSec.

Provides a centralized way to define module arguments without relying on
dynamic signature inspection. Each module registers its expected parameters.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass


@dataclass
class ModuleArgument:
    """Definition of a module argument."""
    
    name: str
    type: Type = str
    required: bool = False
    default: Any = None
    help: str = ""
    choices: Optional[List[Any]] = None


class ModuleRegistry:
    """Registry for module argument definitions."""
    
    def __init__(self):
        self._registry: Dict[str, List[ModuleArgument]] = {}
    
    def register(self, module_name: str, args: List[ModuleArgument]) -> None:
        """Register module arguments.
        
        Args:
            module_name: Name of the module (e.g., 'port_scanner')
            args: List of ModuleArgument definitions
        """
        self._registry[module_name] = args
    
    def get_args(self, module_name: str) -> List[ModuleArgument]:
        """Get arguments for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            List of ModuleArgument definitions
        """
        return self._registry.get(module_name, [])
    
    def get_all(self) -> Dict[str, List[ModuleArgument]]:
        """Get all registered modules and their arguments.
        
        Returns:
            Dictionary mapping module names to their arguments
        """
        return self._registry.copy()


# Global registry instance
MODULE_ARGS = ModuleRegistry()


# Register built-in modules
MODULE_ARGS.register(
    "port_scanner",
    [
        ModuleArgument(
            name="targets",
            type=list,
            required=True,
            help="List of target IPs or hostnames"
        ),
        ModuleArgument(
            name="ports",
            type=list,
            required=False,
            default=[22, 80, 443, 3306, 5432],
            help="List of ports to scan"
        ),
        ModuleArgument(
            name="scan_type",
            type=str,
            required=False,
            default="connect",
            choices=["connect", "tcp", "syn", "udp"],
            help="Type of port scan to perform"
        ),
        ModuleArgument(
            name="timeout",
            type=float,
            required=False,
            default=2.0,
            help="Timeout per connection attempt in seconds"
        ),
    ]
)

MODULE_ARGS.register(
    "ping_sweep",
    [
        ModuleArgument(
            name="networks",
            type=list,
            required=True,
            help="List of CIDR networks to sweep (e.g., 192.168.1.0/24)"
        ),
        ModuleArgument(
            name="method",
            type=str,
            required=False,
            default="icmp",
            choices=["icmp", "arp"],
            help="Ping sweep method (icmp or arp for local networks)"
        ),
    ]
)

MODULE_ARGS.register(
    "syn_scan",
    [
        ModuleArgument(
            name="targets",
            type=list,
            required=True,
            help="List of target IPs"
        ),
        ModuleArgument(
            name="ports",
            type=list,
            required=False,
            default=[22, 80, 443],
            help="List of ports to scan"
        ),
    ]
)

MODULE_ARGS.register(
    "udp_scan",
    [
        ModuleArgument(
            name="targets",
            type=list,
            required=True,
            help="List of target IPs"
        ),
        ModuleArgument(
            name="ports",
            type=list,
            required=False,
            default=[53, 123, 161, 162],
            help="List of UDP ports to scan"
        ),
    ]
)

MODULE_ARGS.register(
    "dns_enum",
    [
        ModuleArgument(
            name="domains",
            type=list,
            required=True,
            help="List of domain names to enumerate"
        ),
    ]
)

MODULE_ARGS.register(
    "subdomain_brute",
    [
        ModuleArgument(
            name="domains",
            type=list,
            required=True,
            help="List of domain names for subdomain brute force"
        ),
        ModuleArgument(
            name="wordlist",
            type=str,
            required=False,
            help="Path to custom wordlist file"
        ),
    ]
)

MODULE_ARGS.register(
    "ssl_scan",
    [
        ModuleArgument(
            name="targets",
            type=list,
            required=True,
            help="List of target hostnames or IPs with port (host:port)"
        ),
    ]
)

MODULE_ARGS.register(
    "shodan_enum",
    [
        ModuleArgument(
            name="targets",
            type=list,
            required=True,
            help="List of target IPs or domains"
        ),
    ]
)

MODULE_ARGS.register(
    "whois_lookup",
    [
        ModuleArgument(
            name="targets",
            type=list,
            required=True,
            help="List of domains or IP addresses to look up"
        ),
    ]
)
