# beaversec/modules/snmp_enum.py
"""SNMP enumeration module for BeaverSec."""
import logging
from typing import Dict, Any, List

from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd,
    nextCmd,
)

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult

logger = logging.getLogger(__name__)


class SnmpEnumModule(BaseModule):
    name = "snmp_enum"
    description = "Enumerate basic SNMP information"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return isinstance(params, dict) and "target" in params and bool(params["target"])

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = params.get("target")
        community = params.get("community", "public")
        port = int(params.get("port", 161))

        engine = SnmpEngine()
        result = {"target": target, "snmp": {}}

        try:
            # Get system description
            iterator = getCmd(
                engine,
                CommunityData(community),
                UdpTransportTarget((target, port), timeout=2, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.1.1.0")),
            )
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                result["snmp"]["error"] = str(errorIndication)
            elif errorStatus:
                result["snmp"]["error"] = f"{errorStatus.prettyPrint()} at {errorIndex}"
            else:
                for varBind in varBinds:
                    result["snmp"]["sysDescr"] = str(varBind[1])

            return ModuleResult(success=True, data=result)
        except Exception as e:
            logger.exception("snmp_enum failed for %s", target)
            return ModuleResult(success=False, error=str(e))
