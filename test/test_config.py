"""
Unit Tests for Configuration Module
Tests config.py settings and utilities
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import config


class TestConfigConstants(unittest.TestCase):
    """Test configuration constants"""
    
    def test_app_info(self):
        """Test application information"""
        self.assertIsInstance(config.APP_NAME, str)
        self.assertIsInstance(config.APP_VERSION, str)
        self.assertIsInstance(config.APP_AUTHOR, str)
        self.assertTrue(len(config.APP_NAME) > 0)
    
    def test_window_settings(self):
        """Test window configuration"""
        self.assertIsInstance(config.WINDOW_WIDTH, int)
        self.assertIsInstance(config.WINDOW_HEIGHT, int)
        self.assertGreater(config.WINDOW_WIDTH, 0)
        self.assertGreater(config.WINDOW_HEIGHT, 0)
    
    def test_installation_settings(self):
        """Test installation timeouts"""
        self.assertIsInstance(config.INSTALLATION_TIMEOUT, int)
        self.assertGreater(config.INSTALLATION_TIMEOUT, 0)


class TestSupportedFormats(unittest.TestCase):
    """Test package format configuration"""
    
    def test_supported_formats_exists(self):
        """Test SUPPORTED_FORMATS dict exists"""
        self.assertIsInstance(config.SUPPORTED_FORMATS, dict)
        self.assertGreater(len(config.SUPPORTED_FORMATS), 0)
    
    def test_deb_format(self):
        """Test .deb format configuration"""
        self.assertIn('deb', config.SUPPORTED_FORMATS)
        deb_config = config.SUPPORTED_FORMATS['deb']
        self.assertEqual(deb_config['extension'], '.deb')
        self.assertIn('managers', deb_config)
        self.assertIn('install_commands', deb_config)
    
    def test_rpm_format(self):
        """Test .rpm format configuration"""
        self.assertIn('rpm', config.SUPPORTED_FORMATS)
        rpm_config = config.SUPPORTED_FORMATS['rpm']
        self.assertEqual(rpm_config['extension'], '.rpm')
    
    def test_snap_format(self):
        """Test .snap format configuration"""
        self.assertIn('snap', config.SUPPORTED_FORMATS)
        snap_config = config.SUPPORTED_FORMATS['snap']
        self.assertEqual(snap_config['extension'], '.snap')
    
    def test_flatpak_format(self):
        """Test .flatpak format configuration"""
        self.assertIn('flatpak', config.SUPPORTED_FORMATS)
        flatpak_config = config.SUPPORTED_FORMATS['flatpak']
        self.assertEqual(flatpak_config['extension'], '.flatpak')


class TestConfigHelpers(unittest.TestCase):
    """Test configuration helper functions"""
    
    def test_get_supported_extensions(self):
        """Test get_supported_extensions()"""
        extensions = config.get_supported_extensions()
        self.assertIsInstance(extensions, list)
        self.assertIn('.deb', extensions)
        self.assertIn('.rpm', extensions)
        self.assertIn('.snap', extensions)
        self.assertIn('.flatpak', extensions)
    
    def test_get_package_format_by_extension(self):
        """Test get_package_format_by_extension()"""
        deb_format = config.get_package_format_by_extension('.deb')
        self.assertIsInstance(deb_format, dict)
        self.assertEqual(deb_format['extension'], '.deb')
        
        # Test case insensitivity
        deb_upper = config.get_package_format_by_extension('.DEB')
        self.assertEqual(deb_upper['extension'], '.deb')
    
    def test_is_supported_package(self):
        """Test is_supported_package()"""
        self.assertTrue(config.is_supported_package('test.deb'))
        self.assertTrue(config.is_supported_package('test.rpm'))
        self.assertTrue(config.is_supported_package('test.snap'))
        self.assertTrue(config.is_supported_package('test.flatpak'))
        
        # Test unsupported
        self.assertFalse(config.is_supported_package('test.txt'))
        self.assertFalse(config.is_supported_package('test.exe'))
        
        # Test case insensitivity
        self.assertTrue(config.is_supported_package('test.DEB'))


class TestLanguageConfig(unittest.TestCase):
    """Test language configuration"""
    
    def test_supported_languages(self):
        """Test SUPPORTED_LANGUAGES dict"""
        self.assertIsInstance(config.SUPPORTED_LANGUAGES, dict)
        self.assertGreater(len(config.SUPPORTED_LANGUAGES), 0)
        
        # Check for core languages
        self.assertIn('en', config.SUPPORTED_LANGUAGES)
        self.assertEqual(config.SUPPORTED_LANGUAGES['en'], 'English')
    
    def test_default_language(self):
        """Test DEFAULT_LANGUAGE"""
        self.assertIsInstance(config.DEFAULT_LANGUAGE, str)
        self.assertIn(config.DEFAULT_LANGUAGE, config.SUPPORTED_LANGUAGES)


class TestThemeConfig(unittest.TestCase):
    """Test theme configuration"""
    
    def test_theme_exists(self):
        """Test theme configuration exists"""
        self.assertIsInstance(config.THEMES, dict)
        self.assertIn('light', config.THEMES)
        self.assertIn('dark', config.THEMES)
    
    def test_light_theme(self):
        """Test light theme colors"""
        light = config.THEMES['light']
        self.assertIn('background', light)
        self.assertIn('text', light)
        self.assertIsInstance(light['background'], str)
    
    def test_dark_theme(self):
        """Test dark theme colors"""
        dark = config.THEMES['dark']
        self.assertIn('background', dark)
        self.assertIn('text', dark)
        self.assertIsInstance(dark['background'], str)


class TestPaths(unittest.TestCase):
    """Test path configuration"""
    
    def test_config_dir(self):
        """Test CONFIG_DIR path"""
        from pathlib import Path
        self.assertIsInstance(config.CONFIG_DIR, Path)
    
    def test_settings_file(self):
        """Test SETTINGS_FILE path"""
        from pathlib import Path
        self.assertIsInstance(config.SETTINGS_FILE, Path)
        self.assertTrue(str(config.SETTINGS_FILE).endswith('.json'))


if __name__ == '__main__':
    unittest.main()
