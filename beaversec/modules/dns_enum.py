import logging
from typing import Dict, Any, Optional

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult
from beaversec.utils.security import SecurityValidator

logger = logging.getLogger(__name__)

class DnsEnumModule(BaseModule):
    """
    Enumerate DNS records for a domain.
    Attempts to retrieve A, AAAA, MX, NS, TXT, SOA, and CNAME records.
    """
    name = "dns_enum"
    description = "Enumerate DNS records (A, AAAA, MX, NS, TXT, SOA, CNAME)"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return SecurityValidator.validate_domain(params.get("target", ""))

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target: str = params.get("target")
        if not target:
            return ModuleResult(
                success=False,
                error="No target provided. Usage: run dns_enum <domain>"
            )

        try:
            import dns.resolver
            import dns.exception
        except ImportError:
            return ModuleResult(
                success=False,
                error="`dnspython` library not installed. Please install it with: pip install dnspython"
            )

        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']

        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(target, record_type, raise_on_no_answer=False)
                if answers.rrset:
                    records[record_type] = [str(r) for r in answers]
                else:
                    records[record_type] = []
            except (dns.resolver.NoResolverConfiguration, dns.resolver.NoNameservers, dns.exception.DNSException) as e:
                records[record_type] = {"error": str(e)}
            except Exception as e:
                logger.error(f"Unexpected error querying {record_type} for {target}: {e}")
                records[record_type] = {"error": "Unexpected error occurred"}

        return ModuleResult(
            success=True,
            data={"target": target, "records": records},
            metadata={"record_types_queried": record_types}
        )