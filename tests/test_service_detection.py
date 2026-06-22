import pytest
from beaversec.modules.service_detection import ServiceDetectionModule

@pytest.mark.asyncio
async def test_service_detection_init():
    m = ServiceDetectionModule()
    assert m.name == "service_detection"
