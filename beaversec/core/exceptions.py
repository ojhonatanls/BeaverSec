"""Custom exception hierarchy for BeaverSec."""

from typing import Optional


class BeaverSecException(Exception):
    """Base exception for all BeaverSec errors."""

    def __init__(self, message: str = "BeaverSec error occurred",
                 details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class ConfigurationError(BeaverSecException):
    """Raised when configuration is invalid or missing."""

    pass


class ModuleNotFoundError(BeaverSecException):
    """Raised when a requested module is not found."""

    pass


class ModuleExecutionError(BeaverSecException):
    """Raised when module execution fails."""

    pass


class ValidationError(BeaverSecException):
    """Raised when input validation fails."""

    pass


class SecurityException(BeaverSecException):
    """Raised for security policy violations."""

    pass


class CredentialError(BeaverSecException):
    """Raised for credential management issues."""

    pass


class RateLimitError(BeaverSecException):
    """Raised when rate limit is exceeded."""

    pass


class NetworkError(BeaverSecException):
    """Raised for network-related errors."""

    pass


class DataError(BeaverSecException):
    """Raised for data processing errors."""

    pass