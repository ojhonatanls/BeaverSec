import logging
import random
import time
from typing import Dict, Any, List, Optional

import requests

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult
from beaversec.utils.security import SecurityValidator

logger = logging.getLogger(__name__)

class SubdomainBruteModule(BaseModule):
    """
    Brute force subdomains using a common wordlist.
    """
    name = "subdomain_brute"
    description = "Brute force subdomains using a common wordlist"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        target = params.get("target")
        if not target or not isinstance(target, str):
            return False
        # Optional: validate wordlist path if provided
        return True

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target: str = params.get("target")
        if not target:
            return ModuleResult(
                success=False,
                error="No target domain provided. Usage: run subdomain_brute <domain>"
            )

        # Basic wordlist (can be expanded or loaded from a file)
        common_subdomains = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "webdisk",
            "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "m", "imap", "test",
            "ns", "blog", "pop3", "dev", "www2", "admin", "forum", "news", "vpn", "ns3",
            "mail2", "new", "mysql", "old", "lists", "support", "mobile", "mx", "static",
            "docs", "beta", "shop", "sql", "secure", "demo", "cp", "calendar", "wiki",
            "web", "media", "email", "images", "img", "download", "dns", "piwik", "stats",
            "dashboard", "portal", "manage", "start", "help", "apps", "video", "sip",
            "dns2", "api", "cdn", "mssql", "remote", "server", "ftp2", "stage", "info"
        ]

        # Check if wordlist was provided in params
        wordlist_file = params.get("wordlist")
        subdomains_to_try = common_subdomains

        if wordlist_file:
            try:
                with open(wordlist_file, 'r') as f:
                    loaded_wordlist = [line.strip() for line in f if line.strip()]
                if loaded_wordlist:
                    subdomains_to_try = loaded_wordlist
            except FileNotFoundError:
                logger.warning(f"Wordlist file not found: {wordlist_file}. Using default wordlist.")
            except Exception as e:
                logger.error(f"Error reading wordlist file {wordlist_file}: {e}")

        found_subdomains = []
        checked_count = 0

        logger.info(f"Starting subdomain brute force for {target} with {len(subdomains_to_try)} entries")

        try:
            import requests
        except ImportError:
            return ModuleResult(
                success=False,
                error="`requests` library not installed. Please install it with: pip install requests"
            )

        for sub in subdomains_to_try[:100]:  # Limit to 100 for performance in this example
            full_domain = f"{sub}.{target}"
            checked_count += 1
            try:
                # Try HTTPS first, then HTTP
                for protocol in ['https', 'http']:
                    url = f"{protocol}://{full_domain}"
                    try:
                        # Use a small timeout to avoid hanging
                        response = requests.get(url, timeout=3, allow_redirects=True)
                        # If we get a response, consider it a valid subdomain
                        found_subdomains.append({
                            "subdomain": full_domain,
                            "url": url,
                            "status_code": response.status_code,
                            "content_length": len(response.content)
                        })
                        break  # Break the protocol loop if we found it
                    except requests.exceptions.Timeout:
                        continue  # Try the next protocol
                    except requests.exceptions.ConnectionError:
                        continue  # Try the next protocol
            except Exception as e:
                logger.debug(f"Error checking {full_domain}: {e}")
                continue

            # Simulate a small delay to avoid rate limiting
            if "delay" in params and params["delay"] > 0:
                time.sleep(params["delay"])

        return ModuleResult(
            success=True,
            data={
                "target": target,
                "subdomains_found": found_subdomains,
                "total_checked": checked_count,
                "total_found": len(found_subdomains)
            },
            metadata={"wordlist_size": len(subdomains_to_try)}
        )