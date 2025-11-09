#!/bin/bash
# Startup script for Render deployment
# Handles persistent disk initialization

set -e  # Exit on error

echo "========================================="
echo "AI Agents Platform - Startup"
echo "========================================="

# Check if running on Render with persistent disk
if [ "$RENDER" = "true" ]; then
    echo "✓ Running on Render (production)"
    
    # Copy database-config.json to persistent disk if it doesn't exist
    if [ ! -f "/data/database-config.json" ]; then
        echo "→ Initializing persistent disk..."
        echo "  Copying database-config.json to /data"
        cp /app/data/database-config.json /data/database-config.json
        echo "✓ Persistent disk initialized"
    else
        echo "✓ Persistent disk already initialized"
    fi
    
    # List persistent disk contents
    echo ""
    echo "Persistent Disk Contents (/data):"
    ls -lh /data/ || echo "  (empty)"
    echo ""
else
    echo "✓ Running locally (development)"
fi

# Start Flask application
echo "→ Starting Flask application..."
exec python AI_infrastructure/flask_app.py
