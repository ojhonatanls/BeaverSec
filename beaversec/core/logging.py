"""Logging configuration for BeaverSec."""

import logging
import sys
from typing import Optional

_logger = None

def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Configure logging for BeaverSec."""
    global _logger
    level = logging.DEBUG if verbose else logging.INFO

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    _logger = logging.getLogger("beaversec")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    if _logger is None:
        setup_logging()
    return logging.getLogger(name or "beaversec")