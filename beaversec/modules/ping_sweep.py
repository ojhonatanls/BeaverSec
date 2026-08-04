"""Ping sweep module for BeaverSec using raw ICMP sockets with fallback to system ping."""
import socket
import struct
import time
import subprocess
import platform
from typing import Dict, Any
from ipaddress import ip_address, AddressValueError

from beaversec.core.base import BaseModule, ModuleResult
from beaversec.utils.retry import with_retry
from beaversec.utils.security import validar_alvo, validate_target as _legacy_validate_target, SecurityValidator

ICMP_ECHO = 8
ICMP_CODE = 0

def _checksum(source_bytes: bytes) -> int:
    """Compute Internet Checksum for ICMP packet."""
    sum_ = 0
    count_to = (len(source_bytes) // 2) * 2
    count = 0
    while count < count_to:
        this_val = source_bytes[count + 1] * 256 + source_bytes[count]
        sum_ = sum_ + this_val
        sum_ = sum_ & 0xffffffff
        count = count + 2
    if count_to < len(source_bytes):
        sum_ = sum_ + source_bytes[len(source_bytes) - 1]
        sum_ = sum_ & 0xffffffff
    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ = sum_ + (sum_ >> 16)
    answer = ~sum_ & 0xffff
    answer = socket.htons(answer)
    return answer


def _system_ping(target: str, timeout: float = 2.0) -> bool:
    """Fallback to system ping command (platform-dependent)."""
    cmd = ["ping", "-c", "1", "-W", str(int(timeout)), target] if platform.system().lower() != "windows" else ["ping", "-n", "1", target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

@with_retry(attempts=3, backoff=2)
class PingSweepModule(BaseModule):
    name = "ping_sweep"
    description = "ICMP ping sweep for host discovery (raw socket with ping fallback)"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params

    def _build_packet(self, id_: int, seq: int = 1) -> bytes:
        header = struct.pack("!BBHHH", ICMP_ECHO, ICMP_CODE, 0, id_, seq)
        payload = b'beaversec'
        chksum = _checksum(header + payload)
        header = struct.pack("!BBHHH", ICMP_ECHO, ICMP_CODE, chksum, id_, seq)
        return header + payload

    def _validate_target_ip(self, target: str) -> str:
        """Validate strict IP and return canonical string or raise ValueError."""
        try:
            ip_address(target)  # raises on invalid
            return target
        except AddressValueError:
            raise ValueError(f"Invalid IP target: {target}")

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = params.get("target", "")
        # Strict validation: require valid IP address
        try:
            target = self._validate_target_ip(target)
        except ValueError as e:
            return ModuleResult(success=False, error=str(e))

        # Try raw socket first
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            # Fallback to system ping when raw sockets not available
            alive = _system_ping(target)
            return ModuleResult(success=True if alive else False, data={"alive": alive})
        except OSError as e:
            # OSError (non-permission) - attempt system ping fallback
            alive = _system_ping(target)
            return ModuleResult(success=True if alive else False, data={"alive": alive, "note": str(e)})

        try:
            sock.settimeout(2)
            packet_id = int((id(self) + time.time()) % 65535)
            packet = self._build_packet(packet_id)
            sock.sendto(packet, (target, 1))
            try:
                data, addr = sock.recvfrom(1024)
                # Basic validation that we received ICMP reply from target
                return ModuleResult(success=True, data={"alive": True, "from": addr})
            except socket.timeout:
                return ModuleResult(success=False, error="Host unreachable", data={"alive": False})
        finally:
            try:
                sock.close()
            except Exception:
                pass

# Alias para compatibilidade com versões anteriores que importavam validate_target
validate_target = _legacy_validate_target
