# beaversec/modules/dns_enum.py
"""DNS enumeration module for BeaverSec."""
import logging
from typing import Dict, Any

import dns.resolver
import dns.exception

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult

logger = logging.getLogger(__name__)


class DnsEnumModule(BaseModule):
    name = "dns_enum"
    description = "Enumerate DNS records for a domain"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return isinstance(params, dict) and "target" in params and bool(params["target"])

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = params.get("target")
        resolver = dns.resolver.Resolver()
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        records: Dict[str, Any] = {}

        try:
            for rtype in record_types:
                try:
                    answers = resolver.resolve(target, rtype)
                    values = [r.to_text() for r in answers]
                    records[rtype] = values
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                    records[rtype] = []
                except dns.exception.Timeout:
                    records[rtype] = []
                except Exception as e:
                    logger.debug("dns_enum: unexpected error for %s %s: %s", target, rtype, e)
                    records[rtype] = []

            return ModuleResult(success=True, data={"target": target, "records": records})
        except Exception as e:
            logger.exception("dns_enum failed for %s", target)
            return ModuleResult(success=False, error=str(e))
