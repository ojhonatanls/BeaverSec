import pytest
from beaversec.modules.snmp_enum import SNMPEnumModule

@pytest.mark.asyncio
async def test_snmp_enum_init():
    m = SNMPEnumModule()
    assert m.name == "snmp_enum"
