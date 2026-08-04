"""Bootstrap utilities for BeaverSec: dependency checks and startup helpers."""
import importlib
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)

# Map pip package names to their importable module names to avoid false positives
PACKAGE_IMPORT_MAP: Dict[str, str] = {
    "click": "click",
    "pydantic": "pydantic",
    "aiohttp": "aiohttp",
    "pyyaml": "yaml",     # pip: pyyaml -> import: yaml
    "dnspython": "dns",   # pip: dnspython -> import: dns
    "shodan": "shodan",
    "pysnmp": "pysnmp",
    "scapy": "scapy",
    "cryptography": "cryptography",
    "idna": "idna",
    "tenacity": "tenacity",
}


def check_dependencies() -> List[str]:
    """Return a list of missing dependency package names."""
    missing = []
    for pkg, import_name in PACKAGE_IMPORT_MAP.items():
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append(pkg)
    return missing


def warn_missing_dependencies():
    """Log a warning if dependencies are missing. Does not raise by default.

    To enforce at startup, set environment variable BEAVERSEC_FAIL_ON_MISSING=1
    """
    missing = check_dependencies()
    if not missing:
        return
    msg = f"Missing dependencies detected: {', '.join(missing)}"
    if os.environ.get("BEAVERSEC_FAIL_ON_MISSING"):
        raise RuntimeError(msg)
    logger.warning(msg)
