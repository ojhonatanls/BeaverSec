import pytest
from beaversec.modules.subdomain_brute import SubdomainBruteModule

@pytest.mark.asyncio
async def test_subdomain_brute_init():
    m = SubdomainBruteModule()
    assert m.name == "subdomain_brute"
