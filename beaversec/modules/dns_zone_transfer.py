import logging
from typing import Dict, Any, List

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult
from beaversec.utils.security import SecurityValidator

logger = logging.getLogger(__name__)

class DnsZoneTransferModule(BaseModule):
    """
    Test for DNS zone transfer vulnerability (AXFR).
    """
    name = "dns_zone_transfer"
    description = "Test for DNS zone transfer (AXFR) vulnerability"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return SecurityValidator.validate_domain(params.get("target", ""))

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target: str = params.get("target")
        if not target:
            return ModuleResult(
                success=False,
                error="No target provided. Usage: run dns_zone_transfer <domain>"
            )

        try:
            import dns.zone
            import dns.resolver
            import dns.exception
        except ImportError:
            return ModuleResult(
                success=False,
                error="`dnspython` library not installed. Please install it with: pip install dnspython"
            )

        try:
            # Get NS records for the domain
            ns_servers = []
            try:
                ns_response = dns.resolver.resolve(target, 'NS')
                ns_servers = [str(r).rstrip('.') for r in ns_response]
            except dns.resolver.NoAnswer:
                return ModuleResult(
                    success=False,
                    error="No NS records found for the domain. Cannot test zone transfer."
                )
            except dns.exception.DNSException as e:
                return ModuleResult(
                    success=False,
                    error=f"DNS resolution error: {e}"
                )

            zone_transferred = {}
            for ns in ns_servers:
                try:
                    # Try to perform an AXFR request
                    zone = dns.zone.from_xfr(dns.query.xfr(ns, target))
                    if zone:
                        zone_transferred[ns] = True
                        # Let's keep a sample of records
                        sample_records = [node.to_text() for node in list(zone.nodes.values())[:10]]
                        zone_transferred[f"{ns}_sample"] = sample_records
                    else:
                        zone_transferred[ns] = False
                except (dns.xfr.TransferError, dns.exception.Timeout, ConnectionRefusedError) as e:
                    logger.debug(f"Zone transfer failed for {ns}: {e}")
                    zone_transferred[ns] = False
                except Exception as e:
                    logger.error(f"Unexpected error during zone transfer to {ns}: {e}")
                    zone_transferred[ns] = {"error": "Unexpected error occurred"}

            # Determine if any zone transfer was successful
            zone_transfer_success = any(v is True for v in zone_transferred.values() if isinstance(v, bool))

            return ModuleResult(
                success=True,
                data={
                    "target": target,
                    "zone_transfer_possible": zone_transfer_success,
                    "ns_servers_tested": ns_servers,
                    "details": zone_transferred
                },
                metadata={"vulnerability": "Zone Transfer (AXFR)"}
            )

        except ImportError:
            return ModuleResult(
                success=False,
                error="`dnspython` library not installed. Please install it with: pip install dnspython"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in dns_zone_transfer module: {e}")
            return ModuleResult(
                success=False,
                error=f"An unexpected error occurred: {e}"
            )