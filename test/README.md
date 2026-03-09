# SnapWiz Test Suite

**Version:** 1.4.1  
**Framework:** Python unittest  
**Coverage:** ~35% (growing)

---

## 📁 Test Structure

```
test/
├── __init__.py              # Test package init
├── test_utils.py            # Common utilities and fixtures
├── run_tests.py             # Test runner script
│
├── test_config.py           # ✅ Configuration tests (15 tests)
├── test_exceptions.py       # ✅ Exception system tests (20 tests)
│
├── TESTING_GUIDE.md         # Complete testing documentation
└── README.md                # This file
```

---

## 🚀 Quick Start

### Run All Tests
```bash
# From project root
python -m test.run_tests

# With verbose output
python -m test.run_tests -v
```

### Run Specific Tests
```bash
# Run config tests only
python -m test.run_tests test_config

# Run exception tests only
python -m test.run_tests test_exceptions
```

### Run with Coverage
```bash
coverage run -m test.run_tests
coverage report
coverage html  # Generate HTML report
```

---

## ✅ Current Test Coverage

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| **config.py** | 15 | ~80% | ✅ Complete |
| **exceptions.py** | 20 | ~85% | ✅ Complete |
| **package_handler.py** | 0 | 0% | 🚧 TODO |
| **language.py** | 0 | 0% | 🚧 TODO |
| **logger.py** | 0 | 0% | 🚧 TODO |
| **retry_utils.py** | 0 | 0% | 🚧 TODO |
| **Total** | **35** |**~35%** | 🚧 In Progress |

---

## 📚 Documentation

For complete testing documentation, see:
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Comprehensive testing guide
  - Test structure
  - Running tests
  - Writing tests
  - Best practices
  - Assertions reference
  - CI/CD setup

---

## 🛠️ Test Utilities

### TestEnvironment
Helper for managing temporary test files and directories:

```python
from test.test_utils import TestEnvironment

env = TestEnvironment()
env.setup()

# Create test file
test_file = env.create_test_file('package.deb')

# Cleanup
env.teardown()
```

### MockCallback
Mock callback for testing progress updates:

```python
from test.test_utils import MockCallback

callback = MockCallback()
function_with_callback(callback=callback)

# Verify
assert callback.was_called()
assert callback.get_call_count() == 3
```

### create_mock_package
Create mock package files for testing:

```python
from test.test_utils import create_mock_package

deb_file = create_mock_package('deb')
rpm_file = create_mock_package('rpm')
```

---

## 🎯 Test Categories

### Unit Tests (Current)
- `test_config.py` - Configuration module
- `test_exceptions.py` - Exception system

### Integration Tests (Planned)
- Test interaction between modules
- End-to-end workflows

### Functional Tests (Planned)
- Complete user scenarios
- GUI testing with pytest-qt

---

## 📝 Writing New Tests

### 1. Create test file
```bash
touch test/test_new_module.py
```

### 2. Write tests
```python
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.new_module import NewClass

class TestNewClass(unittest.TestCase):
    def test_something(self):
        obj = NewClass()
        result = obj.method()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```

### 3. Add to test runner
Edit `run_tests.py` to include your new test module.

### 4. Run tests
```bash
python -m test.run_tests
```

---

## 🔧 Installation

### Install Test Dependencies

```bash
# Using venv (recommended)
venv/bin/pip install coverage pytest pytest-cov

# Or during install.sh
# Choose "yes" when prompted for test dependencies
```

---

## 📊 Running Tests During Installation

The `install.sh` script now includes optional test setup:

```bash
./install.sh
```

You'll be prompted:
1. **Install test dependencies?** (y/n)
   - Installs coverage, pytest, pytest-cov
2. **Run tests now?** (y/n)
   - Runs full test suite

---

## 🎓 Learning Resources

### Official Documentation
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [pytest](https://docs.pytest.org/)

### Best Practices
- Test one thing per test method
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Keep tests independent
- Use setUp/tearDown for common setup

---

## 🚧 TODO

- [ ] Add package_handler tests
- [ ] Add language system tests
- [ ] Add logger tests
- [ ] Add retry_utils tests
- [ ] Add integration tests
- [ ] Add GUI tests (pytest-qt)
- [ ] Set up CI/CD pipeline
- [ ] Increase coverage to 90%+
- [ ] Add performance tests

---

## 💡 Tips

### Quick Commands

```bash
# Run all tests
python -m test.run_tests

# Run with verbose
python -m test.run_tests -v

# Run specific module
python -m test.run_tests test_config

# Run single test class
python -m unittest test.test_config.TestConfigConstants

# Run with coverage
coverage run -m test.run_tests
coverage report -m

# Generate HTML report
coverage html
# Open htmlcov/index.html
```

### Debugging Failed Tests

```bash
# Run with verbose output
python -m test.run_tests -v

# Run specific failing test
python -m unittest test.test_exceptions.TestPackageErrors.test_package_not_found

# Add print() statements in tests for debugging
```

---

## 📞 Need Help?

- **Read:** [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive documentation
- **Examples:** Look at existing test files for patterns
- **Ask:** Open an issue on GitHub

---

**Happy Testing! ✅🧪**

*"Testing leads to failure, and failure leads to understanding." - Burt Rutan*
