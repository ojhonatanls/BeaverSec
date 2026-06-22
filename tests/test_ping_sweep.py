"""tests/test_ping_sweep.py

Unit tests for ping_sweep module using pytest.
"""
from __future__ import annotations

import subprocess
import types
import pytest

from beaversec.modules import ping_sweep


class _CompletedProcess:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_ping_alive(monkeypatch):
    fake = _CompletedProcess(returncode=0, stdout="64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=12.3 ms")

    def fake_run(cmd, capture_output, text, timeout):
        return fake

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = ping_sweep.run("8.8.8.8", timeout=1, count=1)
    assert result["status"] == "success"
    assert result["data"]["rtt"] == 12.3
    assert result["target"] == "8.8.8.8"


def test_ping_timeout(monkeypatch):
    def fake_run(cmd, capture_output, text, timeout):
        raise subprocess.TimeoutExpired(cmd, timeout)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = ping_sweep.run("10.255.255.1", timeout=1)
    assert result["status"] == "error"
    assert "timeout" in result["error"].lower()
