#!/bin/bash
# Install script for Paimon-server that handles tenacity version conflict
# 
# This script installs dependencies in the correct order to work around
# mega.py's strict tenacity<6.0.0 constraint while using tenacity>=8.0.0
# which is required for Python 3.11+ compatibility.

set -e  # Exit on error

echo "=========================================="
echo "Paimon-server Dependency Installation"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python version: $PYTHON_VERSION"

# Step 1: Install main dependencies (without mega.py)
echo ""
echo "Step 1: Installing main dependencies..."
pip install --constraint constraints.txt \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    gunicorn==22.0.0 \
    python-dotenv==1.0.0 \
    aiofiles==23.2.1 \
    python-multipart==0.0.6 \
    pydantic==2.10.4 \
    pydantic-settings==2.10.1

# Step 2: Install tenacity 8.0.0+ (required for Python 3.11+)
echo ""
echo "Step 2: Installing tenacity>=8.0.0 for Python 3.11+ compatibility..."
pip install 'tenacity>=8.0.0'

# Step 3: Install mega.py dependencies
echo ""
echo "Step 3: Installing mega.py dependencies..."
pip install pycryptodome requests

# Step 4: Install mega.py without dependencies (to avoid tenacity downgrade)
echo ""
echo "Step 4: Installing mega.py (skipping dependencies to preserve tenacity version)..."
pip install --no-deps mega.py==1.0.8

# Verify installation
echo ""
echo "=========================================="
echo "Verifying installation..."
echo "=========================================="

# Check tenacity version
TENACITY_VERSION=$(python3 -c "import importlib.metadata; print(importlib.metadata.version('tenacity'))")
echo "✓ tenacity version: $TENACITY_VERSION"

# Test mega import
if python3 -c "from mega import Mega" 2>/dev/null; then
    echo "✓ mega.Mega import successful"
else
    echo "✗ mega.Mega import failed"
    exit 1
fi

# Test server import
if python3 -c "import server" 2>/dev/null; then
    echo "✓ server module import successful"
else
    echo "✗ server module import failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "You can now run the server with:"
echo "  python3 server.py"
echo ""
echo "Or with gunicorn:"
echo "  gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app"
