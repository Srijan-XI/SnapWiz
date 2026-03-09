# ⚡🧙‍♂️ SnapWiz

**Install packages in a snap, like a wizard!**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

A magical GUI tool to help Linux users easily install `.deb`, `.rpm`, `.snap`, and `.flatpak` packages with a beautiful, modern interface.

## Features

### Core Features

- ✨ **Simple and Intuitive Interface** - Easy-to-use GUI designed for beginners
- 📦 **Multi-Format Support** - Works with `.deb`, `.rpm`, `.snap`, and `.flatpak` packages
- 🎯 **Drag-and-Drop Support** - Simply drag package files into the window to add them to the queue
- ⚙️ **Centralized Configuration** - Easy customization through `config.py`
- 📊 **Detailed Progress Tracking** - 7-step installation process with real-time updates
- 🔍 **Package Information** - View detailed package metadata before installation
- 📝 **Installation History** - Keep track of all installed packages with success/failure indicators
- ❌ **Error Handling** - Clear error messages and troubleshooting guidance
- 🔧 **Dependency Resolution** - System package managers handle dependencies for individual packages (inter-queue dependencies require manual ordering)
- 🌐 **Offline Support** - Works completely offline once installed
- 📋 **Installation Logs** - Detailed logs for troubleshooting

### Enhanced UI/UX Features

- ⌨️ **Keyboard Shortcuts** - Full keyboard support (Ctrl+O, Ctrl+I, F5, Ctrl+Q)
- 🔔 **System Tray Integration** - Minimize to tray with installation notifications
- 💡 **Comprehensive Tooltips** - Helpful guidance on every element
- 🎨 **Light & Dark Themes** - Switch between themes with persistent settings
- 📍 **Visual Progress Steps** - See exactly what's happening during installation
- ✅ **Success/Failure Icons** - Quick visual identification in history
- 🎯 **Professional Design** - Modern, polished interface with emoji indicators

## Screenshots

### Main Installation Interface
The main interface allows you to browse for packages, view package information, and install with a single click.

### Installation History
Track all your package installations with timestamps and status indicators.

## Requirements

- **Python 3.6+**
- **PyQt5**
- **Linux operating system** (Debian/Ubuntu, Fedora, RHEL, CentOS, openSUSE, etc.)
- **Administrative privileges** (for package installation)

### Package Manager Requirements

The application automatically detects your system's package manager:

**Traditional Package Managers:**
- **Debian/Ubuntu**: `apt` or `dpkg`
- **Fedora**: `dnf`
- **RHEL/CentOS**: `yum` or `dnf`
- **openSUSE**: `zypper`

**Universal Package Managers:**
- **Snap**: `snapd` (for `.snap` packages)
  ```bash
  # Install snapd
  sudo apt install snapd  # Debian/Ubuntu
  sudo dnf install snapd  # Fedora
  sudo systemctl enable --now snapd
  ```

- **Flatpak**: `flatpak` (for `.flatpak` packages)
  ```bash
  # Install flatpak
  sudo apt install flatpak  # Debian/Ubuntu
  sudo dnf install flatpak  # Fedora
  ```

## Installation

### Option 1: Quick Install (Recommended)

Use the automated installation script that handles everything for you:

```bash
# Clone the repository
git clone https://github.com/Srijan-XI/SnapWiz.git
cd SnapWiz

# Run the installation script
chmod +x install.sh
./install.sh
```

The `install.sh` script will:
- ✅ Check for Python 3 and pip
- ✅ Install all required dependencies
- ✅ Create a desktop entry for easy access
- ✅ Create a launcher script in `~/.local/bin`
- ✅ Set up the application automatically

After running the script, you can launch the application by:
- Searching for "SnapWiz" in your application menu
- Running `snapwiz` in terminal (if `~/.local/bin` is in your PATH)
- Running `python3 main.py` from the project directory

### Option 2: Manual Installation

If you prefer manual installation or want more control:

#### 1. Clone the Repository

```bash
git clone https://github.com/Srijan-XI/SnapWiz.git
cd SnapWiz
```

