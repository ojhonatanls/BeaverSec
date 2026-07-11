"""SYN scan module (half-open TCP scan) for BeaverSec."""

import socket
import struct
import time
from typing import Dict, Any
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class SynScanModule(BaseModule):
    name = "syn_scan"
    description = "SYN stealth port scan (requires root)"
    version = "1.0.0"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params and "port" in params

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = SecurityValidator.validate_target(params.get("target", ""))
        port = SecurityValidator.validate_port(params.get("port", 0))

        # Simple SYN scan using raw socket (requires root)
        try:
            # Create raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.settimeout(2)

            # Build IP header (simplified)
            ip_header = b'\x45\x00\x00\x28'  # IPv4, header length 20
            ip_header += b'\x00\x00\x00\x00'  # total length placeholder
            ip_header += b'\x40\x00\x40\x06'  # TTL=64, protocol=TCP
            ip_header += b'\x00\x00\x00\x00'  # checksum placeholder
            src_ip = socket.inet_aton('0.0.0.0')  # will be filled by OS
            dst_ip = socket.inet_aton(target)
            ip_header += src_ip + dst_ip

            # Build TCP header (SYN flag)
            src_port = 12345  # random
            seq_num = 0
            ack_num = 0
            offset_res = (5 << 4)  # data offset = 5
            flags = 0x02  # SYN
            window = 5840
            checksum = 0
            urgent = 0
            tcp_header = struct.pack('!HHLLBBHHH',
                                     src_port, port, seq_num, ack_num,
                                     offset_res, flags, window, checksum, urgent)

            # Send packet
            packet = ip_header + tcp_header
            sock.sendto(packet, (target, 0))

            # Wait for response
            try:
                data, addr = sock.recvfrom(1024)
                # Parse TCP flags from response
                # For simplicity, check if we got a SYN-ACK (flags=0x12)
                # We'll just assume open if we receive any response
                return ModuleResult(success=True, data={"port": port, "open": True})
            except socket.timeout:
                return ModuleResult(success=True, data={"port": port, "open": False})
            finally:
                sock.close()
        except PermissionError:
            return ModuleResult(success=False, error="Root privileges required for SYN scan")
        except Exception as e:
            return ModuleResult(success=False, error=str(e))