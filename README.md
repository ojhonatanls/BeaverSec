# BeaverSec

BeaverSec - Modular Offensive Security (v3.0)

Overview
- Modular scanning framework with BaseModule-based modules.
- New modules in 3.0: syn_scan, udp_scan, arp_scan, os_detection, service_detection, vuln_scanner, ssl_cipher_scan, dns_zone_transfer, shodan_enum, snmp_enum.
- Async I/O with aiohttp, token-bucket rate limiting, proxy / Tor support.

Quickstart
1. Install dependencies:
   pip install -r requirements.txt

2. Edit config.yaml to add API keys (Shodan, SecurityTrails, NVD) and optional proxy settings.

3. Example usage:
   beaversec list
   beaversec run port_scanner 192.0.2.1 -p 22,80,443
   beaversec run subdomain_brute example.com --wordlist common.txt

New features in v3.0
- Rate limiting using token-bucket across modules.
- Proxy and Tor support for HTTP-based modules.
- Cipher enumeration and improved SSL scanning with basic vulnerability heuristics.
- Shodan and SecurityTrails integrations for enrichment.
- Async modules for better performance.

Developer notes
- Modules are registered automatically in beaversec/modules/__init__.py.
- CLI remains backward compatible; older modules exposing execute() are still supported.
- Tests are skeletonized under `tests/` — add assertions and mocks as needed.

Contributing
- Follow PEP8 and include docstrings.
- Run tests with `pytest`.
