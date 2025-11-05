#!/usr/bin/env python3
"""
Test script to verify the constraints.txt file works correctly.
This script checks that pathlib from stdlib is used instead of the backport package.
"""
import sys
import pathlib

def test_pathlib_stdlib():
    """Test that pathlib is from the standard library."""
    print(f"Python version: {sys.version}")
    print(f"pathlib module location: {pathlib.__file__}")
    
    # Verify pathlib is from stdlib (should contain 'lib/python' in path)
    if 'site-packages' in pathlib.__file__:
        print("❌ FAILED: pathlib is from a third-party package (site-packages)")
        print("   The constraints.txt file may not be working correctly.")
        return False
    elif 'lib/python' in pathlib.__file__:
        print("✅ PASSED: pathlib is from the Python standard library")
        return True
    else:
        print("⚠️  WARNING: Unable to determine pathlib source")
        return None

if __name__ == "__main__":
    result = test_pathlib_stdlib()
    sys.exit(0 if result else 1)
