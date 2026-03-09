#!/usr/bin/env python3
"""
SnapWiz Test Runner
Run all or specific test suites
"""

import sys
import os
import unittest
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test.test_utils import run_test_suite


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run SnapWiz tests')
    parser.add_argument(
        'tests',
        nargs='*',
        help='Specific test modules to run (e.g., test_config test_exceptions)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet output'
    )
    
    args = parser.parse_args()
    
    # Determine verbosity
    verbosity = 1
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 0
    
    # Get test modules
    if args.tests:
        test_modules = args.tests
    else:
        # Run all tests
        test_modules = [
            'test_config',
            'test_exceptions',
            # Add more test modules here as they're created
        ]
    
    print("=" * 70)
    print("SnapWiz Test Suite")
    print("=" * 70)
    print(f"\nRunning {len(test_modules)} test module(s):\n")
    
    # Load and run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            # Import test module
            if not module_name.startswith('test.'):
                module_name = f'test.{module_name}'
            
            module = __import__(module_name, fromlist=[module_name.split('.')[-1]])
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            print(f"  ✓ Loaded: {module_name}")
        except ImportError as e:
            print(f"  ✗ Failed to load {module_name}: {e}")
    
    print()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run:    {result.testsRun}")
    print(f"Passed:       {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed:       {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print("=" * 70)
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
