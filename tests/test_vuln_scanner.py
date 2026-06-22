import pytest
from beaversec.modules.vuln_scanner import VulnScannerModule

@pytest.mark.asyncio
async def test_vuln_scanner_init():
    m = VulnScannerModule()
    assert m.name == "vuln_scanner"
