"""Pytest configuration and fixtures for BeaverSec tests."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
import pytest

from beaversec.core.base import BaseModule
from beaversec.core.security import SecurityContext
from beaversec.utils.credential_manager import CredentialManager
from beaversec.utils.audit_logger import AuditLogger


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def security_context() -> SecurityContext:
    """Create a security context for testing."""
    return SecurityContext()


@pytest.fixture
def credential_manager() -> CredentialManager:
    """Create a credential manager for testing."""
    return CredentialManager()

@pytest.fixture
def audit_logger() -> AuditLogger:
    """Create an audit logger for testing."""
    return AuditLogger()


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Provide test configuration."""
    return {
        "threads": 5,
        "timeout": 2.0,
        "rate_limit": 50,
        "verbose": False,
        "log_level": "DEBUG",
    }


@pytest.fixture
def valid_targets() -> Dict[str, str]:
    """Provide valid test targets."""
    return {
        "ip": "8.8.8.8",
        "domain": "example.com",
        "localhost": "127.0.0.1",
        "ipv6": "2001:4860:4860::8888",
    }


@pytest.fixture
def invalid_targets() -> Dict[str, str]:
    """Provide invalid test targets."""
    return {
        "invalid_ip": "999.999.999.999",
        "invalid_domain": "invalid..domain",
        "empty": "",
        "shell_injection": "8.8.8.8; rm -rf /",
    }


@pytest.fixture
def mock_module() -> BaseModule:
    """Create a mock module for testing."""

    class MockModule(BaseModule):
        def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success", "params": params}

        def validate_params(self, params: Dict[str, Any]) -> bool:
            return True

    return MockModule()