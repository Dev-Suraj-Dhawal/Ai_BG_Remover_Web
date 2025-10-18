#!/bin/bash
# Build script for AI Background Remover Web App
# Pre-downloads the rembg model during build to avoid startup delays on Render

set -e  # Exit on any error

echo "========================================="
echo "Starting build process for AI Background Remover..."
echo "========================================="

echo ""
echo "Step 1: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Pre-downloading rembg u2net model..."
echo "This will cache the model (~176MB) to avoid startup delays on Render"

python3 << 'END'
from rembg import new_session
import sys

try:
    print("Downloading u2net model...")
    session = new_session('u2net')
    print("✓ Model downloaded and cached successfully!")
    sys.exit(0)
except Exception as e:
    print(f"✗ Failed to download model: {e}")
    sys.exit(1)
END

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "Model is ready for instant startup."
echo "========================================="
