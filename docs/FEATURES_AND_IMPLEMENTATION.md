# SnapWiz Features & Implementation Guide

**Version:** 1.4.0  
**Last Updated:** 2026-02-09

---

## Table of Contents

1. [New Features in v1.4.0](#new-features-in-v14)
2. [Implementation Summary](#implementation-summary)
3. [Multi-Language Support](#multi-language-support)
4. [UI/UX Enhancements](#uiux-enhancements)
5. [Quick Reference](#quick-reference)

---

## New Features in v1.4

### 🎉 Major Additions

#### 1. **Extended Package Format Support**

SnapWiz now supports **4 package formats:**

| Format | Extension | Manager | Description |
|--------|-----------|---------|-------------|
| Debian | `.deb` | apt/dpkg | Debian-based distributions |
| RPM | `.rpm` | dnf/yum/zypper | Red Hat-based distributions |
| Snap | `.snap` | snapd | Universal Linux packages |
| Flatpak | `.flatpak` | flatpak | Universal sandboxed apps |

**Snap Package Support:**
- Automatic `snapd` service detection and status checking
- Local `.snap` file installation with `--dangerous` flag
- Package metadata extraction using `unsquashfs`
- Error handling for missing daemon or service issues

**Flatpak Package Support:**
- Bundle (`.flatpak`) file installation
- User-level installation attempt first, then system-wide
- Automatic privilege escalation with `pkexec` when needed
- Runtime dependency handling

#### 2. **Drag-and-Drop Functionality** 🎯

Enhance your workflow with intuitive file handling:

**Features:**
- Drag package files directly into the SnapWiz window
- Multi-file support (up to 50 files at once)
- Automatic validation of package formats
- Smart queue management
- Visual feedback during drag operation
- Status bar notifications
- Auto-switch to Install tab

**How to Use:**
1. Open SnapWiz
2. Drag `.deb`, `.rpm`, `.snap`, or `.flatpak` files from file manager
3. Drop them anywhere in the SnapWiz window
4. Files automatically added to installation queue
5. Click "Start Batch Installation" to install all

**Configuration:**
```python
# config.py settings
DRAG_DROP_ENABLED = True
DRAG_DROP_MAX_FILES = 50
DRAG_DROP_ACCEPTED_MIMES = ['text/uri-list', 'text/plain']
```

#### 3. **Centralized Configuration System** ⚙️

All settings now managed in `config.py`:

**Benefits:**
- No hardcoded values in main code
- Easy customization for developers
- Consistent settings across application
- Simple to add new package formats
- Theme and UI configuration in one place

**Key Configuration Categories:**
- Application info (name, version, author)
- Window settings (size, title)
- Package formats and managers
- Installation settings (timeout, verification)
- UI settings (themes, fonts, buttons)
- Keyboard shortcuts
- Drag-and-drop settings
- Language support

**Example Usage:**
```python
import config

# Use configured values
window_title = config.WINDOW_TITLE
supported_formats = config.get_supported_extensions()
theme_colors = config.THEMES['Dark']
```

#### 4. **Multi-Language Support** 🌍

Professional internationalization using gettext:

**Supported Languages:**
- 🇬🇧 English (en) - Default
- 🇫🇷 French (fr) - Français
- 🇩🇪 German (de) - Deutsch
- 🇪🇸 Spanish (es) - Español
- 🇮🇹 Italian (it) - Italiano
- 🇷🇺 Russian (ru) - Русский

**Translation System:**
- Standard gettext `.po` files in `locales/` folder
- 360 translations (60 keys × 6 languages)
- Language selector in Settings tab
- Persistent language preference
- Auto-fallback to English if translation missing

**Changing Language:**
1. Go to Settings tab
2. Select "Language" dropdown
3. Choose your preferred language
4. Restart SnapWiz
5. Enjoy in your language!

**For Translators:**
- Edit `.po` files in `locales/{lang}/LC_MESSAGES/`
- Use tools like Poedit for easier editing
- Run `python compile_translations.py` to compile
- Submit pull request with translations

---

## Implementation Summary

### Architecture Overview

**Core Components:**

1. **main.py** (2,100+ lines)
   - Main application window (PyQt5)
   - Drag-and-drop event handlers
   - Tab management (Install, History, Settings)
   - Language selector integration
   - Theme system

2. **package_handler.py** (580 lines)
   - Package format detection
   - Metadata extraction for all 4 formats
   - Installation logic per format
   - Package manager detection
   - Error handling

3. **config.py** (300 lines)
   - Centralized configuration
   - All settings and constants
   - Helper functions
   - Format definitions

4. **language.py** (300 lines)
   - Gettext-based translation system
   - Language manager class
   - JSON translation fallback
   - Auto-compilation support

5. **logger.py** (Unchanged)
   - Installation history tracking
   - JSON-based storage
   - Success/failure logging

### New Files Added

```
p:\CODE-TOOLS\app-install-linux\
├── config.py                          ← NEW! Centralized config
├── language.py                        ← NEW! i18n system
├── compile_translations.py            ← NEW! Translation compiler
└── locales/                           ← NEW! Translation files
    ├── en/LC_MESSAGES/snapwiz.po
    ├── fr/LC_MESSAGES/snapwiz.po
    ├── de/LC_MESSAGES/snapwiz.po
    ├── es/LC_MESSAGES/snapwiz.po
    ├── it/LC_MESSAGES/snapwiz.po
    └── ru/LC_MESSAGES/snapwiz.po
```

### Code Changes Summary

**main.py:**
- Added drag-and-drop event handlers (`dragEnterEvent`, `dropEvent`)
- Enabled drag-and-drop with `setAcceptDrops(True)`
- Added language selector dropdown in Settings tab
- Added `change_language()` method
- Imported `config` and `language` modules
- Updated file browser filter to include all 4 formats

**package_handler.py:**
- Extended `get_package_info()` for snap and flatpak
- Added `_get_snap_info()` and `_get_flatpak_info()` methods
- Added `_install_snap()` and `_install_flatpak()` methods
- Added `_detect_all_managers()` for multiple manager detection
- Updated `__init__` to use `config.get_supported_extensions()`

### Statistics

| Metric | Value |
|--------|-------|
| **New Lines of Code** | ~1,500 |
| **New Files** | 9 (.py + .po files) |
| **Languages Supported** | 6 |
| **Total Translations** | 360 |
| **Package Formats** | 4 |
| **Drag-Drop Max Files** | 50 |
| **Configuration Items** | 80+ |

---

## Multi-Language Support

### Translation System Architecture

**Technology:** gettext (industry standard)  
**Format:** `.po` (Portable Object) files  
**Storage:** `locales/` folder with standard structure

**Directory Structure:**
```
locales/
├── en/
│   └── LC_MESSAGES/
│       ├── snapwiz.po      ← Source translations
│       └── snapwiz.json    ← Compiled (auto-generated)
├── fr/
│   └── LC_MESSAGES/
│       ├── snapwiz.po
│       └── snapwiz.json
└── [de, es, it, ru...]
```

### Translation Coverage

**60 Translation Keys per Language:**

- Application metadata (name, tagline, description)
- Tab names (Install, Uninstall, History, Settings)
- Button labels (11 buttons)
- Status messages (Ready, Installing, Completed, Failed, etc.)
- User messages (9 messages)
- Error messages (5 errors)
- Tooltips (7 helpful hints)
- Settings labels (13 labels)
- History column names
- Keyboard shortcut display

### How It Works

**1. Developer Code:**
```python
from language import _

# Simple translation
button.setText(_('btn_install'))

# With variables
message = _('msg_files_added', count=5)
# Result: "Added 5 package(s) to queue!"
```

**2. Translation File (French example):**
```po
msgid "btn_install"
msgstr "✅ Démarrer l'installation par lots"

msgid "msg_files_added"
msgstr "{count} paquet(s) ajouté(s) à la file !"
```

**3. Compilation:**
```bash
python compile_translations.py
```

**4. Runtime:**
- User selects French in Settings
- Preference saved to `~/.snapwiz/settings.json`
- On next startup, French translations loaded
- All `_('key')` calls return French text

### Adding New Language

**Step-by-Step:**

1. Create locale directory:
   ```bash
   mkdir -p locales/pt/LC_MESSAGES
   ```

2. Copy English template:
   ```bash
   cp locales/en/LC_MESSAGES/snapwiz.po locales/pt/LC_MESSAGES/snapwiz.po
   ```

3. Translate all `msgstr` values in the `.po` file

4. Add to `config.py`:
   ```python
   SUPPORTED_LANGUAGES = {
       # ...
       'pt': 'Portuguese',
   }
   ```

5. Compile:
   ```bash
   python compile_translations.py
   ```

6. Test and enjoy!

---

## UI/UX Enhancements

### Visual Design

**Icons and Emojis:**
- 📥 Install
- 🗑️ Uninstall
- 📋 History
- ⚙️ Settings
- ✅ Success
- ❌ Failure/Error
- ⚠️ Warning
- 🔄 Refresh
- 📂 Browse

**Themes:**
- **Light Theme** (Default): Clean, bright interface
- **Dark Theme**: Easy on eyes, modern dark colors
- Persistent theme selection
- Instant theme switching

**Color Schemes:**

*Light Theme:*
- Background: `#f5f5f5`
- Foreground: `#333333`
- Accent: `#3498db`
- Success: `#27ae60`
- Warning: `#f39c12`
- Danger: `#e74c3c`

*Dark Theme:*
- Background: `#2c3e50`
- Foreground: `#ecf0f1`
- Accent: `#3498db`
- (Same success/warning/danger colors)

### Keyboard Navigation

**Full keyboard support** - never need a mouse!

| Category | Shortcuts |
|----------|-----------|
| **Main Actions** | Ctrl+O (Open), Ctrl+I (Install), Ctrl+Q (Quit) |
| **Navigation** | Ctrl+Tab (Switch tabs), Tab/Shift+Tab (Navigate elements) |
| **History** | F5 (Refresh) |
| **Window** | Alt+F4 (Minimize to tray), Enter (Activate button) |

See `KEYBOARD_SHORTCUTS.md` for complete reference.

### System Tray Integration

**Features:**
- Minimize to tray instead of fully closing
- Double-click tray icon to restore window
- Installation progress notifications
- Right-click menu with quick actions

**Notifications:**
- Installation started
- Installation completed (success)
- Installation failed (with reason)
- Files added to queue

### Progress Tracking

**7-Step Installation Process:**

1. 📋 **Initialization** (5%)
2. 🔍 **Validation** (15%)
3. 🔐 **Security Verification** (25%)
4. 📖 **Reading Metadata** (40%)
5. 🔗 **Checking Dependencies** (50%)
6. ⚙️ **Installing Package** (60%)
7. 🔧 **Configuring** (85%)
8. ✅ **Finalizing** (95%)

**Visual Indicators:**
- Progress bar with percentage
- Current step name with icon
- Estimated time remaining (future)
- Real-time log output

### Tooltips System

**Comprehensive Help:**
- Every button has tooltip
- Every input field explained
- Keyboard shortcuts shown
- Status messages clarified
- Package format info displayed

**Examples:**
- "Browse for package files to add to the installation queue"
- "Install all packages in the queue"
- "Drag and drop package files here"
- "Choose between light and dark theme"

---

## Quick Reference

### Supported Package Formats

| Format | Extension | Install Command | Notes |
|--------|-----------|----------------|-------|
| Debian | `.deb` | `apt install -y` | For Ubuntu, Debian, Mint |
| RPM | `.rpm` | `dnf/yum install -y` | For Fedora, RHEL, CentOS |
| Snap | `.snap` | `snap install --dangerous` | Universal, requires snapd |
| Flatpak | `.flatpak` | `flatpak install -y` | Universal, sandboxed |

### System Requirements

**Operating System:**
- Debian/Ubuntu (apt/dpkg)
- Fedora (dnf)
- RHEL/CentOS (yum/dnf)
- openSUSE (zypper)
- Any Linux with snapd (for Snap)
- Any Linux with flatpak (for Flatpak)

**Python Requirements:**
- Python 3.6+
- PyQt5
- PyQt5-sip

**Optional (for specific formats):**
- `snapd` + `unsquashfs` (for Snap packages)
- `flatpak` (for Flatpak bundles)

### Common Workflows

**Workflow 1: Simple Single Package Install**
```
1. Click "📂 Add Package..." or press Ctrl+O
2. Select a .deb/.rpm/.snap/.flatpak file
3. Click "✅ Start Batch Installation" or press Ctrl+I
4. Enter password when prompted
5. Done!
```

**Workflow 2: Batch Install with Drag-and-Drop**
```
1. Open SnapWiz
2. Open file manager
3. Select multiple package files
4. Drag them into SnapWiz window
5. Drop to add to queue
6. Click "✅ Start Batch Installation"
7. Wait for all to complete
```

**Workflow 3: Change Language**
```
1. Go to Settings tab (⚙️)
2. Find "Language" dropdown
3. Select your language
4. Restart SnapWiz
5. Interface now in your language!
```

### Important Notes & Limitations

⚠️ **Batch Installation:**
- **Recommended maximum:** 20 packages per batch
- Larger batches may be slower
- For 50+ packages, split into smaller batches

⚠️ **Dependency Resolution:**
- Dependencies **between queued packages** are NOT auto-resolved
- Order packages manually (dependencies first)
- Individual package dependencies ARE handled by system managers

⚠️ **Password Prompts:**
- May be requested multiple times during batch installation
- This is a Linux security feature (OS limitation)
- Each package may require authentication
- Keep an eye on installation process

⚠️ **Package Format Specific:**

**Snap:**
- Requires `snapd` service running
- Uses `--dangerous` flag for local files
- First install may take longer (core snap setup)

**Flatpak:**
- Only bundle `.flatpak` files supported (not repository refs)
- User install attempted first, then system-wide
- May require runtime dependencies

### Configuration

All settings in `config.py`:

**Key Settings:**
```python
# Application
APP_NAME = "SnapWiz"
APP_VERSION = "1.4.0"

# Window
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 700

# Limits
BATCH_MAX_RECOMMENDED = 20
DRAG_DROP_MAX_FILES = 50
INSTALLATION_TIMEOUT = 300  # seconds

# Themes
DEFAULT_THEME = 'Light'

# Language
DEFAULT_LANGUAGE = 'en'
```

### File Locations

**User Data:**
- Settings: `~/.snapwiz/settings.json`
- History: `~/.snapwiz/installation_history.json`
- Logs: Installation logs in working directory

**Application:**
- Main app: `main.py`
- Config: `config.py`
- Translations: `locales/{lang}/LC_MESSAGES/snapwiz.po`

---

## Troubleshooting

### Common Issues

**1. Package format not recognized**
- Ensure file has correct extension (.deb, .rpm, .snap, .flatpak)
- File may be corrupted - redownload

**2. Snap installation fails**
- Install snapd: `sudo apt install snapd`
- Start service: `sudo systemctl start snapd`
- Enable service: `sudo systemctl enable snapd`

**3. Flatpak installation fails**
- Install flatpak: `sudo apt install flatpak`
- May need to add Flathub: `flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo`

**4. Language not changing**
- Make sure you restarted SnapWiz after changing language
- Check `~/.snapwiz/settings.json` has correct language code
- Recompile translations: `python compile_translations.py`

**5. Permission denied errors**
- Ensure your user has sudo privileges
- Enter password correctly when prompted
- Check that `pkexec` is installed

---

## Future Enhancements

See `DEVELOPMENT_GUIDE.md` for roadmap and planned features.

---

**Documentation Version:** 1.4.0  
**Last Updated:** 2026-02-09  
**SnapWiz - The Magical Package Installer** ⚡🧙‍♂️
