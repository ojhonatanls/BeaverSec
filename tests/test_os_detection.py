import pytest
from beaversec.modules.os_detection import OSDetectionModule

@pytest.mark.asyncio
async def test_os_detection_init():
    m = OSDetectionModule()
    assert m.name == "os_detection"
