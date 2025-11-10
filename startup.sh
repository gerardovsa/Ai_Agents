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
else
    echo "✓ Running locally (development)"
fi

# Start Flask application
echo "→ Starting Flask application..."
exec python AI_infrastructure/flask_app.py
