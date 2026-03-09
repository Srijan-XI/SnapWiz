# SnapWiz Testing Guide

**Version:** 1.4.1  
**Last Updated:** 2026-02-09  
**Test Framework:** Python unittest

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Coverage](#test-coverage)
6. [Continuous Integration](#continuous-integration)

---

## Overview

SnapWiz uses Python's built-in `unittest` framework for automated testing. The test suite covers:

- ✅ Configuration module
- ✅ Exception system
- ✅ Package handler (planned)
- ✅ Language system (planned)
- ✅ Logger (planned)
- ✅ Retry utilities (planned)

---

## Test Structure

```
test/
├── __init__.py                  # Test package initialization
├── test_utils.py                # Common utilities and fixtures
├── run_tests.py                 # Test runner script
│
├── test_config.py               # Configuration tests
├── test_exceptions.py           # Exception system tests
├── test_package_handler.py      # Package handler tests (TODO)
├── test_language.py             # Language/i18n tests (TODO)
├── test_logger.py               # Logger tests (TODO)
├── test_retry_utils.py          # Retry logic tests (TODO)
│
└── TESTING_GUIDE.md             # This file
```

---

## Running Tests

### Run All Tests

```bash
# From project root
python -m test.run_tests

# Or directly
cd test
python run_tests.py
```

### Run Specific Test Module

```bash
# Run only config tests
python -m test.run_tests test_config

# Run only exception tests
python -m test.run_tests test_exceptions

# Run multiple specific modules
python -m test.run_tests test_config test_exceptions
```

### Run with Different Verbosity

```bash
# Verbose output
python -m test.run_tests -v

# Quiet output (only summary)
python -m test.run_tests -q
```

### Run Single Test Class

```bash
# Run specific test class
python -m unittest test.test_config.TestConfigConstants

# Run specific test method
python -m unittest test.test_config.TestConfigConstants.test_app_info
```

---

## Writing Tests

### Test File Template

```python
"""
Unit Tests for [Module Name]
Description of what this tests
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.module_name import SomeClass
from test.test_utils import TestEnvironment, MockCallback


class TestClassName(unittest.TestCase):
    """Test description"""
    
    def setUp(self):
        """Run before each test"""
        self.env = TestEnvironment()
        self.env.setup()
    
    def tearDown(self):
        """Run after each test"""
        self.env.teardown()
    
    def test_something(self):
        """Test description"""
        # Arrange
        input_value = "test"
        expected = "TEST"
        
        # Act
        result = input_value.upper()
        
        # Assert
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
```

### Using Test Utilities

```python
from test.test_utils import (
    TestEnvironment,
    MockCallback,
    create_mock_package,
    assert_file_exists
)

class TestExample(unittest.TestCase):
    
    def test_with_temp_files(self):
        """Test using temporary files"""
        env = TestEnvironment()
        env.setup()
        
        # Create test file
        test_file = env.create_test_file('package.deb')
        assert_file_exists(test_file)
        
        # Cleanup
        env.teardown()
    
    def test_with_mock_callback(self):
        """Test using mock callback"""
        callback = MockCallback()
        
        # Call function with callback
        function_that_uses_callback(callback=callback)
        
        # Check callback was called
        self.assertTrue(callback.was_called())
        self.assertEqual(callback.get_call_count(), 3)
```

### Test Naming Conventions

**File names:**
- `test_[module_name].py` - e.g., `test_config.py`

**Class names:**
- `Test[FeatureName]` - e.g., `TestConfigConstants`

**Method names:**
- `test_[what_is_tested]` - e.g., `test_app_info`
- Use descriptive names that explain what is being tested
- Use underscores for readability

---

## Test Coverage

### Current Coverage

| Module | Coverage | Tests | Status |
|--------|----------|-------|--------|
| **config.py** | ~80% | 15 | ✅ Complete |
| **exceptions.py** | ~85% | 20 | ✅ Complete |
| **package_handler.py** | 0% | 0 | 🚧 TODO |
| **language.py** | 0% | 0 | 🚧 TODO |
| **logger.py** | 0% | 0 | 🚧 TODO |
| **retry_utils.py** | 0% | 0 | 🚧 TODO |

### Measuring Coverage

Install coverage tool:
```bash
pip install coverage
```

Run tests with coverage:
```bash
# Run tests
coverage run -m test.run_tests

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

---

## Test Categories

### Unit Tests
Test individual functions/classes in isolation

**Location:** `test/test_*.py`  
**Examples:**
- `test_config.py` - Test config constants and helpers
- `test_exceptions.py` - Test exception creation and messages

### Integration Tests (Planned)
Test interaction between multiple components

**Location:** `test/integration/` (to be created)  
**Examples:**
- Test package installation flow
- Test language switching with UI
- Test error handling across modules

### Functional Tests (Planned)
Test complete user workflows

**Location:** `test/functional/` (to be created)  
**Examples:**
- Install package end-to-end
- View history
- Change settings

---

## Assertions Reference

### Common Assertions

```python
# Equality
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# Truth
self.assertTrue(x)
self.assertFalse(x)

# Presence
self.assertIn(item, container)
self.assertNotIn(item, container)

# Identity
self.assertIs(a, b)
self.assertIsNot(a, b)

# None
self.assertIsNone(x)
self.assertIsNotNone(x)

# Types
self.assertIsInstance(obj, type)
self.assertNotIsInstance(obj, type)

# Exceptions
self.assertRaises(ExceptionType, callable, *args)
with self.assertRaises(ExceptionType):
    # code that should raise

# Comparisons
self.assertGreater(a, b)
self.assertGreaterEqual(a, b)
self.assertLess(a, b)
self.assertLessEqual(a, b)
```

### Custom Assertions (from test_utils)

```python
from test.test_utils import (
    assert_file_exists,
    assert_file_not_exists,
    assert_is_file,
    assert_is_directory,
    assert_exception_message_contains
)

# File assertions
assert_file_exists('/path/to/file')
assert_file_not_exists('/path/to/missing')
assert_is_file('/path/to/file')
assert_is_directory('/path/to/dir')

# Exception assertions
try:
    raise ValueError("Test error message")
except ValueError as e:
    assert_exception_message_contains(e, "error message")
```

---

## Testing Best Practices

### 1. Test Independence
Each test should be independent and not rely on other tests

```python
# Good
def test_something(self):
    data = create_test_data()  # Create own data
    result = process(data)
    self.assertEqual(result, expected)

# Bad (depends on class state)
def test_first(self):
    self.data = create_test_data()  # Sets class state

def test_second(self):
    result = process(self.data)  # Depends on test_first
```

### 2. Use setUp and tearDown

```python
def setUp(self):
    """Run before each test"""
    self.temp_dir = tempfile.mkdtemp()

def tearDown(self):
    """Run after each test"""
    shutil.rmtree(self.temp_dir)
```

### 3. Test One Thing at a Time

```python
# Good - tests one specific thing
def test_package_validation_rejects_empty_files(self):
    empty_file = create_empty_file()
    with self.assertRaises(InvalidPackageError):
        validate_package(empty_file)

# Bad - tests multiple things
def test_package_validation(self):
    # Tests too many scenarios in one test
    ...
```

### 4. Use Descriptive Names

```python
# Good
def test_install_package_raises_error_when_file_not_found(self):
    ...

# Bad
def test_install(self):
    ...
```

### 5. Arrange-Act-Assert Pattern

```python
def test_example(self):
    # Arrange - setup test data
    package_file = create_mock_package('deb')
    handler = PackageHandler()
    
    # Act - perform the action
    result = handler.validate_package(package_file)
    
    # Assert - verify the outcome
    self.assertTrue(result)
```

---

## Mocking and Fixtures

### Using Mock Objects

```python
from unittest.mock import Mock, patch

def test_with_mock(self):
    # Create mock
    mock_handler = Mock()
    mock_handler.install.return_value = (True, "Success")
    
    # Use mock
    success, message = mock_handler.install('/path/to/package.deb')
    
    # Verify
    self.assertTrue(success)
    mock_handler.install.assert_called_once()
```

### Patching

```python
@patch('src.package_handler.subprocess.run')
def test_with_patch(self, mock_run):
    # Setup mock return value
    mock_run.return_value.returncode = 0
    
    # Run test
    handler = PackageHandler()
    result = handler.install_package('/test.deb')
    
    # Verify subprocess was called
    mock_run.assert_called()
```

---

## Continuous Integration

### GitHub Actions (Coming Soon)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests
      run: |
        python -m test.run_tests
    
    - name: Generate coverage report
      run: |
        coverage run -m test.run_tests
        coverage report
```

---

## Adding New Tests

### Step-by-Step Guide

**1. Create test file:**
```bash
touch test/test_new_module.py
```

**2. Write tests:**
```python
import unittest
from src.new_module import NewClass

class TestNewClass(unittest.TestCase):
    def test_something(self):
        obj = NewClass()
        result = obj.method()
        self.assertTrue(result)
```

**3. Add to test runner:**
Edit `test/run_tests.py`:
```python
test_modules = [
    'test_config',
    'test_exceptions',
    'test_new_module',  # Add here
]
```

**4. Run tests:**
```bash
python -m test.run_tests
```

---

## Troubleshooting

### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'src'

# Solution: Run from project root
cd /path/to/SnapWiz
python -m test.run_tests
```

### Path Issues

```python
# Add this at top of test files
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

### Test Failures

```bash
# Run with verbose output
python -m test.run_tests -v

# Run specific failing test
python -m unittest test.test_config.TestConfigConstants.test_app_info
```

---

## Interactive Notebook Tests

SnapWiz now includes Jupyter Notebooks (`.ipynb`) for interactive and visual testing.

### Location
`test/notebook/` contains:
- `test_config.ipynb` - Visual configuration inspection
- `test_exceptions.ipynb` - Exception hierarchy visualization
- `test_retry_utils.ipynb` - Real-time retry logic demos

### Running Notebooks
1. Ensure `jupyter`, `pandas`, and `matplotlib` are installed.
2. Navigate to `test/notebook/`.
3. Run `jupyter notebook`.
4. Open any `.ipynb` file to run interactive tests.

---

## Future Enhancements

- [ ] Add integration tests
- [ ] Add functional tests
- [ ] Set up CI/CD pipeline
- [ ] Increase code coverage to 90%+
- [ ] Add performance tests
- [ ] Add GUI tests with pytest-qt
- [ ] Generate HTML coverage reports
- [ ] Add test for all modules

---

## Quick Reference

### Run Commands

```bash
# All tests
python -m test.run_tests

# Specific module
python -m test.run_tests test_config

# With coverage
coverage run -m test.run_tests
coverage report

# Single test
python -m unittest test.test_config.TestConfigConstants
```

### Common Patterns

```python
# Setup/Teardown
def setUp(self): ...
def tearDown(self): ...

# Test exceptions
with self.assertRaises(ExceptionType):
    code_that_raises()

# Mock callback
callback = MockCallback()
function(callback=callback)
self.assertTrue(callback.was_called())

# Temp files
env = TestEnvironment()
file_path = env.create_test_file('test.deb')
```

---

**Testing Guide Version:** 1.4.1  
**Last Updated:** 2026-02-09  
**Framework:** Python unittest  

**Happy Testing! ✅🧪**
