"""Módulo de segurança - Sanitização e validação de entradas."""

import re
import ipaddress

def validate_ip(ip: str) -> bool:
    """Valida se a string é um IP válido (IPv4 ou IPv6)."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_domain(domain: str) -> bool:
    """Valida se a string é um domínio válido."""
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))

def validate_cidr(cidr: str) -> bool:
    """Valida se a string é um CIDR válido."""
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def sanitize_target(target: str) -> str:
    """Sanitiza o alvo, removendo caracteres potencialmente maliciosos."""
    sanitized = target.strip()
    sanitized = re.sub(r'[;&|$`(){}]', '', sanitized)
    sanitized = re.sub(r'[\\x00-\\x1f\\x7f]', '', sanitized)
    if not sanitized:
        raise ValueError("Alvo vazio após sanitização")
    return sanitized

def validate_target(target: str) -> str:
    """Valida e sanitiza o alvo, determinando seu tipo."""
    sanitized = sanitize_target(target)
    if validate_ip(sanitized):
        return 'ip'
    elif validate_domain(sanitized):
        return 'domain'
    elif validate_cidr(sanitized):
        return 'cidr'
    else:
        raise ValueError(f"Alvo inválido: {target}")