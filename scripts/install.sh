#!/bin/bash
# BeaverSec Installation Script for Unix-like systems

set -e

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

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "[ERROR] Failed to create virtual environment"; exit 1; }
fi

# Upgrade pip using absolute path (no source activation)
echo "Upgrading pip..."
venv/bin/pip install --upgrade pip || { echo "[ERROR] Failed to upgrade pip"; exit 1; }

# Install dependencies
echo "Installing dependencies..."
venv/bin/pip install -r requirements.txt || { echo "[ERROR] Failed to install dependencies"; exit 1; }

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
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
chmod 755 ~/.beaversec
chmod 700 ~/.beaversec/credentials

echo ""
echo "[OK] Installation complete!"
echo ""
echo "To start using BeaverSec:"
echo "  source venv/bin/activate"
echo "  beaversec --help"
echo ""
echo "Or run directly:"
echo "  venv/bin/beaversec --help"
