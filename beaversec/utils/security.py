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
    """Valida se a string é um CIDR válido (deve ter a barra /)."""
    # CIDR DEVE ter a barra /
    if '/' not in cidr:
        return False
    
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def sanitize_target(target: str) -> str:
    """
    Sanitiza o alvo, removendo caracteres potencialmente maliciosos.
    
    Args:
        target: String do alvo (IP, domínio, CIDR)
    
    Returns:
        String sanitizada
    
    Raises:
        ValueError: Se o alvo for inválido
    """
    # Remove espaços extras
    sanitized = target.strip()
    
    # Remove caracteres de controle
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    
    # Remove caracteres que podem ser usados em injeção de comandos
    # Mantém apenas letras, números, pontos, hífens, barras, dois pontos
    sanitized = re.sub(r'[^a-zA-Z0-9.\-:/]', '', sanitized)
    
    # Remove espaços internos
    sanitized = re.sub(r'\s+', '', sanitized)
    
    if not sanitized:
        raise ValueError("Alvo vazio após sanitização")
    
    return sanitized

def validate_target(target: str) -> str:
    """
    Valida e sanitiza o alvo, determinando seu tipo.
    
    Returns:
        str: 'ip', 'domain', 'cidr'
    
    Raises:
        ValueError: Se o alvo for inválido
    """
    sanitized = sanitize_target(target)
    
    # Verifica se é IP (IPv4 ou IPv6)
    if validate_ip(sanitized):
        return 'ip'
    
    # Verifica se é CIDR
    if validate_cidr(sanitized):
        return 'cidr'
    
    # Verifica se é domínio
    if validate_domain(sanitized):
        return 'domain'
    
    raise ValueError(f"Alvo inválido: {target}")
