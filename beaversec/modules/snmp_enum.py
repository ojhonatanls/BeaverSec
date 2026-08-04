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
    UsmUserData,
    usmNoAuthProtocol,
    usmHMACSHAAuthProtocol,
    usmAesCfb128Protocol,
)

from beaversec.core.base import BaseModule
from beaversec.core.result import ModuleResult

logger = logging.getLogger(__name__)


class SnmpEnumModule(BaseModule):
    name = "snmp_enum"
    description = "Enumerate basic SNMP information (sysDescr, sysName, interfaces, processes)"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return isinstance(params, dict) and "target" in params and bool(params["target"])

    def _try_get(self, target: str, auth, port: int, oid: str, engine: SnmpEngine):
        iterator = getCmd(
            engine,
            auth,
            UdpTransportTarget((target, port), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            raise RuntimeError(str(errorIndication))
        if errorStatus:
            raise RuntimeError('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
        return {str(vb[0]): vb[1].prettyPrint() for vb in varBinds}

    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        target = params.get("target")
        port = int(params.get("port", 161))
        version = params.get("version", "2c")
        community = params.get("community", "public")
        user = params.get("user")
        auth_key = params.get("auth_key")
        priv_key = params.get("priv_key")

        engine = SnmpEngine()
        result: Dict[str, Any] = {"target": target, "snmp": {}}

        try:
            if version in ("2c", "1", None):
                try:
                    sys_descr = self._try_get(target, CommunityData(community), port, "1.3.6.1.2.1.1.1.0", engine)
                    sys_name = self._try_get(target, CommunityData(community), port, "1.3.6.1.2.1.1.5.0", engine)
                    result["snmp"]["sysDescr"] = sys_descr
                    result["snmp"]["sysName"] = sys_name
                except Exception as e:
                    logger.debug("snmp v2c/v1 get failed: %s", e)

            if user:
                try:
                    auth_proto = usmHMACSHAAuthProtocol if auth_key else usmNoAuthProtocol
                    priv_proto = usmAesCfb128Protocol if priv_key else None
                    usm = UsmUserData(user, auth_key or None, priv_key or None, authProtocol=auth_proto, privProtocol=priv_proto)
                    sys_descr_v3 = self._try_get(target, usm, port, "1.3.6.1.2.1.1.1.0", engine)
                    sys_name_v3 = self._try_get(target, usm, port, "1.3.6.1.2.1.1.5.0", engine)
                    result["snmp"]["v3"] = {"sysDescr": sys_descr_v3, "sysName": sys_name_v3}
                except Exception as e:
                    logger.debug("snmp v3 get failed: %s", e)

            interfaces: List[str] = []
            try:
                for (errInd, errStatus, errIndex, varBinds) in nextCmd(
                    engine,
                    CommunityData(community),
                    UdpTransportTarget((target, port), timeout=2, retries=1),
                    ContextData(),
                    ObjectType(ObjectIdentity("1.3.6.1.2.1.2.2.1.2")),
                    lexicographicMode=False,
                ):
                    if errInd or errStatus:
                        logger.debug("interfaces walk interruption: %s %s", errInd, errStatus)
                        break
                    for varBind in varBinds:
                        interfaces.append(varBind[1].prettyPrint())
                        if len(interfaces) >= 50:
                            break
                    if len(interfaces) >= 50:
                        break
            except Exception as e:
                logger.debug("interfaces walk exception: %s", e)
            result["snmp"]["interfaces"] = interfaces

            processes: List[str] = []
            try:
                for (errInd, errStatus, errIndex, varBinds) in nextCmd(
                    engine,
                    CommunityData(community),
                    UdpTransportTarget((target, port), timeout=2, retries=1),
                    ContextData(),
                    ObjectType(ObjectIdentity("1.3.6.1.2.1.25.4.2.1.2")),
                    lexicographicMode=False,
                ):
                    if errInd or errStatus:
                        logger.debug("processes walk interruption: %s %s", errInd, errStatus)
                        break
                    for varBind in varBinds:
                        processes.append(varBind[1].prettyPrint())
                        if len(processes) >= 200:
                            break
                    if len(processes) >= 200:
                        break
            except Exception as e:
                logger.debug("processes walk exception: %s", e)
            result["snmp"]["processes"] = processes

            return ModuleResult(success=True, data=result)
        except Exception as e:
            logger.exception("snmp_enum failed for %s", target)
            return ModuleResult(success=False, error=str(e))
