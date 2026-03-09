"""
Test Utilities for SnapWiz Test Suite
Common functions and fixtures for testing
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestEnvironment:
    """Setup and teardown test environment"""
    
    def __init__(self):
        self.temp_dir = None
        self.test_files = []
    
    def setup(self):
        """Create temporary test directory"""
        self.temp_dir = tempfile.mkdtemp(prefix='snapwiz_test_')
        return self.temp_dir
    
    def teardown(self):
        """Clean up test directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.temp_dir = None
        self.test_files = []
    
    def create_test_file(self, filename, content=b'test', size_bytes=None):
        """Create a test file with optional content and size"""
        if not self.temp_dir:
            self.setup()
        
        assert self.temp_dir is not None, "Temp directory not initialized"
        filepath = os.path.join(self.temp_dir, filename)
        
        with open(filepath, 'wb') as f:
            if size_bytes:
                # Create file of specific size
                f.write(b'0' * size_bytes)
            else:
                f.write(content)
        
        self.test_files.append(filepath)
        return filepath
    
    def get_temp_dir(self):
        """Get temporary directory path"""
        if not self.temp_dir:
            self.setup()
        return self.temp_dir


def create_mock_package(package_type='deb', temp_dir=None):
    """
    Create a mock package file for testing
    
    Args:
        package_type: Type of package (deb, rpm, snap, flatpak)
        temp_dir: Directory to create file in
    
    Returns:
        Path to created file
    """
    if temp_dir is None:
        temp_dir = tempfile.gettempdir()
    
    extensions = {
        'deb': '.deb',
        'rpm': '.rpm',
        'snap': '.snap',
        'flatpak': '.flatpak'
    }
    
    ext = extensions.get(package_type, '.deb')
    filename = f'test_package{ext}'
    filepath = os.path.join(temp_dir, filename)
    
    # Create a dummy file
    with open(filepath, 'wb') as f:
        f.write(b'MOCK_PACKAGE_DATA')
    
    return filepath


def assert_exception_message_contains(exception, text):
    """Assert that exception message contains specific text"""
    message = str(exception)
    assert text.lower() in message.lower(), \
        f"Expected '{text}' in exception message, got: {message}"


def assert_file_exists(filepath):
    """Assert that a file exists"""
    assert os.path.exists(filepath), f"File not found: {filepath}"


def assert_file_not_exists(filepath):
    """Assert that a file does not exist"""
    assert not os.path.exists(filepath), f"File should not exist: {filepath}"


def assert_is_file(filepath):
    """Assert that path is a file"""
    assert os.path.isfile(filepath), f"Not a file: {filepath}"


def assert_is_directory(dirpath):
    """Assert that path is a directory"""
    assert os.path.isdir(dirpath), f"Not a directory: {dirpath}"


class MockCallback:
    """Mock callback for testing progress updates"""
    
    def __init__(self):
        self.calls = []
    
    def __call__(self, *args, **kwargs):
        """Record callback invocation"""
        self.calls.append({
            'args': args,
            'kwargs': kwargs
        })
    
    def get_call_count(self):
        """Get number of times callback was called"""
        return len(self.calls)
    
    def get_last_call(self):
        """Get last callback invocation"""
        return self.calls[-1] if self.calls else None
    
    def was_called(self):
        """Check if callback was called at least once"""
        return len(self.calls) > 0
    
    def reset(self):
        """Reset callback history"""
        self.calls = []


def run_test_suite(test_modules):
    """
    Run a suite of test modules
    
    Args:
        test_modules: List of test module names
    
    Returns:
        Tuple of (passed, failed, errors)
    """
    import unittest
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(f'test.{module_name}', fromlist=[module_name])
            suite.addTests(loader.loadTestsFromModule(module))
        except ImportError as e:
            print(f"Warning: Could not import test module {module_name}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return (
        result.testsRun - len(result.failures) - len(result.errors),
        len(result.failures),
        len(result.errors)
    )


# Test data constants
VALID_EXTENSIONS = ['.deb', '.rpm', '.snap', '.flatpak']
INVALID_EXTENSIONS = ['.txt', '.exe', '.zip', '.tar.gz']

MOCK_PACKAGE_INFO = {
    'name': 'test-package',
    'version': '1.0.0',
    'architecture': 'amd64',
    'description': 'Test package for unit testing'
}
