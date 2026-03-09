"""
Configuration Module for SnapWiz
Centralized settings and constants to avoid hardcoding values
"""

import os
from pathlib import Path

# ==================== APPLICATION INFO ====================
APP_NAME = "SnapWiz"
APP_TAGLINE = "The Magical Package Installer"
APP_DESCRIPTION = "Install packages in a snap, like a wizard!"
APP_VERSION = "1.4.0"
APP_AUTHOR = "Srijan-XI"
APP_LICENSE = "MIT"
APP_REPO = "https://github.com/Srijan-XI/SnapWiz"

# ==================== WINDOW SETTINGS ====================
WINDOW_TITLE = f"{APP_NAME} - {APP_TAGLINE}"
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# ==================== SUPPORTED PACKAGE FORMATS ====================
SUPPORTED_FORMATS = {
    'deb': {
        'extension': '.deb',
        'description': 'Debian Package',
        'icon': '📦',
        'managers': ['apt', 'apt-get', 'dpkg'],
        'info_command': ['dpkg-deb', '-I'],
        'install_commands': [
            ['pkexec', 'apt', 'install', '-y'],  # Preferred
            ['pkexec', 'dpkg', '-i'],            # Fallback
        ]
    },
    'rpm': {
        'extension': '.rpm',
        'description': 'RPM Package',
        'icon': '📦',
        'managers': ['dnf', 'yum', 'zypper', 'rpm'],
        'info_command': ['rpm', '-qip'],
        'install_commands': [
            ['pkexec', 'dnf', 'install', '-y'],
            ['pkexec', 'yum', 'install', '-y'],
            ['pkexec', 'zypper', 'install', '-y'],
            ['pkexec', 'rpm', '-ivh'],
        ]
    },
    'snap': {
        'extension': '.snap',
        'description': 'Snap Package',
        'icon': '📸',
        'managers': ['snap'],
        'info_command': ['snap', 'info'],
        'install_commands': [
            ['pkexec', 'snap', 'install'],
        ],
        'requires_daemon': True
    },
    'flatpak': {
        'extension': '.flatpak',
        'description': 'Flatpak Package',
        'icon': '📱',
        'managers': ['flatpak'],
        'info_command': ['flatpak', 'info'],
        'install_commands': [
            ['flatpak', 'install', '-y'],  # Flatpak handles permissions internally
        ],
        'requires_daemon': False
    }
}

# File filter for dialog
FILE_FILTER = "Package Files (*.deb *.rpm *.snap *.flatpak);;Debian Packages (*.deb);;RPM Packages (*.rpm);;Snap Packages (*.snap);;Flatpak Packages (*.flatpak);;All Files (*)"

# ==================== INSTALLATION SETTINGS ====================
INSTALLATION_TIMEOUT = 300  # seconds
INTEGRITY_CHECK_MIN_SIZE = 1024  # bytes (minimum file size)
DEFAULT_VERIFY_INTEGRITY = True
DEFAULT_VERIFY_SIGNATURE = False
DEFAULT_CHECKSUM_TYPE = 'sha256'

# Installation steps for progress tracking
INSTALLATION_STEPS = [
    {"name": "Initialization", "progress": 5, "icon": "📋"},
    {"name": "Validation", "progress": 15, "icon": "🔍"},
    {"name": "Security Verification", "progress": 25, "icon": "🔐"},
    {"name": "Reading Metadata", "progress": 40, "icon": "📖"},
    {"name": "Checking Dependencies", "progress": 50, "icon": "🔗"},
    {"name": "Installing Package", "progress": 60, "icon": "⚙️"},
    {"name": "Configuring", "progress": 85, "icon": "🔧"},
    {"name": "Finalizing", "progress": 95, "icon": "✅"},
]

# ==================== UI SETTINGS ====================
# Themes
THEMES = {
    'Light': {
        'background': '#f5f5f5',
        'foreground': '#333333',
        'accent': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'border': '#bdc3c7',
        'highlight': '#ecf0f1'
    },
    'Dark': {
        'background': '#2c3e50',
        'foreground': '#ecf0f1',
        'accent': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'border': '#34495e',
        'highlight': '#34495e'
    }
}

DEFAULT_THEME = 'Light'

# Font settings
HEADER_FONT_SIZE = 24
SUBTITLE_FONT_SIZE = 11
BUTTON_FONT_SIZE = 14
LABEL_FONT_SIZE = 10

# Button dimensions
BUTTON_HEIGHT_LARGE = 45
BUTTON_HEIGHT_MEDIUM = 35
BUTTON_WIDTH_LARGE = 250
BUTTON_WIDTH_MEDIUM = 180
BUTTON_WIDTH_SMALL = 130

# Progress bar
PROGRESS_BAR_HEIGHT = 25
PROGRESS_BAR_UPDATE_INTERVAL = 200  # milliseconds

# ==================== KEYBOARD SHORTCUTS ====================
SHORTCUTS = {
    'browse': 'Ctrl+O',
    'install': 'Ctrl+I',
    'refresh': 'F5',
    'quit': 'Ctrl+Q',
    'switch_tab': 'Ctrl+Tab',
}

SHORTCUTS_DISPLAY = "💡 Shortcuts: Ctrl+O (Open) | Ctrl+I (Install) | F5 (Refresh) | Ctrl+Q (Quit)"

