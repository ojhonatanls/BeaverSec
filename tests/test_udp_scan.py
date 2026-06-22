import pytest
from beaversec.modules.udp_scan import UDPScanModule

@pytest.mark.asyncio
async def test_udp_scan_init():
    m = UDPScanModule()
    assert m.name == "udp_scan"
