import asyncio
import pytest

from beaversec.modules.syn_scan import SynScanModule

@pytest.mark.asyncio
async def test_syn_scan_init():
    m = SynScanModule()
    assert m.name == "syn_scan"
