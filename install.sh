#!/bin/bash

# Installation script for SnapWiz - The Magical Package Installer
# This script sets up the application and creates a desktop entry

set -e

echo "======================================"
echo "⚡🧙‍♂️ SnapWiz - Setup"
echo "======================================"
echo ""
echo "Install packages in a snap, like a wizard!"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.6 or higher and try again."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if python3-venv is installed
if ! python3 -m venv --help &> /dev/null; then
    echo "⚠ Warning: python3-venv is not installed."
    echo "Installing python3-venv..."
    
    # Try to install venv based on distribution
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-venv
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-venv
    elif command -v pacman &> /dev/null; then
        sudo pacman -S python-virtualenv
    else
        echo "Error: Could not install python3-venv automatically."
        echo "Please install it manually for your distribution."
        exit 1
    fi
fi

echo "✓ python3-venv available"

# Get the current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create virtual environment
VENV_DIR="$INSTALL_DIR/venv"
echo ""
echo "Creating virtual environment..."

if [ -d "$VENV_DIR" ]; then
    echo "⚠ Virtual environment already exists, recreating..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"

if [ $? -eq 0 ]; then
    echo "✓ Virtual environment created at: $VENV_DIR"
else
    echo "✗ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing Python dependencies in virtual environment..."

# Use the venv's pip directly
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Make main.py executable
chmod +x main.py
echo "✓ Made main.py executable"

# Create desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/snapwiz.desktop"
mkdir -p "$HOME/.local/share/applications"

echo ""
echo "Creating desktop entry..."

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=SnapWiz
Comment=Install packages in a snap, like a wizard!
Exec="$VENV_DIR/bin/python" "$INSTALL_DIR/main.py"
Icon=package-x-generic
Terminal=false
Type=Application
Categories=System;PackageManager;
EOF

if [ $? -eq 0 ]; then
    chmod +x "$DESKTOP_FILE"
    echo "✓ Desktop entry created at: $DESKTOP_FILE"
else
    echo "✗ Failed to create desktop entry"
fi

# Create a launcher script in user's bin directory
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

LAUNCHER="$BIN_DIR/snapwiz"

echo ""
echo "Creating launcher script..."

cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# SnapWiz Launcher Script
# This script ensures proper execution from any directory

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect the installation directory
if [ -f "$HOME/.snapwiz/install_path.txt" ]; then
    INSTALL_DIR=$(cat "$HOME/.snapwiz/install_path.txt")
else
    echo "Error: Installation path not found."
    echo "Please reinstall the application using install.sh"
    exit 1
fi

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: Installation directory not found: $INSTALL_DIR"
    echo "Please reinstall the application."
    exit 1
fi

# Set virtual environment path
VENV_DIR="$INSTALL_DIR/venv"

# Check if virtual environment exists
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Error: Virtual environment not found at: $VENV_DIR"
    echo "Please reinstall the application using install.sh"
    exit 1
fi

# Run the application
cd "$INSTALL_DIR"
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/main.py" "$@"
EOF

# Replace placeholder with actual installation directory
sed -i "s|INSTALL_DIR=.*|INSTALL_DIR=\"$INSTALL_DIR\"|" "$LAUNCHER" 2>/dev/null || \
    perl -i -pe "s|INSTALL_DIR=.*|INSTALL_DIR=\"$INSTALL_DIR\"|" "$LAUNCHER"

chmod +x "$LAUNCHER"
echo "✓ Created launcher script at: $LAUNCHER"

# Save installation path for launcher script
mkdir -p "$HOME/.snapwiz"
echo "$INSTALL_DIR" > "$HOME/.snapwiz/install_path.txt"

# Check if .local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠ Warning: $BIN_DIR is not in your PATH"
    echo "Add the following line to your ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Ask if user wants to set up testing
echo ""
echo "======================================"
echo "🧪 Test Setup (Optional)"
echo "======================================"
echo ""
read -p "Do you want to install test dependencies? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing test dependencies..."
    
    # Install test dependencies
    "$VENV_DIR/bin/pip" install coverage pytest pytest-cov
    
    if [ $? -eq 0 ]; then
        echo "✓ Test dependencies installed"
        
        # Ask if user wants to run tests
        echo ""
        read -p "Do you want to run tests now? (y/n) " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "Running tests..."
            echo ""
            
            cd "$INSTALL_DIR"
            "$VENV_DIR/bin/python" -m test.run_tests
            
            TEST_RESULT=$?
            
            if [ $TEST_RESULT -eq 0 ]; then
                echo ""
                echo "✅ All tests passed!"
            else
                echo ""
                echo "⚠ Some tests failed. Check the output above."
            fi
        fi
    else
        echo "✗ Failed to install test dependencies"
    fi
else
    echo "Skipping test setup."
    echo "To run tests later, install dependencies:"
    echo "  $VENV_DIR/bin/pip install coverage pytest pytest-cov"
    echo "Then run:"
    echo "  $VENV_DIR/bin/python -m test.run_tests"
fi

echo ""
echo "======================================"
echo "⚡ Installation Complete! 🧙‍♂️"
echo "======================================"
echo ""
echo "You can now run SnapWiz by:"
echo "  1. Running: $VENV_DIR/bin/python $INSTALL_DIR/main.py"
echo "  2. Running: snapwiz (if ~/.local/bin is in PATH)"
echo "  3. Searching for 'SnapWiz' in your application menu"
echo ""
echo "To run tests:"
echo "  $VENV_DIR/bin/python -m test.run_tests"
echo ""
echo "To view test documentation:"
echo "  cat test/TESTING_GUIDE.md"
echo ""
echo "Note: The application uses a virtual environment at: $VENV_DIR"
echo ""
echo "Enjoy using SnapWiz - Install packages in a snap, like a wizard!"
echo ""
