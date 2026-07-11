"""Security context tests."""

import pytest

from beaversec.core.security import SecurityContext
from beaversec.core.exceptions import SecurityException, ValidationError


class TestSecurityContext:
    """Test cases for SecurityContext class."""

    @pytest.fixture
    def security_context(self):
        """Create security context for testing."""
        return SecurityContext()

    def test_validate_operation_allowed(self, security_context):
        """Test validating allowed operations."""
        assert security_context.validate_operation("scan")

    def test_validate_operation_blocked(self, security_context):
        """Test validating blocked operations."""
        with pytest.raises(SecurityException):
            security_context.validate_operation("exec")

        with pytest.raises(SecurityException):
            security_context.validate_operation("eval")

        with pytest.raises(SecurityException):
            security_context.validate_operation("subprocess")

    def test_validate_target_valid_ip(self, security_context):
        """Test validating valid IP addresses."""
        assert security_context.validate_target("8.8.8.8") is True
        assert security_context.validate_target("2001:4860:4860::8888") is True

    def test_validate_target_invalid_ip(self, security_context):
        """Test validating invalid IP addresses."""
        with pytest.raises(ValidationError):
            security_context.validate_target("999.999.999.999")

    def test_validate_target_valid_domain(self, security_context):
        """Test validating valid domain names."""
        assert security_context.validate_target("example.com") is True
        assert security_context.validate_target("subdomain.example.com") is True

    def test_validate_target_invalid_domain(self, security_context):
        """Test validating invalid domain names."""
        with pytest.raises(ValidationError):
            security_context.validate_target("invalid..domain")

        with pytest.raises(ValidationError):
            security_context.validate_target(".leading.dot")

    def test_validate_target_private_ip_blocked(self, security_context):
        """Test that private IPs are blocked."""
        with pytest.raises(SecurityException):
            security_context.validate_target("192.168.1.1")

        with pytest.raises(SecurityException):
            security_context.validate_target("10.0.0.1")

        with pytest.raises(SecurityException):
            security_context.validate_target("172.16.0.1")

    def test_validate_target_loopback_blocked(self, security_context):
        """Test that loopback IPs are blocked."""
        with pytest.raises(SecurityException):
            security_context.validate_target("127.0.0.1")

        with pytest.raises(SecurityException):
            security_context.validate_target("::1")

    def test_validate_ports_valid(self, security_context):
        """Test validating valid port specifications."""
        result = security_context._validate_ports("80")
        assert result == [80]

        result = security_context._validate_ports([22, 443])
        assert result == [22, 443]

        result = security_context._validate_ports("1-100")
        # This would need additional parsing for ranges
        # Current implementation handles comma-separated only

    def test_validate_ports_invalid(self, security_context):
        """Test validating invalid port specifications."""
        with pytest.raises(ValidationError):
            security_context._validate_ports(-1)

        with pytest.raises(ValidationError):
            security_context._validate_ports(99999)

    def test_sanitize_string(self, security_context):
        """Test string sanitization."""
        dirty = "hello; rm -rf /"
        clean = security_context._sanitize_string(dirty)
        assert ";" not in clean

        dirty = "test|echo hello"
        clean = security_context._sanitize_string(dirty)
        assert "|" not in clean
        assert "echo" in clean

    def test_validate_params(self, security_context):
        """Test parameter validation."""
        params = {
            "target": "8.8.8.8",
            "port": "80",
            "output": "/tmp/result.json",
        }

        sanitized = security_context.validate_params(params)
        assert sanitized["target"] == "8.8.8.8"
        assert sanitized["port"] == [80]

    def test_validate_params_with_path_traversal(self, security_context):
        """Test validation prevents path traversal."""
        params = {"output": "../../etc/passwd"}

        with pytest.raises(SecurityException):
            security_context.validate_params(params)