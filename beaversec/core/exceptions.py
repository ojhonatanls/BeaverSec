"""Custom exceptions for BeaverSec."""

class BeaverSecError(Exception):
    """Base exception for all BeaverSec errors."""
    pass

class ModuleLoadError(BeaverSecError):
    """Raised when a module fails to load."""
    pass

class ValidationError(BeaverSecError):
    """Raised when input validation fails."""
    pass

class ExecutionError(BeaverSecError):
    """Raised when module execution fails."""
    pass

class ConfigurationError(BeaverSecError):
    """Raised when configuration is invalid."""
    pass