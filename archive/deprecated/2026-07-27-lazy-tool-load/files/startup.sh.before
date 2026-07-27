#!/bin/bash
# Startup script for Render deployment
# Handles persistent disk initialization

set -e  # Exit on error

# ============================================================================
# STARTUP_TIMING ANCHOR (added 2026-07-23 — startup phase diagnostics)
# ----------------------------------------------------------------------------
# The Python helper AI_infrastructure/shared/startup_timing.py anchors its
# _BOOT_T0 at *its own* import time, which is several hundred ms into the
# gunicorn worker process startup. To capture the shell-side phases that
# happen *before* Python starts (persistent disk prep, cache dirs, config
# symlink, db file placeholders), we anchor here at the very top of this
# script. The lines emitted with the [STARTUP_TIMING] tag are greppable
# from Render's stdout (and from `gunicorn --access-logfile -`).
# ============================================================================
SHELL_T0_NS=$(date +%s%N)
emit_startup_timing() {
    # Usage: emit_startup_timing <phase_id> <note>
    local phase_id="$1"
    local note="$2"
    local now_ns
    now_ns=$(date +%s%N)
    local dt_ms=$(( (now_ns - SHELL_T0_NS) / 1000000 ))
    local wall
    wall=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    # Single-line printf keeps the line atomic from grep's perspective.
    printf '[STARTUP_TIMING] phase=%s status=ok dt_ms=%d total_ms=%d wall=%s note="%s"\n' \
        "$phase_id" "$dt_ms" "$dt_ms" "$wall" "$note"
}

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

    # OPTIONAL: Copy database-config.json to persistent disk if available
    # NOTE: This file is NO LONGER REQUIRED - Flask auto-creates from environment variables
    # Only needed for legacy compatibility (quote-calculator module, disabled in production)
    if [ ! -f "/data/database-config.json" ]; then
        echo "→ Checking for database-config.json (optional)..."

        # Try multiple possible locations for the config file
        if [ -f "/app/data/database-config.json" ]; then
            echo "  ✓ Found database-config.json in /app/data, copying to /data"
            cp /app/data/database-config.json /data/database-config.json
        elif [ -f "./data/database-config.json" ]; then
            echo "  ✓ Found database-config.json in ./data, copying to /data"
            cp ./data/database-config.json /data/database-config.json
        else
            echo "  ℹ️  database-config.json not found (OK - will be auto-created from environment variables)"
            echo "  Creating minimal placeholder in /data"
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
        echo "  ✓ Config placeholder created (Flask will populate from environment variables)"
    else
        echo "  ✓ database-config.json already exists in /data"
    fi

    # ========================================
    # CACHE INITIALIZATION (Build Time Optimization)
    # ========================================
    echo "→ Initializing cache directories..."

    # Create all cache directories with proper permissions
    mkdir -p /data/.cache/pip \
             /data/.cache/torch \
             /data/.cache/huggingface \
             /data/.cache/whisper \
             /data/.cache/numpy \
             /data/.cache/matplotlib \
             /data/.cache/npm \
             /data/tmp \
             /data/uploads \
             /data/transcriptions \
             /data/logs

    chmod -R 777 /data/.cache 2>/dev/null || echo "  Note: Could not chmod cache (may already have permissions)"
    chmod -R 777 /data/tmp 2>/dev/null || echo "  Note: Could not chmod tmp"

    # Check cache sizes (helps debug build time issues)
    echo ""
    echo "Cache Status:"
    if [ -d "/data/.cache/pip" ]; then
        PIP_SIZE=$(du -sh /data/.cache/pip 2>/dev/null | cut -f1)
        echo "  Pip cache: $PIP_SIZE"
    fi
    if [ -d "/data/.cache/torch" ]; then
        TORCH_SIZE=$(du -sh /data/.cache/torch 2>/dev/null | cut -f1)
        echo "  PyTorch cache: $TORCH_SIZE"
    fi
    if [ -d "/data/.cache/whisper" ]; then
        WHISPER_SIZE=$(du -sh /data/.cache/whisper 2>/dev/null | cut -f1)
        WHISPER_COUNT=$(ls -1 /data/.cache/whisper/*.pt 2>/dev/null | wc -l)
        echo "  Whisper models: $WHISPER_SIZE ($WHISPER_COUNT models)"
    fi
    if [ -d "/data/.cache/npm" ]; then
        NPM_SIZE=$(du -sh /data/.cache/npm 2>/dev/null | cut -f1)
        echo "  NPM cache: $NPM_SIZE"
    fi
    echo ""

    # List persistent disk contents
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

    # ============================================================================
    # STARTUP_TIMING markers — capture shell-side cost before gunicorn exec.
    # Three phases correspond to the dominant shell blocks above. They go to
    # Render stdout (greppable as [STARTUP_TIMING]) and are the only phases
    # that are log-only — Python-side phases are exposed via the in-memory
    # endpoint at /api/dev-tools/startup-diagnostics[.txt].
    # ============================================================================
    emit_startup_timing "shell_disk_prepare" "persistent-disk mount + writability test"
    emit_startup_timing "shell_cache_and_db_files" "pip/torch/whisper/npm cache dirs + .db placeholders"
    emit_startup_timing "shell_runtime_config" "/app/config dir + /config symlink"
else
    echo "✓ Running locally (development)"
fi

# Start Flask application with Gunicorn (production) or Python (development)
if [ "$RENDER" = "true" ]; then
    # ============================================================================
    # DEPLOY-TIME TOOL EMBEDDING PREWARM (added 2026-07-24)
    # ----------------------------------------------------------------------------
    # CRITICAL: runs BEFORE `exec gunicorn` so the HuggingFace model + tool
    # embeddings are ready before /health returns 200. Without this, the first
    # user chat arriving during the 30-60s background prewarm would block on
    # a singleton lock - the "1.4 minute hang" symptom reported by the user.
    #
    # Why a separate script:
    #   flask_app.py's background-thread prewarm runs AFTER /health returns
    #   200. Render routes traffic to the worker as soon as /health is 200,
    #   so the user pays for the prewarm cost.
    #
    #   By running prewarm BEFORE exec gunicorn, Render never even starts
    #   polling /health until the work is done. Render's healthCheckTimeout
    #   (30s) only applies to gunicorn's own readiness AFTER exec - NOT to
    #   the time spent in this script.
    #
    # Failure mode: if prewarm fails (e.g. Supabase unreachable), we still
    # start gunicorn (degraded mode). flask_app.py detects the missing
    # marker file and falls back to the background-thread prewarm + the
    # 503+Retry-After gate on the chat endpoint. The deploy never crash-loops
    # because of a prewarm failure.
    # ============================================================================
    echo ""
    echo "→ Running deploy-time tool embedding prewarm..."
    echo "  (first deploy:    30-90s for HuggingFace model download)"
    echo "  (subsequent:      5-15s, model + embeddings cached in /data)"
    echo ""
    PREWARM_START=$(date +%s%N)
    if python AI_infrastructure/scripts/deploy_prewarm.py; then
        PREWARM_END=$(date +%s%N)
        PREWARM_MS=$(( (PREWARM_END - PREWARM_START) / 1000000 ))
        echo "✓ Deploy-time prewarm completed in ${PREWARM_MS}ms"
    else
        PREWARM_END=$(date +%s%N)
        PREWARM_MS=$(( (PREWARM_END - PREWARM_START) / 1000000 ))
        echo "⚠️  Deploy-time prewarm FAILED after ${PREWARM_MS}ms"
        echo "   Starting gunicorn in DEGRADED mode."
        echo "   Chat endpoint will return 503+Retry-After until background prewarm completes."
    fi
    emit_startup_timing "shell_deploy_prewarm" "tool embeddings + HF model (deploy-time)"

    echo ""
    echo "→ Starting Flask with Gunicorn (production)..."
    echo "  Workers: 1 (WebSocket limitation - sticky sessions required)"
    echo "  Worker Class: geventwebsocket (WebSocket support)"
    echo "  Max Concurrent: ~1000 connections per worker"
    echo "  Timeout: 120s (for long-running AI requests)"
    echo "  Note: Multi-worker requires Redis message queue (SOCKETIO_MESSAGE_QUEUE)"
    echo ""
    exec gunicorn \
        --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
        --workers 1 \
        --bind 0.0.0.0:$PORT \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        AI_infrastructure.flask_app:app
else
    echo "→ Starting Flask application (development)..."
    exec python AI_infrastructure/flask_app.py
fi
