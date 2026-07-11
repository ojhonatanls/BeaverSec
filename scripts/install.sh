#!/bin/bash
# BeaverSec Main Installation Script
set -e

echo "BeaverSec Installation"
echo "======================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "[ERROR] Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
echo "[OK] Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt

# Install BeaverSec in editable mode
echo "[INFO] Installing BeaverSec..."
pip install -e .

# Create config directory
CONFIG_DIR="$HOME/.config/beaversec"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    if [ -f "config.example.yaml" ]; then
        cp config.example.yaml "$CONFIG_DIR/config.yaml"
        echo "[INFO] Created config file at $CONFIG_DIR/config.yaml"
    fi
fi

# Create entry point symlink (fallback)
if ! command -v beaversec &> /dev/null; then
    echo "[INFO] Creating symlink for beaversec in /usr/local/bin (may require sudo)..."
    sudo ln -sf "$(pwd)/venv/bin/beaversec" /usr/local/bin/beaversec || echo "[WARN] Could not create symlink"
fi

echo ""
echo "[OK] Installation complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To verify installation:"
echo "  beaversec --help"