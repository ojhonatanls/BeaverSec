import pytest
from beaversec.modules.ping_sweep import PingSweepModule

@pytest.mark.asyncio
async def test_ping_sweep_init():
    m = PingSweepModule()
    assert m.name == "ping_sweep"
