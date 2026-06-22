import pytest
from beaversec.modules.arp_scan import ArpScanModule

@pytest.mark.asyncio
async def test_arp_scan_init():
    m = ArpScanModule()
    assert m.name == "arp_scan"
