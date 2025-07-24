#!/usr/bin/env python3
"""
Test runner for cfgone package.
Run this script to execute all tests.
"""

import unittest
import sys
import os

if __name__ == "__main__":

    # Add the parent directory to Python path so we can import cfgone
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
