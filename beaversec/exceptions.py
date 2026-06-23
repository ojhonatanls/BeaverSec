"""
BeaverSec Exception Hierarchy.

Provides structured exception types for different error scenarios.
"""


class BeaverSecError(Exception):
    """Base exception for all BeaverSec errors."""
    pass


class ModuleError(BeaverSecError):
    """Exception raised when a module fails during execution."""
    pass


class ConfigError(BeaverSecError):
    """Exception raised when configuration is invalid or missing."""
    pass


class APIError(BeaverSecError):
    """Exception raised when an external API call fails."""
    pass


class ValidationError(BeaverSecError):
    """Exception raised when input validation fails."""
    pass


class TimeoutError(BeaverSecError):
    """Exception raised when an operation times out."""
    pass


class TargetError(BeaverSecError):
    """Exception raised when target validation fails."""
    pass
