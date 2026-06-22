import pytest
from beaversec.modules.http_headers import HTTPHeadersModule

@pytest.mark.asyncio
async def test_http_headers_init():
    m = HTTPHeadersModule()
    assert m.name == "http_headers"
