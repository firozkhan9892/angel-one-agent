#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating directories..."
mkdir -p data logs output

echo "Build complete!"

