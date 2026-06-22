import pytest
from beaversec.modules.ssl_scan import SSLScanModule

@pytest.mark.asyncio
async def test_ssl_scan_init():
    m = SSLScanModule()
    assert m.name == "ssl_scan"
