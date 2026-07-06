BeaverSec - Modular Offensive Security
=====================================

What is BeaverSec
-----------------

BeaverSec is a modular offensive security framework designed for reconnaissance,
enumeration, and vulnerability analysis. Built with Python 3.8+, it provides a
plugin-based architecture for conducting security assessments.

Key Features:

- Modular plugin architecture using setuptools entry points
- Secure input validation and sanitization
- Structured logging with audit trail
- Asynchronous processing for high performance
- Linux-native design (no Windows/macOS-specific code)
- Minimal dependencies using Python standard library extensions

Dependencies
------------

The following packages are required:

- click >= 8.1       - Command-line interface
- pydantic >= 1.10   - Data validation
- aiohttp >= 3.8     - Asynchronous HTTP client
- pyyaml >= 6.0      - YAML configuration parsing
- dnspython >= 2.3   - DNS queries
- shodan >= 1.27     - Shodan API integration
- pysnmp >= 4.4      - SNMP protocol support
- scapy >= 2.4       - Network packet manipulation
- cryptography >= 41.0 - Cryptographic operations
- pytest >= 7.0      - Testing framework

How to install
--------------

Single-command installation (recommended):

    $ curl -sSL https://raw.githubusercontent.com/ojhonatanls/BeaverSec/main/scripts/install.sh | bash

Or clone and run installer (alternate):

    $ git clone https://github.com/ojhonatanls/BeaverSec.git
    $ cd BeaverSec
    $ ./scripts/install.sh

Notes:
- The installer now installs BeaverSec for the current user using `pip --user`.
  It will try to ensure `~/.local/bin` (or the user base bin) is in your PATH
  and will copy the `beaversec` entrypoint to `/usr/local/bin` as a fallback
  (sudo may be required for the latter).
- The installer is non-interactive (except for sudo password prompts) and
  attempts to install required system packages using the native package
  manager when available.

Verify installation:

    $ beaversec --help

Quick Start
-----------

List available modules:

    $ beaversec list

Run a module against a target:

    $ beaversec run ping_sweep 192.168.1.0/24
    $ beaversec run port_scanner 192.168.1.1 -p 22,80,443
    $ beaversec run dns_enum example.com

Save results to file:

    $ beaversec run port_scanner 192.168.1.1 -p 22,80,443 -o results.json

Runner
------

The project ships a small runner script `beaversec_runner.py` that can be used as
an alternative to the `beaversec` entry point. The runner has been adapted to
load modules via setuptools entry points (group `beaversec.modules`). Prefer the
`beaversec` command when available.

Configuration
--------------

Configuration file (XDG): ~/.config/beaversec/config.yaml

Create this file to customize BeaverSec behavior (or use environment variables):

    # API Keys
    shodan:
      api_key: "YOUR_SHODAN_API_KEY"

    # Behavior
    timeout: 30
    max_threads: 10

    # Security
    block_private_networks: true

Available Modules
-----------------

- ping_sweep        - Host discovery via ICMP/ARP
- port_scanner      - TCP port scanning with service detection
- syn_scan          - Stealth SYN scan
- udp_scan          - UDP port scanning
- dns_enum          - DNS record enumeration
- dns_zone_transfer - DNS zone transfer testing
- subdomain_brute   - Subdomain brute force
- ssl_scan          - SSL/TLS certificate analysis
- ssl_cipher_scan   - SSL/TLS cipher enumeration
- http_headers      - HTTP security header analysis
- whois_lookup      - WHOIS domain/IP lookup
- shodan_enum       - Shodan API data enrichment
- vuln_scanner      - Vulnerability scanning
- service_detection - Service identification via banner grabbing
- os_detection      - Operating system fingerprinting
- snmp_enum         - SNMP enumeration

Contributing
------------

Guide for adding new modules:

1. Create a new Python file under `beaversec/modules/` implementing a class that
   inherits from `beaversec.core.base.BaseModule`.
2. Implement `validate_params(self, params)` and `execute(self, params)` on the
   class. Older modules that expose `run(target, **kwargs)` are still supported
   by the runner for backward compatibility.
3. Register the module in `pyproject.toml` under the entry-point group
   `[project.entry-points."beaversec.modules"]`:

   ping_sweep = "beaversec.modules.ping_sweep:PingSweepModule"

4. Test by installing the package in editable mode and running the CLI:

    $ pip install -e . --user
    $ beaversec list
    $ beaversec run <module> <target>

5. Open a PR with your changes.

Testing
-------

Run unit tests:

    $ pytest -q

Integration tests are located under `tests/integration/` and are executed by the
CI integration matrix.

Troubleshooting
---------------

If `beaversec` is not in PATH after installation, start a new shell or run
`source ~/.profile` (the installer attempts to add `~/.local/bin` to your PATH).

License
-------

MIT License 2024

Maintained by Jhonatan L. Santos (https://github.com/ojhonatanls)
