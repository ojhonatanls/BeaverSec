import pytest
from beaversec.utils import security


def test_validate_ip():
    assert security.validate_ip("8.8.8.8") is True
    assert security.validate_ip("256.256.256.256") is False


def test_validate_domain_idn():
    # example IDN (中国) encoded as punycode xn--fiq228c
    assert security.validate_domain("xn--fiq228c.com") is True
    assert security.validate_domain("invalid_domain!@#") is False


def test_sanitizar_alvo_rejects_invalid_chars():
    with pytest.raises(ValueError):
        security.sanitizar_alvo("inva lid$")


def test_validar_alvo_returns_type():
    assert security.validar_alvo("8.8.8.8") == "ip"
    assert security.validar_alvo("192.168.0.0/24") == "cidr"
    assert security.validar_alvo("example.com") == "domain"
