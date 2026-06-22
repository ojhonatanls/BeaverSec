import pytest
from beaversec.modules.dns_zone_transfer import DNSZoneTransferModule

@pytest.mark.asyncio
async def test_dns_zone_init():
    m = DNSZoneTransferModule()
    assert m.name == "dns_zone_transfer"
