"""Security validation utilities for BeaverSec."""

import re
import ipaddress
from typing import Union

class SecurityValidator:
    """Validate and sanitize user inputs to prevent injection and path traversal."""

    @staticmethod
    def validate_target(target: str) -> str:
        """Validate and sanitize a target IP or hostname."""
        # Check if it's a valid IP or hostname
        try:
            ipaddress.ip_address(target)
            return target
        except ValueError:
            pass

        # Simple hostname validation (alphanumeric, dots, hyphens)
        if re.match(r'^[a-zA-Z0-9.-]+$', target):
            return target

        raise ValueError(f"Invalid target: {target}")

    @staticmethod
    def validate_port(port: Union[int, str]) -> int:
        """Validate and sanitize a port number."""
        try:
            port_int = int(port)
            if 1 <= port_int <= 65535:
                return port_int
        except (ValueError, TypeError):
            pass
        raise ValueError(f"Invalid port: {port}")

    @staticmethod
    def sanitize_path(path: str) -> str:
        """Prevent path traversal attacks."""
        # Remove any '..' and leading/trailing slashes
        sanitized = re.sub(r'\.\./', '', path)
        sanitized = sanitized.lstrip('/')
        return sanitized