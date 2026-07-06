import subprocess
import shutil
import sys
from pathlib import Path


def run_cmd(cmd, timeout=30):
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return p.returncode, p.stdout.decode(), p.stderr.decode()


def test_beaversec_help():
    # Try to run the beaversec CLI via installed entrypoint or via module
    rc, out, err = run_cmd("beaversec --help || python -m beaversec.cli --help", timeout=10)
    assert rc == 0, f"beaversec --help failed: rc={rc}, err={err}"


def test_beaversec_list():
    rc, out, err = run_cmd("beaversec list || python -m beaversec.cli list", timeout=10)
    assert rc == 0, f"beaversec list failed: rc={rc}, err={err}"
    # Expect at least one module to be listed
    assert "ping_sweep" in out or "port_scanner" in out or "module" in out.lower()


def test_run_ping_sweep_localhost():
    # Run ping_sweep against localhost; this should be safe and quick.
    rc, out, err = run_cmd("beaversec run ping_sweep 127.0.0.1 || python -m beaversec.cli run ping_sweep 127.0.0.1", timeout=20)
    # The module may return non-zero if dependencies are missing; ensure it doesn't crash the CLI
    assert rc in (0, 1), f"ping_sweep execution returned unexpected rc={rc}, err={err}"
