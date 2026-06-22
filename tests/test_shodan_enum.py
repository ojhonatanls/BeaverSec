import pytest
from beaversec.modules.shodan_enum import ShodanEnumModule

@pytest.mark.asyncio
async def test_shodan_enum_init():
    m = ShodanEnumModule()
    assert m.name == "shodan_enum"
