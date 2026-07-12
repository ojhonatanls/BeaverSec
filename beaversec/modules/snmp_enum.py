import logging
from typing import Dict, Any, List, Optional

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult
from beaversec.utils.security import SecurityValidator

logger = logging.getLogger(__name__)

class SnmpEnumModule(BaseModule):
    """
    Enumerate SNMP information from a target.
    Requires pysnmp library.
    """
    name = "snmp_enum"
    description = "Enumerate SNMP information (requires pysnmp and community string)"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        target = params.get("target")
        if not target:
            return False
        return True

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target: str = params.get("target")
        if not target:
            return ModuleResult(
                success=False,
                error="No target provided. Usage: run snmp_enum <target> [--community public]"
            )

        community = params.get("community", "public")
        port = params.get("port", 161)

        try:
            from pysnmp.hlapi import (
                getCmd, nextCmd, SnmpEngine, CommunityData, UdpTransportTarget,
                ContextData, ObjectType, ObjectIdentity, Integer32, Counter32, Counter64,
                Gauge32, TimeTicks, OctetString, ObjectIdentifier, MibVariable
            )
        except ImportError:
            return ModuleResult(
                success=False,
                error="`pysnmp` library not installed. Please install it with: pip install pysnmp"
            )

        snmp_data = {}
        oids_to_check = [
            ('1.3.6.1.2.1.1.1.0', 'System Description'),
            ('1.3.6.1.2.1.1.3.0', 'System Uptime'),
            ('1.3.6.1.2.1.1.4.0', 'System Contact'),
            ('1.3.6.1.2.1.1.5.0', 'System Name'),
            ('1.3.6.1.2.1.1.6.0', 'System Location'),
            ('1.3.6.1.2.1.25.1.1.0', 'System UpTime (Host)'),
            ('1.3.6.1.2.1.4.21.1.1', 'IP Forwarding'),
            ('1.3.6.1.2.1.6.13.1.1', 'TCP Connections'),
            ('1.3.6.1.2.1.2.2.1.1', 'Interface Count'),
        ]

        iterator = None
        try:
            for oid, desc in oids_to_check:
                error_indication, error_status, error_index, var_binds = getCmd(
                    SnmpEngine(),
                    CommunityData(community, mpModel=1),  # SNMP v2c
                    UdpTransportTarget((target, port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )

                if error_indication:
                    logger.debug(f"SNMP getCmd error for {oid}: {error_indication}")
                    snmp_data[desc] = {"error": str(error_indication)}
                    continue
                elif error_status:
                    logger.debug(f"SNMP error status for {oid}: {error_status.prettyPrint()}")
                    snmp_data[desc] = {"error": error_status.prettyPrint()}
                    continue
                else:
                    for var_bind in var_binds:
                        value = var_bind[1].prettyPrint()
                        snmp_data[desc] = value

            # Try to get interfaces (walk)
            interfaces = []
            error_indication, error_status, error_index, var_binds = nextCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),
                UdpTransportTarget((target, port)),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.2'))
            )

            if error_indication:
                logger.debug(f"SNMP walk error for interfaces: {error_indication}")
            elif error_status:
                logger.debug(f"SNMP walk error status: {error_status.prettyPrint()}")
            else:
                for var_bind in var_binds:
                    interfaces.append(var_bind[1].prettyPrint())
                snmp_data['Interfaces'] = interfaces

            # Try to get running processes (walk)
            processes = []
            error_indication, error_status, error_index, var_binds = nextCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),
                UdpTransportTarget((target, port)),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.25.4.2.1.2'))
            )

            if error_indication:
                logger.debug(f"SNMP walk error for processes: {error_indication}")
            elif error_status:
                logger.debug(f"SNMP walk error status: {error_status.prettyPrint()}")
            else:
                for var_bind in var_binds:
                    processes.append(var_bind[1].prettyPrint())
                snmp_data['Processes'] = processes

        except ImportError:
            return ModuleResult(
                success=False,
                error="`pysnmp` library not installed. Please install it with: pip install pysnmp"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in SNMP module: {e}")
            return ModuleResult(
                success=False,
                error=f"An unexpected error occurred during SNMP enumeration: {e}"
            )

        return ModuleResult(
            success=True,
            data={
                "target": target,
                "community": community,
                "port": port,
                "snmp_data": snmp_data
            },
            metadata={"protocol": "SNMP", "version": "v2c"}
        )