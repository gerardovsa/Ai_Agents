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
    
    # Ensure /data directory exists with proper permissions
    echo "→ Checking /data directory permissions..."
    if [ ! -d "/data" ]; then
        echo "  ERROR: /data directory does not exist!"
        exit 1
    fi
    
    # Make /data writable (Render should handle this, but being explicit)
    chmod 777 /data 2>/dev/null || echo "  Note: Could not chmod /data (may already have correct permissions)"
    
    # Test write permissions
    if touch /data/.write_test 2>/dev/null; then
        rm /data/.write_test
        echo "✓ /data directory is writable"
    else
        echo "  ERROR: /data directory is NOT writable!"
        ls -ld /data
        exit 1
    fi
    
    # Copy database-config.json to persistent disk if it doesn't exist
    if [ ! -f "/data/database-config.json" ]; then
        echo "→ Initializing persistent disk..."
        
        # Try multiple possible locations for the config file
        if [ -f "/app/data/database-config.json" ]; then
            echo "  Copying database-config.json from /app/data to /data"
            cp /app/data/database-config.json /data/database-config.json
        elif [ -f "./data/database-config.json" ]; then
            echo "  Copying database-config.json from ./data to /data"
            cp ./data/database-config.json /data/database-config.json
        else
            echo "  Creating default database-config.json in /data"
            cat > /data/database-config.json << 'EOF'
{
    "database": {
        "type": "sqlite",
        "path": "ai_infrastructure.db"
    },
    "AI": {
        "AnthropicAPIKey": "",
        "Model": "claude-sonnet-4-20250514",
        "MaxTokens": 8096,
        "DeepSeekAPIKey": "",
        "OpenAIAPIKey": ""
    }
}
EOF
        fi
        echo "✓ Persistent disk initialized"
    else
        echo "✓ Persistent disk already initialized"
    fi
    
    # List persistent disk contents
    echo ""
    echo "Persistent Disk Contents (/data):"
    ls -lh /data/ || echo "  (empty)"
    echo ""
    
    # Pre-create database files to avoid disk I/O errors
    echo "→ Initializing database files..."
    for db_file in ai_infrastructure.db sessions.db stock.db; do
        if [ ! -f "/data/$db_file" ]; then
            echo "  Creating /data/$db_file"
            touch "/data/$db_file"
            chmod 666 "/data/$db_file"
        else
            echo "  ✓ /data/$db_file exists"
        fi
    done
    echo ""
    
    # Create config directory for runtime-generated config files
    echo "→ Creating /app/config directory for runtime configs..."
    mkdir -p /app/config
    chmod 777 /app/config
    
    # Copy database-config.json to /app/config if it exists
    if [ -f "/data/database-config.json" ]; then
        echo "  Copying database-config.json to /app/config..."
        cp /data/database-config.json /app/config/database-config.json
    elif [ -f "/app/config/database-config.json" ]; then
        echo "  ✓ database-config.json already in /app/config"
    else
        echo "  Warning: database-config.json not found"
    fi
    
    # Create symlink from root /config to /app/config for backward compatibility
    # This fixes quote calculator tools looking for /config/database-config.json
    echo "→ Creating symlink: /config → /app/config..."
    if [ ! -e "/config" ]; then
        ln -s /app/config /config 2>/dev/null || echo "  Note: Could not create /config symlink (may need root)"
        echo "✓ Symlink created (fixes quote calculator config path)"
    else
        echo "  ✓ /config already exists"
    fi
    
    echo "✓ /app/config directory ready"
    echo ""
else
    echo "✓ Running locally (development)"
fi

# Start Flask application with Gunicorn (production) or Python (development)
if [ "$RENDER" = "true" ]; then
    echo "→ Starting Flask with Gunicorn (production)..."
    echo "  Workers: 2 (1 CPU × 2)"
    echo "  Worker Class: gevent (async I/O)"
    echo "  Max Concurrent: ~100 requests"
    echo "  DB Init: File-locked (prevents WAL race condition)"
    echo ""
    exec gunicorn \
        --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
        --workers 2 \
        --bind 0.0.0.0:$PORT \
        --timeout 120 \
        --keep-alive 5 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        AI_infrastructure.flask_app:app
else
    echo "→ Starting Flask application (development)..."
    exec python AI_infrastructure/flask_app.py
fi
