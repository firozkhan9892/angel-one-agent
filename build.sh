#!/bin/bash
# Build script for Render deployment

set -e

echo "Installing dependencies..."
pip install --upgrade pip

# Install from root requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt at root"
    pip install -r requirements.txt
else
    echo "ERROR: requirements.txt not found at root!"
    exit 1
fi

echo "Creating necessary directories..."
mkdir -p data logs output backtest_reports dashboard/templates dashboard/static

echo "Build complete!"

