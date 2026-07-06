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
    pip_pkg="${pip_pkg#lib}"

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

# Install BeaverSec globally for the current user via pip --user
PIP_ARGS=(--user)
if [ "${1:-}" = "--dev" ]; then
    echo "Installing BeaverSec in editable (dev) mode for current user"
    # Try editable install with --user (may fail on some pip versions), fallback to normal editable
    if ! python3 -m pip install -e . "${PIP_ARGS[@]}"; then
        echo "[WARN] editable --user install failed, trying editable without --user"
        python3 -m pip install -e . || { echo "[ERROR] Failed to install BeaverSec (editable)"; exit 1; }
    fi
else
    echo "Installing BeaverSec for current user"
    if ! python3 -m pip install . "${PIP_ARGS[@]}"; then
        echo "[WARN] user install failed, trying editable install as fallback"
        python3 -m pip install -e . "${PIP_ARGS[@]}" || { echo "[ERROR] Failed to install BeaverSec"; exit 1; }
    fi
fi

# Determine user-local bin directory
USER_BASE=$(python3 -m site --user-base 2>/dev/null || true)
LOCAL_BIN="$HOME/.local/bin"
if [ -n "$USER_BASE" ]; then
    LOCAL_BIN="$USER_BASE/bin"
fi

# Ensure local bin exists
mkdir -p "$LOCAL_BIN"

# Ensure ~/ .local/bin is on PATH
if ! echo ":$PATH:" | grep -q ":$LOCAL_BIN:"; then
    echo "[INFO] $LOCAL_BIN not found in PATH. Adding to ~/.profile"
    if ! grep -q "${LOCAL_BIN}" ~/.profile 2>/dev/null; then
        echo "export PATH=\"\$PATH:$LOCAL_BIN\"" >> ~/.profile
        echo "[INFO] Appended PATH update to ~/.profile. Start a new shell or run 'source ~/.profile' to use beaversec command."
    fi
fi

# Try to locate installed entrypoint
ENTRYPOINT="$LOCAL_BIN/beaversec"
if [ -f "$ENTRYPOINT" ]; then
    echo "[OK] beaversec entrypoint installed at $ENTRYPOINT"
else
    # Try to locate via command -v
    INSTALLED_PATH=$(command -v beaversec || true)
    if [ -n "$INSTALLED_PATH" ]; then
        ENTRYPOINT="$INSTALLED_PATH"
        echo "[OK] beaversec available at $ENTRYPOINT"
    else
        echo "[WARN] beaversec entrypoint not found in $LOCAL_BIN nor in PATH"
    fi
fi

# Copy entrypoint to /usr/local/bin as fallback (best-effort)
if [ -n "$ENTRYPOINT" ] && [ -f "$ENTRYPOINT" ]; then
    if [ ! -w "/usr/local/bin" ]; then
        echo "[INFO] Attempting to copy entrypoint to /usr/local/bin using sudo"
        sudo cp "$ENTRYPOINT" /usr/local/bin/beaversec || true
        sudo chmod 755 /usr/local/bin/beaversec || true
    else
        cp "$ENTRYPOINT" /usr/local/bin/beaversec || true
        chmod 755 /usr/local/bin/beaversec || true
    fi
fi

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
chmod 700 ~/.beaversec || true
chmod 700 ~/.beaversec/credentials || true

# Final message
echo ""
echo "[OK] Installation completed successfully!"
echo ""
echo "To start using BeaverSec, ensure $LOCAL_BIN is in your PATH (a line was added to ~/.profile if it was missing)."
echo "Run: beaversec --help"
echo ""
echo "If 'beaversec' is still not available, open a new shell or run: source ~/.profile"
echo ""
