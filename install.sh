#!/bin/bash
# BeaverSec Root Installation Wrapper
# This script handles permissions and delegates to scripts/install.sh

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "BeaverSec Installation Wrapper"
echo "=============================="
echo ""

# Make scripts/install.sh executable
if [ ! -x "$SCRIPT_DIR/scripts/install.sh" ]; then
    echo "[INFO] Setting execute permissions on scripts/install.sh..."
    chmod +x "$SCRIPT_DIR/scripts/install.sh" || { echo "[ERROR] Failed to set permissions"; exit 1; }
    echo "[OK] Permissions set"
fi

# Run the main installation script
echo ""
echo "Running installation script..."
echo ""

if "$SCRIPT_DIR/scripts/install.sh" "$@"; then
    echo ""
    echo "=========================================="
    echo "[OK] BeaverSec Installation Successful!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Verify installation:"
    echo "   beaversec --help"
    echo ""
    echo "3. List available modules:"
    echo "   beaversec list"
    echo ""
    echo "4. Run a module (example):"
    echo "   beaversec run ping_sweep 127.0.0.1"
    echo ""
    exit 0
else
    echo ""
    echo "=========================================="
    echo "[ERROR] Installation Failed!"
    echo "=========================================="
    echo ""
    echo "Please check the error messages above."
    echo ""
    exit 1
fi
