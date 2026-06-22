import pytest
from beaversec.modules.ssl_cipher_scan import SSLCipherScanModule

@pytest.mark.asyncio
async def test_ssl_cipher_init():
    m = SSLCipherScanModule()
    assert m.name == "ssl_cipher_scan"
