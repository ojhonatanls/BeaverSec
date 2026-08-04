# beaversec/modules/dns_zone_transfer.py
"""DNS zone transfer (AXFR) module for BeaverSec."""
import logging
from typing import Dict, Any, List

import dns.query
import dns.exception
import dns.zone

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult

logger = logging.getLogger(__name__)


class DnsZoneTransferModule(BaseModule):
    name = "dns_zone_transfer"
    description = "Attempt DNS zone transfer (AXFR) for a domain"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return isinstance(params, dict) and "target" in params and bool(params["target"])

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = params.get("target")
        nameservers: List[str] = params.get("nameservers", [])
        port = int(params.get("port") or 53)

        try:
            if not nameservers:
                try:
                    import dns.resolver
                    ns_answers = dns.resolver.resolve(target, "NS")
                    nameservers = [str(r.target).rstrip(".") for r in ns_answers]
                except Exception:
                    nameservers = []

            results = {}
            for ns in nameservers:
                try:
                    xfr = dns.query.xfr(ns, target, port=port, timeout=10)
                    zone = dns.zone.from_xfr(xfr)
                    if zone is None:
                        results[ns] = {"success": False, "error": "no_zone_returned"}
                        continue
                    records = []
                    for name, node in zone.nodes.items():
                        rdatasets = node.rdatasets
                        for rdataset in rdatasets:
                            for rdata in rdataset:
                                records.append(f"{name}.{target} {rdataset.rdtype} {rdata.to_text()}")
                    results[ns] = {"success": True, "records": records}
                except dns.exception.FormError as e:
                    logger.debug("zone transfer form error %s: %s", ns, e)
                    results[ns] = {"success": False, "error": "form_error"}
                except dns.exception.Timeout:
                    results[ns] = {"success": False, "error": "timeout"}
                except Exception as e:
                    logger.debug("zone transfer failed for %s: %s", ns, e)
                    results[ns] = {"success": False, "error": str(e)}

            if not results:
                return ModuleResult(success=False, error="no_nameservers_found_or_zone_transfer_not_attempted")

            return ModuleResult(success=True, data={"target": target, "results": results})
        except Exception as e:
            logger.exception("dns_zone_transfer failed for %s", target)
            return ModuleResult(success=False, error=str(e))