#### 2. Use a Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with system packages:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PyQt5
```

#### 4. Make the Script Executable (Optional)

```bash
chmod +x main.py
```

## Usage

### Running the Application

After installation, you can launch the application in several ways:

#### Method 1: From Application Menu (Recommended for Beginners)

1. Open your application menu/launcher
2. Search for "SnapWiz"
3. Click on the icon to launch

#### Method 2: From Terminal (Quick Launch)

If you used the automated installer and `~/.local/bin` is in your PATH:

```bash
snapwiz
```

#### Method 3: From Terminal (Direct Python)

Navigate to the project directory and run:

```bash
# If you used the automated installer
cd ~/path/to/SnapWiz
venv/bin/python main.py
```

Or if you installed manually with a virtual environment:

```bash
cd ~/path/to/SnapWiz
source venv/bin/activate
python main.py
```

#### Method 4: Direct Execution

If you made main.py executable:

```bash
cd ~/path/to/SnapWiz
./main.py
```

### Adding ~/.local/bin to PATH

If the launcher command doesn't work, add `~/.local/bin` to your PATH:

**For Bash (Most Linux distributions):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**For Zsh (Kali Linux, modern Ubuntu, macOS):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For Fish:**
```bash
fish_add_path ~/.local/bin
```

After this, you can run `snapwiz` from anywhere!

### Installing a Package (Step-by-Step Tutorial)

#### First-Time Installation:

1. **Launch the application** using any of the methods above
2. **Click the "Browse..." button** on the Install Package tab
3. **Navigate to your downloaded package file** (usually in ~/Downloads)
4. **Select the `.deb` or `.rpm` file** you want to install
5. **Review the package information** - The app will display:
   - Package name
   - Version
   - Architecture (32-bit/64-bit)
   - Maintainer
   - Description
6. **Click "Install Package"** button (green button)
7. **Enter your password** when prompted - This is required for system changes
8. **Wait for installation** - Watch the progress bar and status messages
9. **Check the result** - A popup will confirm success or show any errors
10. **View the log** - The Installation Log panel shows detailed output

#### Quick Installation (After First Time):

1. Launch app → Browse → Select package → Install → Enter password → Done!

### Viewing Installation History

Track all your package installations:

1. **Click on the "Installation History" tab** (second tab)
2. **View the list** of all packages you've installed
   - ✓ Green checkmark = Successful installation
   - ✗ Red X = Failed installation
   - Each entry shows: Package name and installation date/time
3. **Refresh the list** - Click "Refresh" if you just installed something
4. **Clear history** - Click "Clear History" to remove all entries (permanent!)

### Customizing Settings

Access the **"Settings"** tab (third tab) to customize your experience:

#### Theme Selection

- **Light Theme** (Default) - Clean, bright interface ideal for daytime use
- **Dark Theme** - Easy on the eyes for night-time use or low-light environments

To change theme:
1. Go to Settings tab
2. Under "Appearance", select your preferred theme from dropdown
3. Theme applies instantly and is saved automatically

#### System Information

View detected system configuration:
- **Package Manager** - Shows which package manager is detected (apt, dnf, yum, zypper)
- **Application Version** - Current version of the installer
- **About** - Author and license information

### Common Workflows

#### Workflow 1: Installing Multiple Packages

```
1. Install first package (Browse → Install → Wait)
2. Click "Clear" button to reset
3. Install next package (Browse → Install → Wait)
4. Repeat as needed
5. Check Installation History to verify all installations
```

#### Workflow 2: Checking Before Installing

```
1. Browse to select package
2. Review package information carefully
3. Check if it's the correct version and architecture
4. If correct → Install
5. If wrong → Click "Clear" and select different package
```

#### Workflow 3: Troubleshooting Failed Installation

```
1. If installation fails, check the Installation Log
2. Read the error message carefully
3. Common issues:
   - Missing dependencies → Try installing dependencies first
   - Wrong architecture → Download correct version (32-bit vs 64-bit)
   - Permission denied → Make sure you entered password correctly
