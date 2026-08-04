"""Bootstrap utilities for BeaverSec: dependency checks and startup helpers."""
import importlib
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

REQUIRED = [
    "click",
    "pydantic",
    "aiohttp",
    "pyyaml",
    "dnspython",
    "shodan",
    "pysnmp",
    "scapy",
    "cryptography",
    "idna",
    "tenacity",
]


def check_dependencies() -> List[str]:
    """Return a list of missing dependency package names."""
    missing = []
    for pkg in REQUIRED:
        try:
            importlib.import_module(pkg)
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
