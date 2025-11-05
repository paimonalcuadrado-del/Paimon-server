#!/usr/bin/env python3
"""
Test script to verify tenacity version compatibility with Python 3.11+

This script checks:
1. Python version is 3.11 or higher
2. Tenacity is installed and version is 8.0.0 or higher
3. The mega module can be imported without asyncio.coroutine errors
"""

import sys
import importlib.metadata

def main():
    print("=" * 70)
    print("Tenacity Compatibility Test for Python 3.11+")
    print("=" * 70)
    print()
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {sys.version}")
    
    if python_version < (3, 11):
        print("⚠️  Python version is < 3.11, asyncio.coroutine issue does not apply")
        print("✅ PASSED: No compatibility issues expected")
        return 0
    
    print(f"✓ Python {python_version.major}.{python_version.minor} is >= 3.11")
    print()
    
    # Check if tenacity is installed
    try:
        tenacity_version = importlib.metadata.version('tenacity')
        print(f"Tenacity version: {tenacity_version}")
        
        # Parse version using packaging library for robustness
        try:
            from packaging import version
            parsed_version = version.parse(tenacity_version)
            # Get the major version from the base_version (strips pre-release/dev suffixes)
            major_version = int(str(parsed_version.major))
        except ImportError:
            # Fallback to simple parsing if packaging is not available
            # This handles most common version formats (X.Y.Z)
            major_version = int(tenacity_version.split('.')[0].split('rc')[0].split('dev')[0])
        
        if major_version < 8:
            print(f"❌ FAILED: tenacity {tenacity_version} uses asyncio.coroutine (removed in Python 3.11)")
            print()
            print("Solution:")
            print("  pip uninstall -y tenacity")
            print("  pip install --constraint constraints.txt -r requirements.txt")
            return 1
        else:
            print(f"✓ Tenacity {tenacity_version} is >= 8.0.0 (compatible with Python 3.11+)")
    except importlib.metadata.PackageNotFoundError:
        print("⚠️  Tenacity is not installed")
        print()
        print("Install with:")
        print("  pip install --constraint constraints.txt -r requirements.txt")
        return 1
    
    print()
    
    # Try to import mega module
    print("Testing mega.py import...")
    try:
        from mega import Mega
        print("✓ Successfully imported mega.Mega")
        print()
        print("=" * 70)
        print("✅ PASSED: All tests passed - server should start without errors")
        print("=" * 70)
        return 0
    except AttributeError as e:
        if "asyncio" in str(e) and "coroutine" in str(e):
            print(f"❌ FAILED: {e}")
            print()
            print("This error occurs because tenacity is using asyncio.coroutine")
            print("which was removed in Python 3.11")
            print()
            print("Solution:")
            print("  pip uninstall -y tenacity mega.py")
            print("  pip install --constraint constraints.txt -r requirements.txt")
            return 1
        else:
            raise
    except ImportError as e:
        print(f"⚠️  Could not import mega: {e}")
        print()
        print("This is expected if mega.py is not installed yet.")
        print("Install with:")
        print("  pip install --constraint constraints.txt -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
