"""
Language Module for SnapWiz
Internationalization (i18n) support using gettext
Supported: English, French, German, Spanish, Italian, Russian
"""

import gettext
import os
import json
from pathlib import Path
from . import config

# ==================== PATHS ====================

# Get the application directory (parent of src/)
APP_DIR = Path(__file__).parent.parent.absolute()
LOCALE_DIR = APP_DIR / 'locales'

# ==================== GETTEXT SETUP ====================

# Default language
_current_language = None
_translation = None


def _load_translation(lang_code):
    """Load translation for the given language code"""
    global _translation
    
    # Try JSON-based translation first (simpler, doesn't need msgfmt)
    json_file = LOCALE_DIR / lang_code / 'LC_MESSAGES' / 'snapwiz.json'
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                translations_dict = json.load(f)
                _translation = JSONTranslation(translations_dict)
                return True
        except Exception as e:
            print(f"Warning: Could not load JSON translation for {lang_code}: {e}")
    
    # Try gettext .mo file
    try:
        _translation = gettext.translation(
            'snapwiz',  # Domain name (matches .po file prefix)
            localedir=str(LOCALE_DIR),
            languages=[lang_code],
            fallback=False
        )
        return True
    except FileNotFoundError:
        # Fallback to English
        json_file_en = LOCALE_DIR / 'en' / 'LC_MESSAGES' / 'snapwiz.json'
        if json_file_en.exists():
            try:
                with open(json_file_en, 'r', encoding='utf-8') as f:
                    translations_dict = json.load(f)
                    _translation = JSONTranslation(translations_dict)
                    return True
            except Exception:
                pass
        
        # Use NullTranslations as last resort
        _translation = gettext.NullTranslations()
        return False


class JSONTranslation:
    """Simple translation class using JSON dictionary"""
    
    def __init__(self, translations_dict):
        self.translations = translations_dict
    
    def gettext(self, msgid):
        """Get translation for msgid"""
        return self.translations.get(msgid, msgid)
    
    def ngettext(self, msgid, msgid_plural, n):
        """Get plural translation"""
        # Simple implementation - just use singular/plural based on n
        if n == 1:
            return self.gettext(msgid)
        else:
            return self.translations.get(msgid_plural, msgid_plural)


# ==================== LANGUAGE MANAGER CLASS ====================

