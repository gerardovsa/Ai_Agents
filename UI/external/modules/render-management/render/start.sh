#!/bin/bash
# ============================================
# MustCare ValorAISynergySuite Startup Script
# Starts both server and collector services
# ============================================

set -e

echo "🚀 Starting MustCare ValorAISynergySuite V3..."

# Validate critical environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY is required"
    exit 1
fi

if [ -z "$JWT_SECRET" ]; then
    echo "❌ ERROR: JWT_SECRET is required"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  WARNING: DATABASE_URL not set - using SQLite fallback"
fi

echo "✅ Environment validation passed"

# Create storage directories if they don't exist
mkdir -p /app/storage/lancedb
mkdir -p /app/storage/documents
mkdir -p /app/storage/vector-cache
mkdir -p /app/storage/uploads
mkdir -p /app/logs

echo "✅ Storage directories created"

# Start collector in background
echo "🔧 Starting document collector service..."
cd /app/collector
node index.js > /app/logs/collector.log 2>&1 &
COLLECTOR_PID=$!
echo "✅ Collector started (PID: $COLLECTOR_PID)"

# Wait for collector to be ready
echo "⏳ Waiting for collector to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8888/process > /dev/null 2>&1; then
        echo "✅ Collector is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  WARNING: Collector health check timeout (continuing anyway)"
    fi
    sleep 1
done

# Initialize Prisma
echo "🔧 Initializing Prisma client..."
cd /app/server
npx prisma generate
echo "✅ Prisma client generated"

# Push database schema (creates tables if they don't exist)
echo "🔧 Pushing database schema..."
npx prisma db push --accept-data-loss
echo "✅ Database schema pushed"

# Start main server
echo "🔧 Starting main server..."

# Ensure PORT is set (Render uses 10000 by default)
export PORT=${PORT:-10000}
export SERVER_PORT=${PORT}

echo "✅ Server configuration:"
echo "   PORT=$PORT"
echo "   SERVER_PORT=$SERVER_PORT"
echo "   NODE_ENV=$NODE_ENV"
echo "   COLLECTOR_PORT=$COLLECTOR_PORT"

exec node index.js