4. Check Installation History to see what went wrong
5. Try installing again or check package source
```

### Keyboard Shortcuts

- **Tab** - Navigate between UI elements
- **Enter** - Click focused button
- **Ctrl+Tab** - Switch between tabs
- **Alt+F4** - Close application

### Tips for New Linux Users

1. **Always download packages from official sources** - This ensures security
2. **Check package compatibility** - Make sure it matches your distribution:
   - `.deb` files → Debian, Ubuntu, Linux Mint, Kali
   - `.rpm` files → Fedora, RHEL, CentOS, openSUSE
   - `.snap` files → Universal (requires snapd)
   - `.flatpak` files → Universal (requires flatpak)
3. **Review package info before installing** - Verify it's what you expect
4. **Keep track of installations** - Use the history feature
5. **Read error messages** - They often tell you exactly what's wrong
6. **Make sure you have enough disk space** - Some packages are large
7. **Use dark mode at night** - It's easier on your eyes!
8. **Try drag-and-drop** - It's the fastest way to add packages to the queue!

## ⚠️ Important Notes and Limitations

### Batch Installation Best Practices

**Recommended Maximum**: **20 packages per batch**
- Large batches (>20 packages) may experience performance issues
- For best experience, split large installations into smaller batches
- The application will still work with more, but installation time increases significantly

**What this means:**
```
✅ Good: Install 15 packages in one batch
⚠️ Acceptable: Install 30 packages (may be slower)
❌ Not Recommended: Install 100+ packages at once
```

### Dependency Resolution

**Known Limitation**: Dependencies between queued packages are **not automatically resolved**

**What this means:**
- If Package B depends on Package A, and both are in the queue
- Package B may fail if it's installed before Package A
- **Solution**: Install packages in dependency order, or install dependencies first

**Example:**
```
❌ Wrong Order:
  1. app-plugin.deb (depends on app)
  2. app.deb

✅ Correct Order:
  1. app.deb
  2. app-plugin.deb
```

**Best Practice:**
- Check package dependencies before batch installation
- Order packages manually in the queue (install dependencies first)
- Or use traditional package managers (apt/dnf) which handle dependencies automatically

### Authentication and Password Prompts

**Known Behavior**: Root password may be requested **multiple times** during batch installation

**Why this happens:**
- Linux security policies (OS limitation, not SnapWiz)
- Each package installation requires privilege escalation
- `pkexec`/`sudo` sessions may timeout between packages

**What to expect:**
```
Installing 5 packages:
  Package 1: Password prompt ✓
  Package 2: (may use cached credentials)
  Package 3: Password prompt again ✓
  Package 4: (may use cached credentials)
  Package 5: Password prompt again ✓
```

**Tips:**
- Keep an eye on the installation process
- Be ready to enter your password when prompted
- For large batches, consider using `sudo` with extended timeout
- This is normal behavior and doesn't indicate an error

### Package Format Specific Notes

**Snap Packages:**
- Require `snapd` service to be running
- Local .snap files are installed with `--dangerous` flag (bypasses signature checks)
- First-time snap installation may take longer due to core snap setup

**Flatpak Packages:**
- Only `.flatpak` bundle files are supported (not repository refs)
- User-level installation is attempted first, then system-wide if it fails
- May require runtime dependencies (handled automatically)

**Traditional .deb/.rpm:**
- Dependency resolution handled by system package manager
- May update package databases automatically
- Internet connection may be required for dependencies

## System Integration

### Creating a Desktop Entry (Optional)

Create a desktop launcher for easy access:

```bash
cat > ~/.local/share/applications/package-installer.desktop << EOF
[Desktop Entry]
Name=Linux Package Installer
Comment=Install .deb and .rpm packages easily
Exec=/usr/bin/python3 /path/to/main.py
Icon=package-x-generic
Terminal=false
Type=Application
Categories=System;PackageManager;
EOF
```

Replace `/path/to/main.py` with the actual path to your `main.py` file.

## Troubleshooting

### Permission Denied Errors

If you encounter permission errors:

1. Ensure `pkexec` or `sudo` is installed on your system
2. Make sure you enter the correct password when prompted
3. Check that your user account has sudo privileges

### Package Manager Not Detected

If the package manager is not detected:

1. Ensure you're running a supported Linux distribution
2. Install the appropriate package manager:
   - Debian/Ubuntu: `sudo apt install apt`
   - Fedora: `sudo dnf install dnf`
   - RHEL/CentOS: `sudo yum install yum`

### Dependency Errors

If installation fails due to missing dependencies:

1. **For individual packages**: The system package manager tries to resolve dependencies automatically
2. **For `.deb` packages**: `apt` handles dependencies from repositories
3. **For `.rpm` packages**: `dnf`/`yum` handle dependencies automatically
4. **For batch installations**: Dependencies **between queued packages** are NOT resolved
   - See "Important Notes" section above for details
   - Solution: Order packages manually with dependencies first
5. **Manual fix**: Run your package manager's fix command in terminal
   ```bash
   sudo apt --fix-broken install  # For .deb
   sudo dnf check               # For .rpm
   ```

### Package Information Not Showing

If package information is not displayed:

1. Install the required tools:
   - For `.deb`: `sudo apt install dpkg`
   - For `.rpm`: `sudo dnf install rpm` or `sudo yum install rpm`
   - For `.snap`: `sudo apt install snapd`
   - For `.flatpak`: `sudo apt install flatpak`

## Architecture

The application is built with a modular architecture:

```
├── main.py                    # Main application and GUI
├── requirements.txt           # Python dependencies
└── src/
    ├── config.py              # Centralized configuration and constants
    ├── language.py            # Internationalization (i18n) support
    ├── package_handler.py     # Package validation and installation logic
    ├── logger.py              # Installation history and logging
    ├── exceptions.py          # Custom exception classes
    └── retry_utils.py         # Retry utilities for network operations