class LanguageManager:
    """Manages language translations and preferences using gettext"""
    
    def __init__(self):
        self.current_language = self.load_language_preference()
        self.supported_languages = config.SUPPORTED_LANGUAGES
        self.locale_dir = LOCALE_DIR
        
        # Load the initial language
        self._load_language(self.current_language)
    
    def _load_language(self, language_code):
        """Load translations for the specified language"""
        global _current_language, _translation
        
        _current_language = language_code
        _load_translation(language_code)
    
    def load_language_preference(self):
        """Load saved language preference"""
        try:
            settings_file = config.SETTINGS_FILE
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('language', config.DEFAULT_LANGUAGE)
        except Exception:
            pass
        return config.DEFAULT_LANGUAGE
    
    def save_language_preference(self, language_code):
        """Save language preference"""
        try:
            settings_file = config.SETTINGS_FILE
            settings = {}
            
            # Load existing settings
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # Update language
            settings['language'] = language_code
            
            # Save settings
            config.ensure_config_dir()
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving language preference: {e}")
            return False
    
    def set_language(self, language_code):
        """Set current application language"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            self._load_language(language_code)
            self.save_language_preference(language_code)
            return True
        return False
    
    def get(self, msgid, **kwargs):
        """
        Get translation for a message ID
        
        Args:
            msgid: Message ID (translation key)
            **kwargs: Format parameters for string formatting
            
        Returns:
            Translated string
        """
        global _translation
        
        if _translation is None:
            return msgid
        
        # Get translation
        try:
            translated = _translation.gettext(msgid)
        except Exception:
            translated = msgid
        
        # Apply string formatting if kwargs provided
        if kwargs:
            try:
                return translated.format(**kwargs)
            except (KeyError, ValueError, AttributeError):
                return translated
        
        return translated
    
    def ngettext(self, msgid, msgid_plural, n):
        """
        Get plural translation
        
        Args:
            msgid: Singular form
            msgid_plural: Plural form
            n: Number to determine plural form
            
        Returns:
            Translated string in appropriate plural form
        """
        global _translation
        
        if _translation is None:
            return msgid if n == 1 else msgid_plural
        
        try:
            return _translation.ngettext(msgid, msgid_plural, n)
        except Exception:
            return msgid if n == 1 else msgid_plural
    
    def get_language_name(self, code):
        """Get full language name from code"""
        return self.supported_languages.get(code, code)
    
    def get_available_languages(self):
        """Get list of available languages as (code, name) tuples"""
        return [(code, name) for code, name in self.supported_languages.items()]
    
    def get_current_language(self):
        """Get current language code"""
        return self.current_language


# ==================== GLOBAL INSTANCE ====================

# Create global language manager instance
_language_manager = LanguageManager()


# ==================== CONVENIENCE FUNCTIONS ====================

def _(msgid, **kwargs):
    """
    Convenience function for getting translations
    Usage: _('msg_installation_complete')
           _('msg_files_added', count=5)
    """
    return _language_manager.get(msgid, **kwargs)


def ngettext(msgid, msgid_plural, n):
    """
    Convenience function for plural translations
    Usage: ngettext('file', 'files', count)
    """
    return _language_manager.ngettext(msgid, msgid_plural, n)


def set_language(language_code):
    """Set application language"""
    return _language_manager.set_language(language_code)


def get_current_language():
    """Get current language code"""
    return _language_manager.get_current_language()


def get_available_languages():
    """Get list of available languages"""
    return _language_manager.get_available_languages()


def get_language_manager():
    """Get the language manager instance"""
    return _language_manager


# ==================== COMPILE .PO FILES ====================

def compile_po_files():
    """
    Compile all .po files to .mo files
    This should be run after editing .po files
    """
    import subprocess
    
    compiled_count = 0
    errors = []
    
    # Find all .po files
    for po_file in LOCALE_DIR.rglob('*.po'):
        # Get corresponding .mo file path
        mo_file = po_file.with_suffix('.mo')
        
        try:
            # Compile using msgfmt
            subprocess.run(
                ['msgfmt', '-o', str(mo_file), str(po_file)],
                check=True,
                capture_output=True
            )
            compiled_count += 1
            print(f"✓ Compiled: {po_file.relative_to(LOCALE_DIR)}")
        except subprocess.CalledProcessError as e:
            error_msg = f"✗ Failed to compile {po_file.name}: {e.stderr.decode()}"
            errors.append(error_msg)
            print(error_msg)
        except FileNotFoundError:
            error_msg = "✗ msgfmt not found. Install gettext tools: sudo apt install gettext"
            errors.append(error_msg)
            print(error_msg)
            break
    
    print(f"\nCompilation complete: {compiled_count} files compiled")
    if errors:
        print(f"Errors: {len(errors)}")
    
    return compiled_count, errors


# ==================== HELPER FUNCTIONS ====================

def list_available_locales():
    """List all available locale directories"""
    if not LOCALE_DIR.exists():
        return []
    
    locales = []
    for item in LOCALE_DIR.iterdir():
        if item.is_dir() and (item / 'LC_MESSAGES').exists():
            locales.append(item.name)
    
    return sorted(locales)


def check_locale_health():
    """Check health of locale files"""
    print(f"Locale Directory: {LOCALE_DIR}")
    print(f"Locale Directory Exists: {LOCALE_DIR.exists()}\n")
    
    available_locales = list_available_locales()
    print(f"Available Locales: {', '.join(available_locales)}\n")
    
    for locale in available_locales:
        po_file = LOCALE_DIR / locale / 'LC_MESSAGES' / 'snapwiz.po'
        mo_file = LOCALE_DIR / locale / 'LC_MESSAGES' / 'snapwiz.mo'
        
        print(f"{locale}:")
        print(f"  .po file: {' ✓' if po_file.exists() else '✗'} {po_file.name}")
        print(f"  .mo file: {'✓' if mo_file.exists() else '✗ (needs compilation)'} {mo_file.name}")
        
        if po_file.exists():
            # Check if .mo is older than .po
            if mo_file.exists():
                if po_file.stat().st_mtime > mo_file.stat().st_mtime:
                    print(f"  Warning: .po file is newer than .mo file. Recompile needed!")
        print()


# ==================== AUTO-COMPILE ON IMPORT ====================

def _auto_compile_if_needed():
    """Auto-compile .po files if .mo files are missing or outdated"""
    needs_compile = False
    
    for po_file in LOCALE_DIR.rglob('*.po'):
        mo_file = po_file.with_suffix('.mo')
        
        # Check if .mo doesn't exist or is older than .po
        if not mo_file.exists():
            needs_compile = True
            break
        elif po_file.stat().st_mtime > mo_file.stat().st_mtime:
            needs_compile = True
            break
    
    if needs_compile:
        print("Compiling translation files...")
        try:
            compile_po_files()
        except Exception as e:
            print(f"Auto-compilation failed: {e}")
            print("You may need to run: python -c 'import language; language.compile_po_files()'")


# Try to auto-compile on import (optional, can be disabled)
if os.environ.get('SNAPWIZ_AUTO_COMPILE', '1') == '1':
    try:
        _auto_compile_if_needed()
    except Exception:
        pass  # Silent fail, app will use NullTranslations
