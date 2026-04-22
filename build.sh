#!/bin/bash
# Build script for Render deployment

set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r angel_agent/requirements.txt

echo "Creating necessary directories..."
mkdir -p data logs output backtest_reports dashboard/templates dashboard/static

echo "Initializing database..."
python -c "from angel_agent.modules.database import Database; db = Database(); db.close(); print('Database initialized')"

echo "Build complete!"
