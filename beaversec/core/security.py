"""Security context and validation for BeaverSec."""

import os
import hashlib
import re
from typing import Any, Dict, List, Optional, Set
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address

from beaversec.core.exceptions import SecurityException, ValidationError
from beaversec.utils.audit_logger import AuditLogger


class SecurityContext:
    """
    Security context for validating operations and inputs.

    Attributes:
        logger: Audit logger instance
        allowed_networks: Set of allowed network ranges
        blocked_networks: Set of blocked network ranges
        max_targets: Maximum number of targets allowed
        allowed_protocols: Set of allowed protocols
        block_private_networks: Whether to block private networks (configurable)
    """

    def __init__(self, block_private_networks: bool = True):
        """Initialize security context with default policies.
        
        Args:
            block_private_networks: Whether to block private network addresses.
                                   Can be overridden via config.yaml
        """
        self.logger = AuditLogger.get_logger("security")
        self.allowed_networks: Set[str] = set()
        self.block_private_networks = block_private_networks
        
        self.blocked_networks: Set[str] = {
            "0.0.0.0/8",
            "169.254.0.0/16",
            "224.0.0.0/4",
            "240.0.0.0/4",
            "255.255.255.255/32",
        }
        
        # Add private networks to blocked list if configured
        if self.block_private_networks:
            self.blocked_networks.update({
                "10.0.0.0/8",
                "127.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16",
            })
        
        self.max_targets = 1000
        self.allowed_protocols = {"tcp", "udp", "icmp", "http", "https", "dns"}
        self._initialize_from_config()

    def _initialize_from_config(self) -> None:
        """Load security policies from configuration."""
        # TODO: Load from secure config
        pass

    def validate_operation(self, operation: str) -> None:
        """
        Validate if an operation is permitted.

        Args:
            operation: Operation name to validate

        Raises:
            SecurityException: If operation is not permitted
        """
        blocked_operations = {"exec", "eval", "system", "popen", "subprocess"}

        if operation.lower() in blocked_operations:
            self.logger.warning(f"Blocked operation attempted: {operation}")
            raise SecurityException(f"Operation '{operation}' is not permitted")

        self.logger.info(f"Operation validated: {operation}")

    def validate_target(self, target: str) -> bool:
        """
        Validate a target IP or domain.

        Args:
            target: Target to validate

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If target is invalid
            SecurityException: If target is blocked
        """
        # Domain validation
        if self._is_domain(target):
            return self._validate_domain(target)

        # IP validation
        try:
            ip = ip_address(target)
            return self._validate_ip(ip)
        except ValueError:
            raise ValidationError(f"Invalid target format: {target}")

    def _is_domain(self, target: str) -> bool:
        """Check if target looks like a domain name."""
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        )
        return bool(domain_pattern.match(target))

    def _validate_domain(self, domain: str) -> bool:
        """Validate domain name."""
        # Basic domain validation
        if len(domain) > 253:
            raise ValidationError(f"Domain name too long: {domain}")

        # Check for potentially malicious patterns
        malicious_patterns = [
            r'\.\.',  # Double dots
            r'^\.',   # Leading dot
            r'\.$',   # Trailing dot
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, domain):
                raise SecurityException(f"Domain contains invalid pattern: {domain}")

        # Check against blocked domains
        blocked_domains = {"localhost", "127.0.0.1", "::1"}
        if domain.lower() in blocked_domains:
            raise SecurityException(f"Domain is blocked: {domain}")

        return True

    def _validate_ip(self, ip: Any) -> bool:
        """Validate IP address against security policies."""
        # Block loopback addresses
        if ip.is_loopback:
            raise SecurityException(f"Loopback IP address blocked: {ip}")

        # Block multicast addresses
        if ip.is_multicast:
            raise SecurityException(f"Multicast IP address blocked: {ip}")

        # Block unspecified addresses
        if ip.is_unspecified:
            raise SecurityException(f"Unspecified IP address blocked: {ip}")

        # Block private addresses if configured
        if self.block_private_networks and ip.is_private:
            raise SecurityException(f"Private IP address blocked: {ip}")

        # Check against blocked networks
        if isinstance(ip, (IPv4Address, IPv6Address)):
            ip_str = str(ip)
            for network in self.blocked_networks:
                try:
                    if ip_address(ip_str) in ip_network(network, strict=False):
                        raise SecurityException(
                            f"IP {ip} is in blocked network {network}"
                        )
                except ValueError:
                    continue

        return True

    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize parameters.

        Args:
            params: Parameters to validate

        Returns:
            Dict[str, Any]: Sanitized parameters

        Raises:
            ValidationError: If parameters are invalid
        """
        sanitized = {}

        for key, value in params.items():
            if key == "target":
                self.validate_target(str(value))
                sanitized[key] = self._sanitize_string(str(value))
            elif key == "port":
                sanitized[key] = self._validate_ports(value)
            elif key == "output":
                sanitized[key] = self._validate_output_path(str(value))
            else:
                sanitized[key] = self._sanitize_string(str(value))

        return sanitized

    def _validate_ports(self, ports: Any) -> List[int]:
        """Validate and parse port specifications."""
        valid_ports = []

        if isinstance(ports, (int, str)):
            ports = [str(ports)]

        for port in ports:
            try:
                port_num = int(port)
                if 1 <= port_num <= 65535:
                    valid_ports.append(port_num)
                else:
                    raise ValidationError(f"Invalid port: {port_num}")
            except ValueError:
                raise ValidationError(f"Invalid port format: {port}")

        if len(valid_ports) > 100:
            raise ValidationError("Too many ports specified")

        return valid_ports

    def _validate_output_path(self, path: str) -> str:
        """Validate output file path."""
        # Prevent path traversal
        if ".." in path:
            raise SecurityException("Invalid output path: path traversal detected")

        # Check directory exists
        output_dir = os.path.dirname(path)
        if output_dir and not os.path.exists(output_dir):
            raise ValidationError(f"Output directory does not exist: {output_dir}")

        return os.path.normpath(path)

    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input."""
        if not value:
            return ""

        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)

        # Remove shell metacharacters
        shell_metachars = "|;><&$`\\\"'"
        for char in shell_metachars:
            sanitized = sanitized.replace(char, "")

        return sanitized
