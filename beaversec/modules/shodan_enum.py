import logging
from typing import Dict, Any, Optional

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult
from beaversec.utils.security import SecurityValidator

logger = logging.getLogger(__name__)

class ShodanEnumModule(BaseModule):
    """
    Query Shodan API for host information.
    Requires a Shodan API key in the configuration file.
    """
    name = "shodan_enum"
    description = "Enumerate host information using the Shodan API"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        target = params.get("target")
        if not target:
            return False
        # Could be an IP or a domain
        return True

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target: str = params.get("target")
        if not target:
            return ModuleResult(
                success=False,
                error="No target provided. Usage: run shodan_enum <target>"
            )

        # Load API key from configuration or environment
        try:
            import shodan
        except ImportError:
            return ModuleResult(
                success=False,
                error="`shodan` library not installed. Please install it with: pip install shodan"
            )

        try:
            # This will load the API key from the config file set up by the core
            api_key = self._get_api_key('shodan')
            if not api_key:
                return ModuleResult(
                    success=False,
                    error="Shodan API key not found. Please set it in ~/.config/beaversec/config.yaml"
                )

            api = shodan.Shodan(api_key)

            # Try to query as IP first
            try:
                # Basic IP validation
                import ipaddress
                ip_address = ipaddress.ip_address(target)
                host_info = api.host(str(ip_address))
                return ModuleResult(
                    success=True,
                    data={"target": target, "type": "IP", "info": host_info}
                )
            except ValueError:
                # Not an IP, try to resolve domain
                import dns.resolver
                import dns.exception
                try:
                    answers = dns.resolver.resolve(target, 'A')
                    ip = str(answers[0])
                    host_info = api.host(ip)
                    return ModuleResult(
                        success=True,
                        data={"target": target, "type": "DOMAIN", "resolved_ip": ip, "info": host_info}
                    )
                except (dns.resolver.NoResolverConfiguration, dns.resolver.NoNameservers, dns.exception.DNSException) as e:
                    return ModuleResult(
                        success=False,
                        error=f"Could not resolve domain {target}: {e}"
                    )
            except shodan.exception.APIError as e:
                return ModuleResult(
                    success=False,
                    error=f"Shodan API error: {e}"
                )
            except Exception as e:
                logger.exception(f"Unexpected error in Shodan module: {e}")
                return ModuleResult(
                    success=False,
                    error=f"An unexpected error occurred: {e}"
                )

        except ImportError:
            return ModuleResult(
                success=False,
                error="`shodan` library not installed. Please install it with: pip install shodan"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in Shodan module setup: {e}")
            return ModuleResult(
                success=False,
                error=f"An unexpected error occurred: {e}"
            )