# SnapWiz - Project Structure

**Version:** 1.4.1  
**Last Updated:** 2026-02-09  
**Reorganization:** Clean, Professional Project Layout

---

## 📁 Directory Structure

```
SnapWiz/
├── main.py                         # Main application entry point
├── README.md                       # Project documentation
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── LICENSE                         # MIT License
├── install.sh                      # Installation script
├── requirements.txt                # Python dependencies
├── setup.py                        # Setup configuration
├── .gitignore                      # Git ignore rules
├── Dockerfile                     # Full Tauri build image
├── docker-compose.yml             # Frontend/backend Docker workflow
├── .dockerignore                  # Docker build context exclusions
├── package.json                   # Frontend and Tauri scripts
├── package-lock.json              # npm dependency lockfile
├── frontend/                      # React/TypeScript frontend
│   ├── Dockerfile.frontend        # Frontend development image
│   ├── App.tsx                    # Application shell
│   ├── App.css                    # Frontend styling
│   ├── main.tsx                   # Frontend entry point
│   └── index.html                 # Frontend HTML entry
├── backend/                       # Backend container configuration
│   └── Dockerfile.backend         # Rust/Tauri validation image
├── src-tauri/                     # Rust/Tauri backend source
│   ├── Cargo.toml                 # Rust dependencies
│   ├── tauri.conf.json            # Tauri application configuration
│   └── src/                       # Commands and backend services
│
├── src/                            # Core source code
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Centralized configuration
│   ├── package_handler.py          # Package operations
│   ├── logger.py                   # Installation history
│   ├── language.py                 # Internationalization (i18n)
│   ├── exceptions.py               # Custom exception classes
│   └── retry_utils.py              # Retry logic and utilities
│
├── utils/                          # Utility scripts
│   ├── __init__.py                 # Package initialization
│   └── compile_translations.py     # Translation compiler
│
├── examples/                       # Example implementations
│   ├── main_old.py                 # Old version reference
│   └── package_handler_enhanced_example.py  # Enhanced handler example
│
├── locales/                        # Translation files
│   ├── en/LC_MESSAGES/             # English
│   ├── fr/LC_MESSAGES/             # French
│   ├── de/LC_MESSAGES/             # German
│   ├── es/LC_MESSAGES/             # Spanish
│   ├── it/LC_MESSAGES/             # Italian
│   └── ru/LC_MESSAGES/             # Russian
│
├── docs/                           # Documentation
│   ├── INDEX.md                    # Documentation index
│   ├── KEYBOARD_SHORTCUTS.md       # Quick reference
│   ├── FEATURES_AND_IMPLEMENTATION.md  # Feature documentation
│   ├── DEVELOPMENT_GUIDE.md        # Developer guide
│   └── ERROR_HANDLING_GUIDE.md     # Error handling documentation
│
└── GUIDE/                          # User guides
    └── LANGUAGE_SUPPORT_GUIDE.md   # Language support guide
```

---

## 📦 Package Organization

### Tauri and Docker Packages

The migration runtime is split into a web frontend and native Rust backend:

- `frontend/` renders the application and invokes typed Tauri commands.
- `src-tauri/src/` owns package validation, metadata, installation, verification, settings, and history.
- `frontend/Dockerfile.frontend` runs Vite on port `1420`.
- `backend/Dockerfile.backend` validates the Rust crate with `cargo check`.
- `docker-compose.yml` provides the `frontend` and `backend` development services.
- `Dockerfile` builds the complete Linux Tauri toolchain with Node 22 and Rust 1.90.

### Root Directory

**Files that remain in root:**
- `main.py` - Application entry point, imports from `src/`
- `README.md` - Main documentation
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE` - MIT License
- `install.sh` - Installation script for Linux
- `requirements.txt` - Python dependencies for pip
- `setup.py` - Setup configuration
- `.gitignore` - Git ignore patterns

**Why these stay in root:**
- Standard Python project convention
- Easy to find for new users
- Expected locations for documentation
- Installation scripts need root access

---

## 🏗️ src/ Package

**Core application modules organized in src/ package**

### src/__init__.py
```python
"""SnapWiz core package"""
__version__ = "1.4.1"
__author__ = "Srijan-XI"

