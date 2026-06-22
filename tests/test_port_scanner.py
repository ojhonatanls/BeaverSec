import pytest
from beaversec.modules.port_scanner import PortScannerModule

@pytest.mark.asyncio
async def test_port_scanner_init():
    m = PortScannerModule()
    assert m.name == "port_scanner"
