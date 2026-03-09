# SnapWiz Development Guide

**Version:** 1.4.0  
**Last Updated:** 2026-02-09  
**For Developers and Contributors**

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Roadmap](#development-roadmap)
3. [Release Notes](#release-notes)
4. [Contributing Guidelines](#contributing-guidelines)

---

## Project Structure

### Overview

```
SnapWiz/
├── main.py                         # Main application (2,100+ lines)
├── package_handler.py              # Package operations (580 lines)
├── logger.py                       # Installation history
├──config.py                        # Centralized configuration (300 lines)
├── language.py                     # i18n system (300 lines)
├── compile_translations.py         # Translation compiler
│
├── locales/                        # Translation files
│   ├── en/LC_MESSAGES/snapwiz.po
│   ├── fr/LC_MESSAGES/snapwiz.po
│   ├── de/LC_MESSAGES/snapwiz.po
│   ├── es/LC_MESSAGES/snapwiz.po
│   ├── it/LC_MESSAGES/snapwiz.po
│   └── ru/LC_MESSAGES/snapwiz.po
│
├── docs/                           # Documentation
│   ├── INDEX.md
│   ├── KEYBOARD_SHORTCUTS.md
│   ├── FEATURES_AND_IMPLEMENTATION.md
│   └── DEVELOPMENT_GUIDE.md        # This file
│
├── GUIDE/                          # User guides
│   └── LANGUAGE_SUPPORT_GUIDE.md
│
├── README.md                       # Main documentation
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── LICENSE                         # MIT License
├── requirements.txt                # Python dependencies
└── install.sh                      # Installation script
```

### Core Modules

#### **1. main.py** - Main Application

**Purpose:** PyQt5 GUI application with 4 tabs

**Key Classes:**
- `MainWindow` - Main application window
- `InstallerThread` - Background installation thread

**Key Methods:**
- `init_ui()` - Initialize user interface
- `create_install_tab()` - Install tab with drag-drop
- `create_uninstall_tab()` - Uninstall tab (placeholder)
- `create_history_tab()` - History viewing
- `create_settings_tab()` - Settings with theme and language
- `dragEnterEvent()` - Handle drag operations
- `dropEvent()` - Handle file drops
- `change_language()` - Language switching
- `change_theme()` - Theme switching
- `apply_theme()` - Apply theme colors

**Dependencies:**
- PyQt5 (GUI framework)
- config (configuration)
- language (i18n)
- package_handler (backend)
- logger (history)

#### **2. package_handler.py** - Package Operations

**Purpose:** Backend logic for all package operations

**Key Methods:**
- `validate_package()` - Check if file is valid package
- `get_package_type()` - Determine package format
- `get_package_info()` - Extract metadata
  - `_get_deb_info()` - Debian package info
  - `_get_rpm_info()` - RPM package info
  - `_get_snap_info()` - Snap package info
  - `_get_flatpak_info()` - Flatpak package info
- `install_package()` - Install dispatcher
  - `_install_deb()` - Debian installation
  - `_install_rpm()` - RPM installation
  - `_install_snap()` - Snap installation
  - `_install_flatpak()` - Flatpak installation
- `detect_package_manager()` - Find system package manager
- `_detect_all_managers()` - Detect all available managers

**Supported Formats:**
- `.deb` (Debian packages)
- `.rpm` (Red Hat packages)
- `.snap` (Snap packages)
- `.flatpak` (Flatpak bundles)

#### **3. config.py** - Configuration

**Purpose:** Centralized settings and constants

**Categories:**
- Application info (name, version, author)
- Window settings (size, title)
- Package formats (supported formats, commands)
- Installation settings (timeout, steps)
- UI settings (themes, fonts, colors)
- Keyboard shortcuts
- Directory paths
- Logging settings
- Batch installation limits
- Drag-and-drop settings
- Language support

**Helper Functions:**
- `ensure_config_dir()` - Create config directory
- `get_supported_extensions()` - Get list of extensions
- `get_package_format_by_extension()` - Get format info
- `is_supported_package()` - Check if file is supported

#### **4. language.py** - Internationalization

**Purpose:** Gettext-based translation system

**Key Classes:**
- `LanguageManager` - Manages translations
- `JSONTranslation` - JSON-based translation fallback

**Key Functions:**
- `_(msgid, **kwargs)` - Get translation
- `set_language(code)` - Change language
- `get_current_language()` - Get active language
- `get_available_languages()` - List languages
- `compile_po_files()` - Compile .po to .json

**Translation Flow:**
1. Load preference from `~/.snapwiz/settings.json`
2. Load `.json` or `.mo` file from `locales/{lang}/LC_MESSAGES/`
3. Fallback to English if not found
4. Return msgid as-is if no translation

#### **5. logger.py** - History Tracking

**Purpose:** Track installation history in JSON

**Key Methods:**
- `log_installation()` - Log install attempt
- `get_all_installations()` - Get history
- `clear_history()` - Clear all entries
- `export_history()` - Export to file
- `import_history()` - Import from file

**Storage:**
- Location: `~/.snapwiz/installation_history.json`
- Format: JSON array of objects
- Fields: timestamp, package, status, message

### Data Flow

```
User Action
    ↓
main.py (GUI)
    ↓
package_handler.py (Backend)
    ↓
System Package Manager (apt/dnf/snap/flatpak)
    ↓
logger.py (History)
    ↓
~/.snapwiz/installation_history.json
```

### Configuration Flow

```
User Changes Language
    ↓
main.py (Settings tab)
    ↓
language.py (set_language)
    ↓
~/.snapwiz/settings.json (save preference)
    ↓
Restart Application
    ↓
language.py (load preference)
    ↓
locales/{lang}/LC_MESSAGES/snapwiz.json
```

---

## Development Roadmap

### 📅 Version History

| Version | Date | Status | Highlights |
|---------|------|--------|------------|
| **1.0.0** | 2026-01-15 | Released | Initial release, .deb/.rpm support |
| **1.1.0** | 2026-01-22 | Released | UI/UX enhancements, themes, shortcuts |
| **1.4.0** | 2026-02-09 | **Current** | Snap/Flatpak, drag-drop, multi-language |
| **2.0.0** | TBD | Planned | Batch install, uninstall, verification |

### 🚀 v2.0 Planned Features

#### Feature 1: Batch Installation Queue
**Priority:** High  
**Complexity:** Medium  
**Status:** 🚧 Planned

**Features:**
- Multi-file selection
- Installation queue display
- Sequential installation with progress
- Cancel/pause queue
- Skip failed packages option
- Estimated total time

**UI Changes:**
- "Add to Queue" button
- Queue list with drag-to-reorder
- Current package indicator
- Queue progress (X of Y packages)

**Implementation:**
```python
class QueueManager:
    def __init__(self):
        self.queue = []
    
    def add_package(self, path):
        self.queue.append(path)
    
    def install_queue(self, callback):
        for i, package in enumerate(self.queue):
            callback(i+1, len(self.queue), package)
            # Install package
```

#### Feature 2: Uninstallation
**Priority:** High  
**Complexity:** Medium  
**Status:** 🚧 Planned

**Features:**
- List all installed packages
- Filter by format (.deb/.rpm/.snap/.flatpak)
- Search packages
- Uninstall with confirmation
- Dependency checking
- Uninstall history logging

**UI Changes:**
- New "Uninstall Package" tab
- Package list with search bar
- Uninstall button
- Confirmation dialog

**Backend Commands:**
```bash
# Debian/Ubuntu
sudo apt remove package-name
sudo dpkg -r package-name

# Fedora/RHEL
sudo dnf remove package-name
sudo rpm -e package-name

# Snap
sudo snap remove package-name

# Flatpak
flatpak uninstall package-id
```

#### Feature 3: Package Verification
**Priority:** Medium  
**Complexity:** High  
**Status:** 🚧 Planned

**Features:**
- SHA256 checksum verification
- MD5 checksum verification (fallback)
- GPG signature validation
- File size verification
- Optional verification
- Trust/skip prompts

**Implementation:**
```python
import hashlib
import gnupg

def verify_sha256(file_path, expected_hash):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest() == expected_hash
```

#### Feature 4: Search & Filter
**Priority:** Medium  
**Complexity:** Low  
**Status:** 🚧 Planned

**Features:**
- Search by package name
- Filter by status (Success/Failed)
- Filter by date range
- Filter by package type
- Sort by date/name/status
- Real-time search
- Result count display

#### Feature 5: Export/Import History
**Priority:** Low  
**Complexity:** Low  
**Status:** 🚧 Planned

**Features:**
- Export to CSV
- Export to JSON
- Import history from backup
- Merge or replace option
- Date range selection
- Statistics in export

### 📊 Implementation Phases

**Phase 1: Core Features (v1.5) - Q2 2026**
1. Search & Filter (Quick win)
2. Export/Import History

**Phase 2: Advanced Features (v1.6) - Q3 2026**
3. Batch Installation
4. Uninstallation Feature

**Phase 3: Security (v2.0) - Q4 2026**
5. Package Verification

### ⚠️ Known Limitations (v1.4.0)

**Batch Installation:**
- Recommended maximum: 20 packages
- No dependency resolution between queued packages
- Multiple password prompts may be required

**Snap Packages:**
- Requires `snapd` service running
- Uses `--dangerous` flag for local files
- First installation may be slower

**Flatpak Packages:**
- Only bundles (`.flatpak` files) supported
- Not repository refs
- User install attempted first, then system-wide

**Translation System:**
- Requires restart after language change
- Not all UI elements translated yet (work in progress)

### 🎯 Success Criteria

**For v2.0 Release:**
- [ ] Can queue and install 10+ packages
- [ ] Can list and uninstall packages safely
- [ ] Package verification working (SHA256 + GPG)
- [ ] Search & filter performs well (1000+ entries)
- [ ] Export/import without data loss
- [ ] All features documented
- [ ] Comprehensive test suite

---

## Release Notes

### v1.4.0 (2026-02-09) - Current Release

**Major Features:**

✨ **Extended Package Format Support**
- Added Snap (`.snap`) package installation
- Added Flatpak (`.flatpak`) bundle installation
- Now supports 4 package formats total

🎯 **Drag-and-Drop Support**
- Drag package files directly into window
- Multi-file drop support (up to 50 files)
- Automatic queue addition
- Visual feedback and notifications

⚙️ **Centralized Configuration**
- New `config.py` module
- All settings in one place
- Easy customization
- No hardcoded values

🌍 **Multi-Language Support**
- 6 languages: English, French, German, Spanish, Italian, Russian
- Gettext-based professional i18n
- Standard `.po` files in `locales/` folder
- Language selector in Settings
- 360 total translations

**Improvements:**
- Better error messages for snap/flatpak
- Service status checking
- Privilege escalation handling
- Auto-compile translations on first run

**Bug Fixes:**
- Fixed file filter to include all formats
- Fixed theme persistence
- Improved error handling for missing tools

---

### v1.1.0 (2026-01-22)

**UI/UX Enhancements:**

⌨️ **Keyboard Shortcuts**
- Ctrl+O: Open package
- Ctrl+I: Install
- F5: Refresh history
- Ctrl+Q: Quit

🎨 **Themes**
- Light and Dark themes
- Persistent theme selection
- Instant theme switching

🔔 **System Tray**
- Minimize to tray
- Installation notifications
- Restore with double-click

💡 **Tooltips**
- Every button explained
- Helpful hints throughout
- Context-sensitive help

**Other:**
- Professional icons and emojis
- 7-step progress tracking
- Improved error messages
- Better status indicators

---

### v1.0.0 (2026-01-15) - Initial Release

**Core Features:**
- Install `.deb` packages (Debian/Ubuntu)
- Install `.rpm` packages (Fedora/RHEL)
- Package information display
- Installation history
- Automatic package manager detection
- Progress tracking
- Error handling

---

## Contributing Guidelines

### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/Srijan-XI/SnapWiz.git
   cd SnapWiz
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes**
   - Follow code style guidelines
   - Add docstrings to functions
   - Update documentation

3. **Test changes**
   - Test on multiple distributions if possible
   - Test all package formats
   - Test themes and languages

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```
   Then create Pull Request on GitHub

### Code Style

**Python:**
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all functions/classes

**Example:**
```python
def install_package(self, package_path):
    """
    Install a package file.
    
    Args:
        package_path (str): Absolute path to package file
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Implementation
    pass
```

**Commit Messages:**
- Use conventional commits format
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Examples:
  - `feat: Add snap package support`
  - `fix: Fix drag-drop validation`
  - `docs: Update README with new features`
  - `refactor: Extract config to separate module`

### Adding New Package Format

1. **Update `config.py`:**
   ```python
   SUPPORTED_FORMATS = {
       # ...
       'appimage': {
           'extension': '.appimage',
           'description': 'AppImage Package',
           'icon': '📦',
           'managers': ['appimaged'],
           'info_command': ['file'],
           'install_commands': [
               ['chmod', '+x'],
           ]
       }
   }
   ```

2. **Add info extraction in `package_handler.py`:**
   ```python
   def _get_appimage_info(self, package_path):
       """Extract AppImage metadata"""
       # Implementation
       pass
   ```

3. **Add installation method:**
   ```python
   def _install_appimage(self, package_path):
       """Install AppImage file"""
       # Implementation
       pass
   ```

4. **Update `get_package_info()` and `install_package()`**

5. **Update documentation**

### Adding New Language

1. **Create locale directory:**
   ```bash
   mkdir -p locales/pt/LC_MESSAGES
   ```

2. **Copy template:**
   ```bash
   cp locales/en/LC_MESSAGES/snapwiz.po locales/pt/LC_MESSAGES/snapwiz.po
   ```

3. **Translate all `msgstr` values**

4. **Add to `config.py`:**
   ```python
   SUPPORTED_LANGUAGES = {
       # ...
       'pt': 'Portuguese',
   }
   ```

5. **Compile:**
   ```bash
   python compile_translations.py
   ```

6. **Test and submit PR**

### Testing

**Manual Testing Checklist:**

For new features, test:
- [ ] Installation on Ubuntu/Debian
- [ ] Installation on Fedora/RHEL (if possible)
- [ ] All package formats (.deb, .rpm, .snap, .flatpak)
- [ ] Drag-and-drop with multiple files
- [ ] Language switching
- [ ] Theme switching
- [ ] Error scenarios (missing tools, wrong format, etc.)
- [ ] Keyboard shortcuts
- [ ] History logging

**Automated Testing (Future):**
- Unit tests with pytest
- GUI tests with pytest-qt
- Integration tests
- CI/CD pipeline

### Documentation

When adding features, update:
- [ ] README.md (if user-facing)
- [ ] CHANGELOG.md (version entry)
- [ ] docs/FEATURES_AND_IMPLEMENTATION.md
- [ ] Relevant guide in GUIDE/
- [ ] Docstrings in code

### Questions?

- Open an issue on GitHub
- Check existing documentation
- Review similar features in codebase

---

## Technical Debt & Future Work

### Refactoring Opportunities

1. **Test Suite** - Add comprehensive automated tests
2. **Error Handling** - Centralize error handling logic
3. **Logging** - Add proper logging framework (not just history)
4. **Configuration** - Add GUI for editing config.py
5. **Plugin System** - Make package formats pluggable

### Performance Optimization

1. **Large History Files** - Optimize for 1000+ entries
2. **Package Info Extraction** - Cache metadata
3. **Translation Loading** - Lazy load languages
4. **UI Rendering** - Optimize for low-end systems

### Code Quality

1. **Type Hints** - Add Python type annotations
2. **Linting** - Set up flake8/pylint
3. **Formatting** - Set up black/autopep8
4. **Documentation** - Add more inline comments

---

## Resources

### Development Tools

- **Qt Designer** - For GUI design
- **Poedit** - For translation editing
- **pytest** - For unit testing
- **pytest-qt** - For Qt GUI testing

### Documentation

- PyQt5 Docs: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- Gettext Guide: https://www.gnu.org/software/gettext/manual/
- Python Packaging: https://packaging.python.org/

### Package Manager Docs

- apt: https://wiki.debian.org/Apt
- dnf: https://dnf.readthedocs.io/
- snap: https://snapcraft.io/docs
- flatpak: https://docs.flatpak.org/

---

**Development Guide Version:** 1.4.0  
**Last Updated:** 2026-02-09  
**Maintainers:** Srijan-XI

**Happy Coding! ⚡🧙‍♂️**