# Convenience imports
from .config import *
from .exceptions import SnapWizError
from .language import _, get_current_language, set_language
```

### src/config.py (300+ lines)
**Centralized configuration management**
- Application constants (name, version, author)
- Window settings
- Package format definitions
- Installation settings
- UI themes and colors
- Keyboard shortcuts
- Directory paths
- Language support

**Key Functions:**
- `ensure_config_dir()` - Create configuration directory
- `get_supported_extensions()` - List file extensions
- `get_package_format_by_extension()` - Get format info
- `is_supported_package()` - Check if file supported

### src/package_handler.py (640 lines)
**Package operations for all formats**
- Package validation
- Installation (deb, rpm, snap, flatpak)
- Package information extraction
- Package manager detection

**Key Classes:**
- `PackageHandler` - Main handler class

**Key Methods:**
- `validate_package()` - Check if package valid
- `install_package()` - Install package
- `get_package_info()` - Extract metadata
- `detect_package_manager()` - Find system PM

### src/logger.py (200+ lines)
**Installation history tracking**
- Log installation attempts
- Store success/failure
- Export/import history (planned)

**Key Functions:**
- `log_installation()` - Log install attempt
- `get_all_installations()` - Retrieve history
- `clear_history()` - Clear all entries

### src/language.py (376 lines)
**Internationalization system**
- Gettext-based translation
- JSON fallback
-6 supported languages
- Language preference persistence

**Key Classes:**
- `LanguageManager` - Translation manager
- `JSONTranslation` - JSON-based fallback

**Key Functions:**
- `_(msgid, **kwargs)` - Get translation
- `set_language(code)` - Change language
- `get_current_language()` - Get active language
- `compile_po_files()` - Compile translations

### src/exceptions.py (380 lines)
**Custom exception system**
- 15+ specific exception types
- Detailed error messages
- Helpful suggestions
- Error categorization

**Exception Categories:**
- Package errors (PackageNotFoundError, etc.)
- Installation errors (DependencyError, etc.)
- Permission errors (InsufficientPrivilegesError)
- Network errors (DownloadError, etc.)
- System errors (ServiceNotRunningError, etc.)
- Language errors (UnsupportedLanguageError, etc.)

**Helper Functions:**
- `get_error_category()` - Categorize error
- `get_error_icon()` - Get emoji for error
- `is_retryable_error()` - Check if retryable

### src/retry_utils.py (340 lines)
**Retry logic and utilities**
- Configurable retry behavior
- Exponential backoff
- Progress callbacks

**Key Classes:**
- `RetryConfig` - Retry configuration
- `RetryableOperation` - Context manager

**Key Functions:**
- `retry_on_failure()` - Decorator for retry
- `retry_with_progress()` - Retry with progress
- `should_retry()` - Check if should retry

**Predefined Configs:**
- `DEFAULT_RETRY_CONFIG` - 3 attempts, 1s delay
- `NETWORK_RETRY_CONFIG` - 5 attempts, 2s delay
- `INSTALLATION_RETRY_CONFIG` - 2 attempts, 3s delay

---

## 🛠️ utils/ Package

**Utility scripts and tools**

### utils/compile_translations.py (124 lines)
**Translation compilation**
- Compiles `.po` files to `.json`
- Pure Python implementation
- No external dependencies (no msgfmt needed)

**Usage:**
```bash
python -m utils.compile_translations
# or
cd utils && python compile_translations.py
```

---

## 💡 examples/ Package

**Reference implementations and old versions**

### examples/main_old.py
**Previous version of main.py**
- Kept for reference
- Older implementation
- Can be removed after full migration

### examples/package_handler_enhanced_example.py (399 lines)
**Enhanced package handler example**
- Demonstrates exception usage
- Shows retry logic integration
- Example error handling
- Reference for improvements

**Not meant for production use - examples only**

---

## 🌍 locales/ Directory

**Translation files for 6 languages**

Structure:
```
locales/
├── en/LC_MESSAGES/
│   ├── snapwiz.po      # English source
│   └── snapwiz.json    # Compiled translation
├── fr/LC_MESSAGES/     # French
├── de/LC_MESSAGES/     # German
├── es/LC_MESSAGES/     # Spanish
├── it/LC_MESSAGES/     # Italian
└── ru/LC_MESSAGES/     # Russian
```

**Files:**
- `.po` - Portable Object files (source)
- `.json` - Compiled JSON translations (generated)

**Workflow:**
1. Edit `.po` files for translations
2. Run `utils/compile_translations.py`
3. JSON files generated automatically
4. Application loads JSON at runtime

---

## 📚 docs/ Directory

**Project documentation**

### docs/INDEX.md
- Documentation navigation
- Quick links
- Structure overview

### docs/KEYBOARD_SHORTCUTS.md
- Quick reference
- All keyboard shortcuts
- Power user tips

### docs/FEATURES_AND_IMPLEMENTATION.md (15.6 KB)
- All feature documentation
- Implementation details
- Multi-language support
- UI/UX enhancements
- Quick reference
- Troubleshooting

### docs/DEVELOPMENT_GUIDE.md (18.4 KB)
- Project structure
- Development roadmap
- Release notes
- Contributing guidelines
- Technical details

### docs/ERROR_HANDLING_GUIDE.md
- Custom exception system
- Retry logic documentation
- Integration examples
- Usage guide

---

## 📖 GUIDE/ Directory

**User-focused guides**

### GUIDE/LANGUAGE_SUPPORT_GUIDE.md
- How to use multi-language system
- Changing language
- Translation system overview
- Adding new languages

---

## 🔄 Import Patterns

### From main.py (root)
```python
from src.package_handler import PackageHandler
from src.logger import InstallLogger
from src import config
from src import language
from src.language import _
```

### Within src/ package
```python
# Relative imports
from . import config
from .exceptions import SnapWizError
from .retry_utils import retry_on_failure

