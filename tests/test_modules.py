import subprocess
from types import SimpleNamespace

from beaversec.modules import ping_sweep, port_scanner
from beaversec.core.base import ModuleResult


def test_ping_fallback_to_system_ping(monkeypatch):
    # Simulate PermissionError when attempting to create raw socket
    def fake_socket(*args, **kwargs):
        raise PermissionError("raw sockets not permitted")

    class FakeProcResult:
        def __init__(self, rc=0):
            self.returncode = rc
            self.stdout = "pong"

    def fake_run(cmd, capture_output=True, text=True, timeout=None):
        return FakeProcResult(rc=0)

    monkeypatch.setattr(ping_sweep.socket, "socket", fake_socket)
    monkeypatch.setattr(ping_sweep.subprocess, "run", fake_run)

    mod = ping_sweep.PingSweepModule()
    res = mod.execute({"target": "8.8.8.8"})
    assert isinstance(res, ModuleResult)
    assert res.success is True
    assert res.data["alive"] is True


def test_ping_raw_socket_success(monkeypatch):
    # Fake socket that returns a reply
    class FakeSocket:
        def __init__(self, *args, **kwargs):
            self.timeout = None
            self.closed = False

        def settimeout(self, t):
            self.timeout = t

        def sendto(self, pkt, addr):
            # no-op
            pass

        def recvfrom(self, bufsize):
            return (b"reply", ("8.8.8.8", 0))

        def close(self):
            self.closed = True

    def fake_socket(*args, **kwargs):
        return FakeSocket()

    monkeypatch.setattr(ping_sweep.socket, "socket", fake_socket)

    mod = ping_sweep.PingSweepModule()
    res = mod.execute({"target": "8.8.8.8"})
    assert isinstance(res, ModuleResult)
    assert res.success is True
    assert res.data["alive"] is True
    assert res.data.get("from")[0] == "8.8.8.8"


def test__scan_port_open_and_closed(monkeypatch):
    # Fake socket object used by _scan_port
    class FakeSock:
        def __init__(self, retcode=0):
            self._ret = retcode
            self.timeout = None
            self.closed = False

        def settimeout(self, t):
            self.timeout = t

        def connect_ex(self, addr):
            return self._ret

        def close(self):
            self.closed = True

    # Open port
    def fake_socket_open(*args, **kwargs):
        return FakeSock(retcode=0)

    monkeypatch.setattr(port_scanner.socket, "socket", fake_socket_open)
    assert port_scanner._scan_port("127.0.0.1", 80) is True

    # Closed port
    def fake_socket_closed(*args, **kwargs):
        return FakeSock(retcode=1)

    monkeypatch.setattr(port_scanner.socket, "socket", fake_socket_closed)
    assert port_scanner._scan_port("127.0.0.1", 22) is False
