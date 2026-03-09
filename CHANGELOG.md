# Changelog

All notable changes to the **SnapWiz** (formerly Linux Package Installer) project.

## [1.4.0] - 2026-02-09

### Added - Snap & Flatpak Support + Drag-and-Drop + Multi-Language
- 📦 **Extended Package Format Support**
  - Snap package installation (.snap files)
  - Flatpak package installation (.flatpak bundles)
  - Service/daemon status checking for Snap
  - User and system-wide installation for Flatpak
  - Package metadata extraction for all formats
  
- 🎯 **Drag-and-Drop Functionality**
  - Drag package files directly into window
  - Multi-file drag-and-drop support (up to 50 files)
  - Automatic queue addition
  - Smart file validation
  - Visual feedback and notifications
  - Auto-switch to Install tab
  
- ⚙️ **Centralized Configuration System**
  - New `config.py` module for all settings
  - Extracted hardcoded values
  - Easy customization and maintenance
  - Support for new package formats
  - Theme configuration
  - Keyboard shortcut configuration
  - Drag-and-drop settings

- 🌍 **Multi-Language Support** (Internationalization)
  - Support for 6 languages: English, French, German, Spanish, Italian, Russian
  - New `language.py` module with full translation system
  - Language selector in Settings tab
  - 360+ translations (60 keys × 6 languages)
  - Persistent language preference
  - Automatic fallback to English
  - Easy to add new languages
  
### Changed
- 🎨 **UI Updates**: Updated subtitle to mention all four package formats
- 📝 **File Dialog**: Extended to include .snap and .flatpak filters
- 🔧 **Package Handler**: Refactored to use config-based format detection
- 💡 **Status Messages**: Added drag-and-drop hint in main window

### Technical
- Added `config.py` with comprehensive settings
- Enhanced `PackageHandler` with format-agnostic methods
- Implemented `dragEnterEvent` and `dropEvent` in  `MainWindow`
- Added snap and flatpak installation handlers
- Updated imports to include QUrl, QDragEnterEvent, QDropEvent

## [1.3.0] - 2026-02-08

### Added - Security & Verification
- 🔐 **Package Verification System**
  - Automatic integrity checks for all packages
  - GPG signature verification support (.asc/.sig)
  - Manual checksum verification (SHA256/MD5)
  - Comprehensive security settings in Settings tab
- �️ **Safety Features**
  - Blocks installation of corrupted or truncated files
  - Prevents installation if checksums do not match
  - Validates package structure before reducing system risk
- ⚙️ **New Settings**
  - Toggle for integrity checks (Default: On)
  - Toggle for GPG verification (Default: Off)
  - Input fields for manual checksum validation

## [1.2.0] - 2026-02-08

### Added - Batch Operations & Uninstallation
- � **Batch Installation**
  - Install multiple packages sequentially
  - Multi-file selection in file browser
  - Installation Queue management (Add/Remove/Clear)
  - Overall batch progress tracking
  - Automatic error handling and continuation options
- �️ **Uninstallation Feature**
  - New "Uninstall Package" tab
  - Visual list of all installed packages (.deb/.rpm)
  - Real-time search and filtering
  - Filter by package type
  - Multi-select batch uninstallation
- ⚠️ **Safety Logic**
  - Confirmation dialogs for all destructive actions
  - "Cannot be undone" warnings
  - Root privilege escalation for removal (pkexec)

### Changed
- 🔄 **Rebranding**: Application renamed to **SnapWiz**
- 🎨 **UI Overhaul**: Added Uninstall tab, updated Install tab for queues
- 📝 **Documentation**: Added `BATCH_INSTALLATION_GUIDE.md` and `UNINSTALL_GUIDE.md`

## [1.1.0] - 2026-02-08

### Added - Data Management
- 🔍 **Search & Filter History**
  - Real-time search in Installation History
  - Filter by status (Success/Failed)
  - Filter by package type (.deb/.rpm)
  - Date range filtering (implicitly via sorted list)
- 📤 **Export Capabilities**
  - Export history to CSV format
  - Export history to JSON format
  - Backup your installation logs
- 📥 **Import Capabilities**
  - Import history from JSON backups
  - Merge or replace existing history
- 📊 **Enhanced Logging**
  - Improved JSON structure for history data
  - Added more metadata to logs

## [1.0.0-enhanced] - 2026-02-08

### Added - UI/UX Enhancements

#### Icons & Visual Enhancements
- ✨ Emoji icons throughout the interface for better visual guidance
- ✅ Success indicators (green checkmarks) in installation history
- ❌ Failure indicators (red X marks) in installation history
- 📦 Package type indicators on tabs and headers
- 🎨 Color-coded buttons for different actions
- Professional visual hierarchy with consistent iconography

#### Keyboard Shortcuts
- ⌨️ `Ctrl+O` - Open/Browse for package file
- ⌨️ `Ctrl+I` - Install selected package
- ⌨️ `F5` - Refresh installation history
- ⌨️ `Ctrl+Q` - Quit application completely
- ⌨️ `Ctrl+Tab` - Switch between tabs
- ⌨️ Full keyboard navigation support

#### System Tray Integration
- 🔔 Minimize to system tray instead of closing
- 🔔 System tray icon with context menu
- 🔔 Desktop notifications for success/failure

#### Enhanced Progress Indication
- 📊 7-step detailed installation process
- 📊 Smooth progress bar updates
- 📊 Detailed installation log with emoji markers

#### Tooltips & Help System
- 💡 Comprehensive tooltips on all interactive elements
- 💡 Context-sensitive help text

### Fixed
- Fixed "externally-managed-environment" error on modern Linux distros
- Fixed path handling for directories with spaces
- Fixed theme not loading on startup

## [1.0.0] - 2026-02-08 (Initial Release)

### Added
- Core package installation (.deb/.rpm)
- Automatic package manager detection (apt, dnf, yum, zypper)
- Dependency resolution
- Basic GUI with Install/History/Settings tabs
- Installation history logging
- `install.sh` automated setup script

---

## Release Notes - v1.3.0 (SnapWiz)

**SnapWiz v1.3** is a major milestone that transforms the simple "Linux Package Installer" into a full-featured, secure package management suite.

**Key Highlights:**
- **Security**: Verify checksums and signatures before installing.
- **Productivity**: Install dozens of packages at once with Batch Mode.
- **Management**: Uninstall unwanted packages directly from the GUI.
- **Data**: Search, filter, and export your installation history.

**Recommended for**: All users. This update provides critical security features and major workflow improvements.

---

## Upgrade Guide

### From 1.0.0 -> 1.3.0
1. Pull the latest changes.
2. Run `./install.sh` to update dependencies and shortcuts.
3. Your existing history will be preserved and automatically upgraded to the new format if necessary.

---

## Links
- **Documentation**: See `README.md`, `BATCH_INSTALLATION_GUIDE.md`, `UNINSTALL_GUIDE.md`, `VERIFICATION_GUIDE.md`
- **License**: MIT License

**Last Updated**: 2026-02-08
**Current Version**: 1.3.0
