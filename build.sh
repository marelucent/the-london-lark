#!/usr/bin/env bash
# Build script for Render deployment

echo "🕊️  Building The London Lark..."

# Install Python dependencies
pip install -r requirements.txt

# Build the database from JSON
echo "📊 Building database from venues JSON..."
python import_lark_to_sqlite.py

echo "✅ Build complete!"
