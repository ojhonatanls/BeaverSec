"""Módulo de segurança - Validação de IP/domínio/CIDR e sanitização (PT-BR names)."""

import re
import ipaddress
import idna
from typing import Tuple

def validate_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_domain(domain: str) -> bool:
    """Validate domain including internationalized names via idna."""
    if not domain or len(domain) > 253:
        return False
    try:
        ace = idna.encode(domain).decode("ascii")
    except idna.IDNAError:
        return False
    # Basic pattern for ACE/Punycode or ASCII labels
    pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')
    return bool(pattern.match(ace))

def validate_cidr(cidr: str) -> bool:
    if '/' not in cidr:
        return False
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def sanitizar_alvo(target: str) -> str:
    """Sanitizador que rejeita caracteres inválidos em vez de removê-los."""
    if not isinstance(target, str) or not target.strip():
        raise ValueError("Alvo vazio")
    # Allow only characters valid for IP, domain, CIDR, and port specs
    if re.search(r"[^0-9A-Za-z\.\-:\/\[\]]", target):
        raise ValueError(f"Alvo contém caracteres inválidos: {target}")
    return target.strip()

def validar_alvo(target: str) -> str:
    """Valida estritamente o alvo e retorna um tipo 'ip'|'domain'|'cidr' ou levanta ValueError."""
    t = sanitizar_alvo(target)
    if validate_ip(t):
        return "ip"
    if validate_cidr(t):
        return "cidr"
    if validate_domain(t):
        return "domain"
    raise ValueError(f"Alvo inválido: {target}")

# Backwards-compatible aliases (English names)
validate_target = validar_alvo
sanitize_target = sanitizar_alvo

# SecurityValidator wrapper (compatibilidade)
class SecurityValidator:
    @staticmethod
    def validate_ip(ip: str) -> bool:
        return validate_ip(ip)
    @staticmethod
    def validate_domain(domain: str) -> bool:
        return validate_domain(domain)
    @staticmethod
    def validate_target(target: str) -> str:
        return validar_alvo(target)
    @staticmethod
    def sanitize_target(target: str) -> str:
        return sanitizar_alvo(target)
