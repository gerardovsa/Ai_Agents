#!/bin/bash
# ============================================
# MustCare ValorAISynergySuite Minimal Startup
# Starts ONLY the server (no collector)
# ============================================

set -e

echo "🚀 Starting MustCare ValorAISynergySuite (MINIMAL MODE)..."

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

echo "⚠️  COLLECTOR DISABLED - Document processing not available"
echo "   This is a minimal deployment for testing"

# Start server (main application)
echo "🌐 Starting Express server..."
cd /app/server

# Run database migrations if needed
if [ -f "prisma/schema.prisma" ]; then
    echo "🔧 Running database migrations..."
    npx prisma migrate deploy || echo "⚠️  Migration skipped"
fi

echo "✅ Server starting on port ${PORT:-3001}..."
exec node index.js
