"""
SnapWiz - The Magical Package Installer
Core source package
"""

__version__ = "1.4.0"
__author__ = "Srijan-XI"

# Import commonly used items for convenience
from .config import *
from .exceptions import SnapWizError
from .language import _, get_current_language, set_language

__all__ = [
    'config',
    'package_handler',
    'logger',
    'language',
    'exceptions',
    'retry_utils',
    'SnapWizError',
    '_',
    'get_current_language',
    'set_language',
]