```

### Main Components

- **MainWindow**: PyQt5-based GUI with tabs for installation, batch operations, uninstall, history, and settings
- **PackageHandler**: Detects package managers, validates packages (.deb/.rpm/.snap/.flatpak), extracts info, and handles installation
- **InstallLogger**: Manages installation history with JSON-based persistence and export capabilities
- **InstallerThread**: Background thread for non-blocking installations with progress reporting
- **Language**: Manages multi-language support with 6 supported languages (EN, FR, DE, ES, IT, RU)
- **Config**: Centralized configuration management for all application settings

## Security Considerations

- **Elevated Privileges**: The application requires administrative privileges to install packages
- **pkexec**: Uses `pkexec` for secure privilege elevation with GUI authentication
- **Package Validation**: Validates package files before attempting installation
- **Logged Actions**: All installations are logged for audit purposes

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly on different Linux distributions
5. Commit: `git commit -am 'Add your feature'`
6. Push: `git push origin feature/your-feature`
7. Submit a pull request

## Future Enhancements

Planned features for future releases:

- [ ] Package search and download from repositories
- [ ] System repository management  
- [ ] Package downgrade capability
- [ ] Advanced package dependency visualization
- [ ] Scheduled/automated updates
- [ ] Integration with popular software centers

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

Comprehensive documentation is available:

### Core Documentation
- **[Keyboard Shortcuts](docs/KEYBOARD_SHORTCUTS.md)** - Quick reference for all shortcuts
- **[Features & Implementation](docs/FEATURES_AND_IMPLEMENTATION.md)** - Complete feature documentation
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** - Developer reference and contribution guide
- **[Documentation Index](docs/INDEX.md)** - Complete documentation overview

### User Guides
- **[Batch Installation Guide](GUIDE/BATCH_INSTALLATION_GUIDE.md)** - Multi-package installation walkthrough
- **[Uninstall Guide](GUIDE/UNINSTALL_GUIDE.md)** - Package removal instructions
- **[Export/Import Guide](GUIDE/EXPORT_IMPORT_GUIDE.md)** - History backup and restore
- **[Language Support Guide](GUIDE/LANGUAGE_SUPPORT_GUIDE.md)** - Multi-language configuration
- **[Verification Guide](GUIDE/VERIFICATION_GUIDE.md)** - Package integrity verification
- **[Search & Filter Guide](GUIDE/SEARCH_FILTER_GUIDE.md)** - Advanced search features
- **[Error Handling Guide](GUIDE/ERROR_HANDLING_GUIDE.md)** - Troubleshooting common issues

### Project Files
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[Contributing](CONTRIBUTING.md)** - Guidelines for contributors

Visit the [docs folder](docs/) and [GUIDE folder](GUIDE/) for complete documentation.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Inspired by the need to make Linux more accessible to beginners
- Thanks to the open-source community

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [documentation](docs/) folder
3. Search existing [Issues](https://github.com/Srijan-XI/SnapWiz/issues)
4. Open a new issue with detailed information about your problem

## Author

**Srijan-XI**

- GitHub: [@Srijan-XI](https://github.com/Srijan-XI)
- Repository: [SnapWiz](https://github.com/Srijan-XI/SnapWiz)

---

**Note**: This application requires administrative privileges to install packages. Always verify package sources before installation to ensure system security.

