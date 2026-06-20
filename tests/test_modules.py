import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import dns_enum, http_headers, whois_lookup

def test_dns_enum():
    result = dns_enum.run("google.com")
    assert "google.com" in result
    assert "A" in result["google.com"]

def test_http_headers():
    result = http_headers.run("https://google.com")
    assert result is not None
    assert "server" in str(result).lower() or "Server" in result

def test_whois():
    result = whois_lookup.run("google.com")
    assert result is not None
    # Verifica se tem criação ou expiração
    assert hasattr(result, 'creation_date')