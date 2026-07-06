#!/bin/bash
# BeaverSec Installation Script for Unix-like systems

set -euo pipefail

echo "BeaverSec Installation"
echo "======================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3.8+ is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "[ERROR] Python 3.8+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "[OK] Found Python $PYTHON_VERSION"

# Make sure this script is executable (best-effort)
if [ -n "${0:-}" ]; then
    chmod +x "$0" 2>/dev/null || true
fi

# Detect package manager
detect_pkg_manager() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_pkg_manager)

install_with_pip_fallback() {
    local pkg="$1"
    # Try to install a python-compatible package via pip as fallback.
    # Strip common prefixes and try reasonable package names.
    local pip_pkg
    pip_pkg="${pkg#python3-}"
    pip_pkg="${pip_pkg#python-}"
    pip_pkg="${pip_pkg#lib}" # best-effort fallback name

    echo "[WARN] Attempting pip fallback for $pkg -> $pip_pkg"
    if command -v python3 >/dev/null 2>&1; then
        python3 -m pip install --user "$pip_pkg" || {
            echo "[WARN] pip fallback failed for $pip_pkg"
        }
    else
        echo "[WARN] pip not available to install $pip_pkg"
    fi
}

install_system_packages() {
    local pkgs=(nmap python3-venv python3-pip git curl whois dnsutils arp-scan)

    case "$PKG_MANAGER" in
        apt)
            echo "[INFO] Using apt to install system dependencies"
            sudo apt-get update -qq || true
            for p in "${pkgs[@]}"; do
                if ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$p"; then
                    echo "[WARN] Package $p failed to install via apt; attempting pip fallback"
                    install_with_pip_fallback "$p"
                fi
            done
            ;;
        dnf)
            echo "[INFO] Using dnf to install system dependencies"
            for p in "${pkgs[@]}"; do
                if ! sudo dnf install -y "$p" -q; then
                    echo "[WARN] Package $p failed to install via dnf; attempting pip fallback"
                    install_with_pip_fallback "$p"
                fi
            done
            ;;
        pacman)
            echo "[INFO] Using pacman to install system dependencies"
            sudo pacman -Sy --noconfirm --needed "${pkgs[@]}" || {
                # pacman doesn't support per-package failure easily; try individually
                for p in "${pkgs[@]}"; do
                    if ! sudo pacman -S --noconfirm --needed "$p"; then
                        echo "[WARN] Package $p failed to install via pacman; attempting pip fallback"
                        install_with_pip_fallback "$p"
                    fi
                done
            }
            ;;
        zypper)
            echo "[INFO] Using zypper to install system dependencies"
            for p in "${pkgs[@]}"; do
                if ! sudo zypper --non-interactive install "$p"; then
                    echo "[WARN] Package $p failed to install via zypper; attempting pip fallback"
                    install_with_pip_fallback "$p"
                fi
            done
            ;;
        *)
            echo "[WARN] No supported package manager detected. Skipping system package installation."
            ;;
    esac
}

# Attempt to install system packages (may prompt for sudo password)
install_system_packages

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "[ERROR] Failed to create virtual environment"; exit 1; }
else
    echo "[OK] Virtual environment already exists"
fi

# Upgrade pip using absolute path (no source activation)
echo "Upgrading pip..."
venv/bin/pip install --upgrade pip || { echo "[ERROR] Failed to upgrade pip"; exit 1; }

# Install dependencies
echo "Installing dependencies..."
venv/bin/pip install -r requirements.txt || { echo "[ERROR] Failed to install dependencies"; exit 1; }

# Install development dependencies if requested
if [ "${1:-}" = "--dev" ]; then
    echo "Installing development dependencies..."
    if [ -f "requirements-dev.txt" ]; then
        venv/bin/pip install -r requirements-dev.txt || { echo "[ERROR] Failed to install dev dependencies"; exit 1; }
    fi
fi

# Install BeaverSec in development mode
echo "Installing BeaverSec..."
venv/bin/pip install -e . || { echo "[ERROR] Failed to install BeaverSec"; exit 1; }

# Create configuration directory
mkdir -p ~/.beaversec
mkdir -p ~/.beaversec/logs
mkdir -p ~/.beaversec/credentials

# Create default configuration
if [ ! -f ~/.beaversec/config.yaml ]; then
    echo "Creating default configuration..."
    if [ -f beaversec/config/templates/config.yaml.template ]; then
        cp beaversec/config/templates/config.yaml.template ~/.beaversec/config.yaml || { echo "[WARNING] Could not copy config template"; }
    fi
fi

# Set permissions
chmod 755 ~/.beaversec || true
chmod 700 ~/.beaversec/credentials || true

echo ""
echo "[OK] Installation completed successfully!"
echo ""
echo "To start using BeaverSec:"
echo "  source venv/bin/activate"
echo "  beaversec --help"
echo ""
echo "Or run directly:"
echo "  venv/bin/beaversec --help"
echo ""
