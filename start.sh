#!/usr/bin/env bash
# Start script for Render

echo "🕊️  Starting The London Lark..."
gunicorn app:app --bind 0.0.0.0:$PORT
