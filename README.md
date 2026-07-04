BeaverSec - Modular Offensive Security
=====================================

What is BeaverSec
-----------------

BeaverSec is a modular offensive security framework designed for reconnaissance,
enumeration, and vulnerability analysis. Built with Python 3.8+, it provides a
plugin-based architecture for conducting security assessments.

Key Features:

- Modular plugin architecture with automatic module discovery
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

Prerequisites: Python 3.8 or later

1. Clone the repository:

    $ git clone https://github.com/ojhonatanls/BeaverSec.git
    $ cd BeaverSec

2. Run the installation script:

    $ ./scripts/install.sh

The script will:
- Check for Python 3.8+
- Create a virtual environment
- Install all dependencies
- Set up the BeaverSec package

3. Activate the virtual environment:

    $ source venv/bin/activate

4. Verify installation:

    $ beaversec --help

How to use
----------

List available modules:

    $ beaversec list

Run a module:

    $ beaversec run ping_sweep 192.168.1.0/24
    $ beaversec run port_scanner 192.168.1.1 -p 22,80,443
    $ beaversec run dns_enum example.com

Save results to file:

    $ beaversec run port_scanner 192.168.1.1 -p 22,80,443 -o results.json

Configuration
--------------

Configuration file: ~/.beaversec/config.yaml

Create this file to customize BeaverSec behavior:

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

Guidelines for contributors:

1. Follow PEP8 style guidelines
2. Add docstrings to all functions and classes
3. Write tests for new modules
4. Use conventional commit messages:
   - fix: for bug fixes
   - feat: for new features
   - docs: for documentation
   - test: for tests

5. Run tests before submitting:

    $ pytest -q

License
-------

MIT License 2024

Maintained by Jhonatan L. Santos (https://github.com/ojhonatanls)