# Or absolute
from src import config
from src.exceptions import SnapWizError
```

### From examples/
```python
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import config
from src.exceptions import *
from src.retry_utils import *
```

### From utils/
```python
# Access parent directory for locales
from pathlib import Path
locale_dir = Path(__file__).parent.parent / 'locales'
```

---

## 🎯 Key Improvements

### Before Reorganization
```
Root directory:
- 19 Python files mixed together
- No clear organization
- Hard to find modules
- Confusing for contributors
```

### After Reorganization
```
Root directory:
- 6 essential files only
- Clear package structure (src/, utils/, examples/)
- Easy to navigate
- Professional layout
- Better for contributors
```

### Benefits

**For Users:**
- ✅ Cleaner repository
- ✅ Easy to find documentation
- ✅ Clear entry point (main.py)

**For Developers:**
- ✅ Clear module organization
- ✅ Easy to import modules
- ✅ Standard Python package structure
- ✅ Separation of concerns

**For Maintainers:**
- ✅ Easier to manage codebase
- ✅ Clear responsibility for each package
- ✅ Better for version control
- ✅ Scales well for future growth

---

## 📊 Statistics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Root files** | 19 | 6 | -68% clutter |
| **Python files in root** | 13 | 1 | Much cleaner |
| **Packages** | 0 | 3 | Organized |
| **Clear structure** | ❌ | ✅ | Professional |

---

## 🚀 Running the Application

### Development
```bash
# From project root
python main.py
```

### Compile Translations
```bash
# Method 1
python -m utils.compile_translations

# Method 2
cd utils
python compile_translations.py
```

### Run Examples
```bash
cd examples
python package_handler_enhanced_example.py
```

---

## 💻 Installation

### For End Users
```bash
# Install normally
python install.sh
# or
pip install -e .
```

### For Developers
```bash
# Clone repository
git clone https://github.com/Srijan-XI/SnapWiz.git
cd SnapWiz

# Install in development mode
pip install -e .

# Or install dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## 📝 Adding New Modules

### To src/ package:
1. Create `src/new_module.py`
2. Add imports to `src/__init__.py` if needed
3. Import in main.py: `from src.new_module import Something`

### To utils/ package:
1. Create `utils/new_util.py`
2. Run from project root: `python -m utils.new_util`

### To examples/:
1. Create `examples/new_example.py`
2. Add path setup:
   ```python
   import sys, os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
   ```
3. Import from src: `from src import config`

---

## ✅ Migration Checklist

- [x] Created src/ package with __init__.py
- [x] Moved core modules to src/
- [x] Created utils/ package
- [x] Moved utilities to utils/
- [x] Created examples/ package
- [x] Moved examples to examples/
- [x] Updated all imports in main.py
- [x] Fixed path references in language.py
- [x] Fixed path references in compile_translations.py
- [x] Updated example imports
- [x] Tested imports work correctly
- [x] Updated documentation
- [x] Created PROJECT_STRUCTURE.md

---

**Reorganization Status:** ✅ Complete  
**Structure:** Professional Python Package  
**Backward Compatibility:** Maintained (imports updated)  

**SnapWiz - Now with clean, professional structure! ⚡🧙‍♂️**
