# Linux Package Installer 

A user-friendly GUI application to help new Linux users install `.deb` and `.rpm` packages with ease.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)

## Features

✨ **Simple and Intuitive Interface** - Easy-to-use GUI designed for beginners

📦 **Multi-Format Support** - Works with both `.deb` and `.rpm` packages

📊 **Progress Tracking** - Real-time progress bar and status updates

🔍 **Package Information** - View detailed package metadata before installation

📝 **Installation History** - Keep track of all installed packages

❌ **Error Handling** - Clear error messages and troubleshooting guidance

🔧 **Dependency Resolution** - Automatically handles package dependencies

🌐 **Offline Support** - Works completely offline once installed

📋 **Installation Logs** - Detailed logs for troubleshooting

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

- **Debian/Ubuntu**: `apt` or `dpkg`
- **Fedora**: `dnf`
- **RHEL/CentOS**: `yum` or `dnf`
- **openSUSE**: `zypper`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Srijan-XI/Linux-pi.git
cd Linux-pi
```

### 2. Use a Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with system packages:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PyQt5
```

### 4. Make the Script Executable (Optional)

```bash
chmod +x main.py
```

## Usage

### Running the Application

```bash
python main.py
```

Or if you made it executable:

```bash
./main.py
```

### Installing a Package

1. **Launch the application**
2. **Click "Browse..."** to select your `.deb` or `.rpm` package file
3. **Review the package information** displayed in the info panel
4. **Click "Install Package"** to start the installation
5. **Enter your password** when prompted (required for administrative privileges)
6. **Wait for installation** to complete - progress will be shown in real-time
7. **Check the installation log** for detailed output

### Viewing Installation History

1. Navigate to the **"Installation History"** tab
2. View all previous installation attempts
3. Use the **"Refresh"** button to update the list
4. Use **"Clear History"** to remove all entries (logs will be deleted)

### Settings

Access the **"Settings"** tab to:
- View detected package manager
- Check application version
- Read about the application

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

1. The application automatically tries to resolve dependencies
2. For `.deb` packages, it runs `apt-get install -f` automatically
3. For `.rpm` packages, use DNF or YUM which handle dependencies
4. Manual fix: Run your package manager's fix command in terminal

### Package Information Not Showing

If package information is not displayed:

1. Install the required tools:
   - For `.deb`: `sudo apt install dpkg`
   - For `.rpm`: `sudo dnf install rpm` or `sudo yum install rpm`

## Architecture

The application is built with a modular architecture:

```
├── main.py              # Main application and GUI
├── package_handler.py   # Package validation and installation logic
├── logger.py            # Installation history and logging
└── requirements.txt     # Python dependencies
```

### Main Components

- **MainWindow**: PyQt5-based GUI with tabs for installation, history, and settings
- **PackageHandler**: Detects package manager, validates packages, extracts info, and handles installation
- **InstallLogger**: Manages installation history with JSON-based persistence
- **InstallerThread**: Background thread for non-blocking installations

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

- [ ] Multi-language support (i18n)
- [ ] Package uninstallation feature
- [ ] Batch package installation
- [ ] Package search and download from repositories
- [ ] System repository management
- [ ] Package verification (GPG signatures)
- [ ] Custom theme support (dark mode)
- [ ] Export installation reports
- [ ] Package downgrade capability
- [ ] Flatpak and Snap support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Inspired by the need to make Linux more accessible to beginners
- Thanks to the open-source community

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing [Issues](https://github.com/yourusername/linux-package-installer/issues)
3. Open a new issue with detailed information about your problem

## Author

**Your Development Team**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

**Note**: This application requires administrative privileges to install packages. Always verify package sources before installation to ensure system security.
