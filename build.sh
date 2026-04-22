#!/bin/bash
# Build script for Render deployment

set -e

echo "Installing dependencies..."
pip install --upgrade pip

# Try both locations for requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "angel_agent/requirements.txt" ]; then
    pip install -r angel_agent/requirements.txt
else
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

echo "Creating necessary directories..."
mkdir -p data logs output backtest_reports dashboard/templates dashboard/static

echo "Initializing database..."
python -c "from modules.database import Database; db = Database(); db.close(); print('Database initialized')" 2>/dev/null || echo "Database initialization skipped"

echo "Build complete!"
