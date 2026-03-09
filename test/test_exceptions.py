"""
Unit Tests for Exception System
Tests custom exceptions and error handling
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.exceptions import *
from test.test_utils import assert_exception_message_contains


class TestBaseException(unittest.TestCase):
    """Test SnapWizError base exception"""
    
    def test_basic_exception(self):
        """Test basic exception creation"""
        exc = SnapWizError("Test error")
        self.assertEqual(exc.message, "Test error")
        self.assertIsNone(exc.details)
        self.assertIsNone(exc.suggestion)
    
    def test_exception_with_details(self):
        """Test exception with details"""
        exc = SnapWizError(
            "Test error",
            details="More information",
            suggestion="Try this"
        )
        self.assertEqual(exc.details, "More information")
        self.assertEqual(exc.suggestion, "Try this")
    
    def test_full_message(self):
        """Test get_full_message()"""
        exc = SnapWizError(
            "Error",
            details="Details here",
            suggestion="Suggestion here"
        )
        full_msg = exc.get_full_message()
        self.assertIn("Error", full_msg)
        self.assertIn("Details here", full_msg)
        self.assertIn("Suggestion here", full_msg)


class TestPackageErrors(unittest.TestCase):
    """Test package-related exceptions"""
    
    def test_package_not_found(self):
        """Test PackageNotFoundError"""
        exc = PackageNotFoundError("/path/to/missing.deb")
        self.assertIn("not found", exc.message.lower())
        self.assertIn("missing.deb", exc.message)
        self.assertIsNotNone(exc.suggestion)
    
    def test_invalid_package(self):
        """Test InvalidPackageError"""
        exc = InvalidPackageError(
            "/path/to/corrupt.deb",
            reason="File is corrupted"
        )
        self.assertIn("corrupt.deb", exc.message)
        assert exc.details is not None, "Exception should have details"
        self.assertIn("corrupted", exc.details.lower())
    
    def test_unsupported_format(self):
        """Test UnsupportedPackageFormatError"""
        exc = UnsupportedPackageFormatError(
            "/path/to/file.txt",
            detected_format=".txt"
        )
        self.assertIn(".txt", exc.message)
        assert exc.details is not None, "Exception should have details"
        self.assertIn(".deb", exc.details)  # Should mention supported formats


class TestInstallationErrors(unittest.TestCase):
    """Test installation-related exceptions"""
    
    def test_package_manager_not_found(self):
        """Test PackageManagerNotFoundError"""
        exc = PackageManagerNotFoundError("deb", "apt")
        self.assertIn("apt", exc.message)
        assert exc.suggestion is not None, "Exception should have suggestion"
        self.assertIn("install", exc.suggestion.lower())
    
    def test_dependency_error(self):
        """Test DependencyError"""
        deps = ['lib1', 'lib2', 'lib3']
        exc = DependencyError("mypackage", missing_dependencies=deps)
        self.assertIn("mypackage", exc.message)
        full_msg = exc.get_full_message()
        for dep in deps:
            self.assertIn(dep, full_msg)
    
    def test_installation_timeout(self):
        """Test InstallationTimeoutError"""
        exc = InstallationTimeoutError("package.deb", 300)
        self.assertIn("300", str(exc.message))
        self.assertIn("timeout", exc.message.lower())


class TestErrorHelpers(unittest.TestCase):
    """Test error helper functions"""
    
    def test_get_error_category(self):
        """Test get_error_category()"""
        exc1 = PackageNotFoundError("/test.deb")
        exc2 = NetworkTimeoutError("download", 10)
        exc3 = InsufficientPrivilegesError("install")
        
        self.assertEqual(get_error_category(exc1), "Package Error")
        self.assertEqual(get_error_category(exc2), "Network Error")
        self.assertEqual(get_error_category(exc3), "Permission Error")
    
    def test_get_error_icon(self):
        """Test get_error_icon()"""
        exc1 = PackageNotFoundError("/test.deb")
        exc2 = NetworkTimeoutError("download", 10)
        
        icon1 = get_error_icon(exc1)
        icon2 = get_error_icon(exc2)
        
        self.assertIsInstance(icon1, str)
        self.assertIsInstance(icon2, str)
        self.assertNotEqual(icon1, icon2)  # Different errors, different icons
    
    def test_is_retryable_error(self):
        """Test is_retryable_error()"""
        retryable = NetworkTimeoutError("test", 10)
        not_retryable = PackageNotFoundError("/test.deb")
        
        self.assertTrue(is_retryable_error(retryable))
        self.assertFalse(is_retryable_error(not_retryable))


class TestNetworkErrors(unittest.TestCase):
    """Test network-related exceptions"""
    
    def test_download_error(self):
        """Test DownloadError"""
        exc = DownloadError("https://example.com/file.deb", reason="Connection failed")
        self.assertIn("example.com", exc.message)
        assert exc.details is not None, "Exception should have details"
        self.assertIn("Connection failed", exc.details)
    
    def test_network_timeout(self):
        """Test NetworkTimeoutError"""
        exc = NetworkTimeoutError("file download", 30)
        self.assertIn("timeout", exc.message.lower())
        self.assertIn("30", str(exc.message))


class TestSystemErrors(unittest.TestCase):
    """Test system-related exceptions"""
    
    def test_service_not_running(self):
        """Test ServiceNotRunningError"""
        exc = ServiceNotRunningError("snapd", "snap")
        self.assertIn("snapd", exc.message)
        assert exc.suggestion is not None, "Exception should have suggestion"
        self.assertIn("systemctl", exc.suggestion)
    
    def test_disk_space_error(self):
        """Test DiskSpaceError"""
        exc = DiskSpaceError(required_mb=500, available_mb=100)
        self.assertEqual(exc.required_mb, 500)
        self.assertEqual(exc.available_mb, 100)
        assert exc.details is not None, "Exception should have details"
        self.assertIn("500", exc.details)
        self.assertIn("100", exc.details)


if __name__ == '__main__':
    unittest.main()