# ==================== DIRECTORY PATHS ====================
# User configuration directory
USER_CONFIG_DIR = Path.home() / f".{APP_NAME.lower()}"
HISTORY_FILE = USER_CONFIG_DIR / "installation_history.json"
SETTINGS_FILE = USER_CONFIG_DIR / "settings.json"
INSTALL_PATH_FILE = USER_CONFIG_DIR / "install_path.txt"

# Desktop integration
DESKTOP_ENTRY_DIR = Path.home() / ".local" / "share" / "applications"
BIN_DIR = Path.home() / ".local" / "bin"

# ==================== LOGGING SETTINGS ====================
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ==================== BATCH INSTALLATION ====================
# Maximum recommended packages per batch
# Larger batches may experience performance issues or slower installation times
BATCH_MAX_RECOMMENDED = 20

# Progress update delay for batch operations  
BATCH_PROGRESS_UPDATE_DELAY = 100  # milliseconds

# IMPORTANT LIMITATIONS:
# 1. Dependency Resolution: Dependencies between queued packages are NOT automatically resolved.
#    Packages should be ordered manually with dependencies installed first.
#
# 2. Password Prompts: Root password may be requested multiple times during batch installation
#    due to Linux security policies (pkexec/sudo timeout between packages).
#    This is an OS limitation, not a SnapWiz issue.
#
# 3. Batch Size: While the app can handle more than 20 packages, it's not recommended.
#    Large batches may require multiple password entries and longer installation times.

# ==================== HISTORY SETTINGS ====================
HISTORY_MAX_ENTRIES = 1000  # Maximum history entries before warning
EXPORT_FORMATS = ['json', 'csv']

# ==================== NOTIFICATIONS ====================
NOTIFICATION_DURATION = 2000  # milliseconds
NOTIFICATION_SUCCESS_TITLE = "Installation Complete"
NOTIFICATION_FAILURE_TITLE = "Installation Failed"
NOTIFICATION_MINIMIZED_TITLE = APP_NAME
NOTIFICATION_MINIMIZED_MESSAGE = "Application minimized to tray. Double-click to restore."

# ==================== VALIDATOR SETTINGS ====================
CHECKSUM_ALGORITHMS = ['sha256', 'md5', 'sha1', 'sha512']
CHUNK_SIZE_FOR_CHECKSUM = 8192  # bytes

# ==================== DRAG AND DROP ====================
DRAG_DROP_ENABLED = True
DRAG_DROP_ACCEPTED_MIMES = ['text/uri-list', 'text/plain']
DRAG_DROP_MAX_FILES = 50  # Maximum files to accept in one drop

# ==================== LANGUAGE SUPPORT (Future) ====================
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'ru': 'Russian',
}
DEFAULT_LANGUAGE = 'en'

# ==================== ICONS ====================
ICONS = {
    'app': '⚡🧙‍♂️',
    'install': '📥',
    'uninstall': '🗑️',
    'history': '📋',
    'settings': '⚙️',
    'browse': '📂',
    'success': '✅',
    'failure': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'search': '🔍',
    'filter': '🎯',
    'export': '📤',
    'import': '📥',
    'refresh': '🔄',
    'cancel': '⏹️',
    'loading': '⏳',
    'waiting': '⏸️',
}

# ==================== TAB NAMES ====================
TAB_NAMES = {
    'install': f"{ICONS['install']} Install Package",
    'uninstall': f"{ICONS['uninstall']} Uninstall Package",
    'history': f"{ICONS['history']} Installation History",
    'settings': f"{ICONS['settings']} Settings",
}

# ==================== ERROR MESSAGES ====================
ERROR_MESSAGES = {
    'no_package_selected': "Please select a package file first.",
    'invalid_package': "Invalid package file. Please select a .deb, .rpm, .snap, or .flatpak file.",
    'package_not_found': "Package file not found.",
    'no_package_manager': "No suitable package manager found for this file type.",
    'installation_failed': "Installation failed. Check the log for details.",
    'permission_denied': "Permission denied. Make sure you have administrative privileges.",
    'timeout': "Installation timed out. The package may be too large or there may be network issues.",
    'verification_failed': "Package verification failed. The package may be corrupted or tampered with.",
    'no_history': "No installation history available.",
    'export_failed': "Failed to export history.",
    'import_failed': "Failed to import history.",
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    'installation_complete': "Package installed successfully!",
    'uninstallation_complete': "Package uninstalled successfully!",
    'history_cleared': "Installation history cleared.",
    'history_exported': "History exported successfully.",
    'history_imported': "History imported successfully.",
    'settings_saved': "Settings saved successfully.",
}

# ==================== HELPER FUNCTIONS ====================
def ensure_config_dir():
    """Ensure the configuration directory exists"""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def get_supported_extensions():
    """Get list of supported file extensions"""
    return [fmt['extension'] for fmt in SUPPORTED_FORMATS.values()]

def get_package_format_by_extension(extension):
    """Get package format info by file extension"""
    for fmt_name, fmt_info in SUPPORTED_FORMATS.items():
        if fmt_info['extension'] == extension.lower():
            return fmt_name, fmt_info
    return None, None

def is_supported_package(filename):
    """Check if filename has a supported package extension"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in get_supported_extensions()

# Initialize configuration directory on import
ensure_config_dir()
