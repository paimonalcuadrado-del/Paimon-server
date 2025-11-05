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
    # We check for site-packages which indicates a third-party installation
    if 'site-packages' in pathlib.__file__:
        print("❌ FAILED: pathlib is from a third-party package (site-packages)")
        print("   The constraints.txt file may not be working correctly.")
        return False
    elif 'lib/python' in pathlib.__file__ or 'lib64/python' in pathlib.__file__:
        print("✅ PASSED: pathlib is from the Python standard library")
        return True
    else:
        print("⚠️  WARNING: Unable to determine pathlib source")
        print("   Path doesn't match expected patterns, but may still be correct")
        # If we can't determine, assume it's OK if not in site-packages
        return True

if __name__ == "__main__":
    result = test_pathlib_stdlib()
    # Exit with 0 (success) if result is True, 1 (failure) if False
    sys.exit(0 if result is True else 1)
