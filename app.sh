#!/bin/bash

# SnapWiz - The Magical Package Installer
# Application launcher script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set virtual environment path
VENV_DIR="$SCRIPT_DIR/venv"

# Check if virtual environment exists
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run install.sh first to set up the application."
    exit 1
fi

# Run the application
cd "$SCRIPT_DIR"
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py" "$@"
