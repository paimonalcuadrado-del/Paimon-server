#!/usr/bin/env python3
"""
Demonstration of the asyncio.coroutine issue and fix

This script demonstrates:
1. Why tenacity 5.x fails on Python 3.11+
2. How the constraints.txt fix resolves the issue
"""

import sys

print("=" * 70)
print("Demonstration: asyncio.coroutine AttributeError")
print("=" * 70)
print()
print(f"Python version: {sys.version}")
print()

# Check if asyncio.coroutine exists
import asyncio

print("Checking for asyncio.coroutine attribute...")
if hasattr(asyncio, 'coroutine'):
    print("✓ asyncio.coroutine exists (Python < 3.11)")
    print("  tenacity 5.x will work fine")
else:
    print("✗ asyncio.coroutine does NOT exist (Python >= 3.11)")
    print("  This is expected - the decorator was removed in Python 3.11")
    print()
    print("ISSUE:")
    print("  tenacity 5.1.5 uses @asyncio.coroutine decorator")
    print("  This causes AttributeError when importing tenacity on Python 3.11+")
    print()
    print("SOLUTION:")
    print("  Use tenacity >= 8.0.0 which uses modern async/await syntax")
    print("  The constraints.txt file forces tenacity>=8.0.0:")
    print()
    print("    # constraints.txt")
    print("    tenacity>=8.0.0")
    print()
    print("  Install command:")
    print("    pip install --constraint constraints.txt -r requirements.txt")

print()
print("=" * 70)
print(f"Status: Python {sys.version_info.major}.{sys.version_info.minor} " + 
      ("requires" if sys.version_info >= (3, 11) else "does not require") + 
      " tenacity >= 8.0.0")
print("=" * 70)
