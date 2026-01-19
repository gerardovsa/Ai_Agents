# AI Agents Platform - Docker Configuration
# Optimized for Render.com deployment with sandbox code execution support
# BUILD TIME OPTIMIZATION: Layer caching to reduce 30min → 5-10min

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ============================================================================
# LAYER 1: System Dependencies (CACHED - rarely changes)
# ============================================================================
# Install system dependencies in single layer to optimize caching
# - curl: For health checks and API calls
# - git: For potential git operations in tools
# - build-essential: For compiling Python packages with C extensions
# - libpq-dev: For psycopg2 PostgreSQL connections (Supabase)
# - postgresql-client: For PostgreSQL command-line tools
# - unixodbc unixodbc-dev: For pyodbc SQL Server connections
# - freetds-dev: For pymssql SQL Server connections
# - tesseract-ocr: For pytesseract OCR text extraction
# - gnupg: For adding Microsoft's GPG key
# - nodejs npm: For frontend CAD visualization libraries (manifold-3d, three.js)
# - libgl1-mesa-glx: OpenGL library for CADQuery 3D rendering
# - libglib2.0-0: Required by CADQuery/OCC
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    libpq-dev \
    postgresql-client \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    tesseract-ocr \
    gnupg \
    apt-transport-https \
    nodejs \
    npm \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 18 for SQL Server
# Required for pyodbc connections to SQL Server (Fred database)
# Using modern GPG key method (apt-key is deprecated)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ============================================================================
# PERSISTENT DISK CONFIGURATION (10GB @ /data)
# ============================================================================
# Configure BEFORE installing dependencies to enable caching
# This dramatically reduces rebuild times: 25min → 5-8min
# Render Disk Setup: Dashboard → Disks → Add Disk → Mount Path: /data, Size: 10GB
# Cost: $2.50/month (10GB × $0.25/GB)

# 1. Pip Cache (wheel files, downloaded packages)
#    Stores ~2-3GB of pre-built wheels (torch, scipy, pandas, etc.)
#    Eliminates re-download and recompilation on every build
ENV PIP_CACHE_DIR=/data/.cache/pip

# 2. PyTorch/Torch Cache (model weights, compiled kernels)
#    Stores compiled CUDA/CPU kernels and model checkpoints
ENV TORCH_HOME=/data/.cache/torch

# 3. HuggingFace/Transformers Cache (Whisper models, tokenizers)
#    Stores downloaded Whisper models and transformers
ENV HF_HOME=/data/.cache/huggingface
ENV TRANSFORMERS_CACHE=/data/.cache/huggingface

# 4. XDG Cache (general application cache)
ENV XDG_CACHE_HOME=/data/.cache

# 5. Temporary Files (transcription, document processing, email attachments)
ENV TMPDIR=/data/tmp
ENV TEMP=/data/tmp
ENV TMP=/data/tmp

# 6. Application Data (uploads, transcriptions, generated files)
ENV UPLOAD_FOLDER=/data/uploads
ENV TRANSCRIPTION_FOLDER=/data/transcriptions

# 7. NumPy/SciPy Build Cache (compilation artifacts)
ENV NUMPY_MADVISE_HUGEPAGE=0
ENV OMP_NUM_THREADS=2

# Create persistent directories (must exist BEFORE pip install)
RUN mkdir -p /data/.cache/pip \
    /data/.cache/torch \
    /data/.cache/huggingface \
    /data/.cache/whisper \
    /data/.cache/numpy \
    /data/.cache/matplotlib \
    /data/tmp \
    /data/uploads \
    /data/transcriptions \
    /data/logs

# ============================================================================
# LAYER 2: Python Dependencies (CACHED on persistent disk!)
# ============================================================================
# Copy ONLY requirements.txt first (not entire app)
# This creates a separate Docker layer that gets cached
# CRITICAL: Now uses /data/.cache/pip for wheel storage
# 
# BUILD TIME BREAKDOWN (with persistent disk cache):
# First build (cold cache):  ~20-25 minutes
#   - torch: ~10-12 min (800MB download + compile)
#   - scipy/scikit: ~3-5 min (C/Fortran compilation)
#   - numpy/pandas: ~2-3 min
#   - Other packages: ~5 min
# 
# Subsequent builds (warm cache): ~3-5 minutes
#   - All wheels cached on /data
#   - No recompilation needed
#   - Only pip install from cached wheels
COPY requirements.txt .
RUN --mount=type=cache,target=/data/.cache/pip,sharing=locked \
    pip install --cache-dir=/data/.cache/pip -r requirements.txt

# ============================================================================
# LAYER 3: JavaScript Dependencies (CACHED on persistent disk!)
# ============================================================================
# Copy ONLY package.json first (not entire app)
# manifold-3d: Advanced 3D CAD operations (boolean ops, fillets, curves)
# three.js: 3D rendering engine
# 
# Now uses persistent npm cache to avoid re-downloading node_modules
ENV NPM_CONFIG_CACHE=/data/.cache/npm
RUN mkdir -p /data/.cache/npm

COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/data/.cache/npm,sharing=locked \
    npm install --only=production --cache /data/.cache/npm

# ============================================================================
# LAYER 4: Application Code (REBUILT EVERY TIME - but previous layers cached!)
# ============================================================================
# Copy entire application LAST
# This layer changes on every code change, but Layers 1-3 are reused from cache
COPY . .

# Ensure persistent disk mount point exists
# /data - for Render persistent disk mount point (10GB)
RUN mkdir -p /data

# NOTE: database-config.json is OPTIONAL (auto-created from environment variables)
# Legacy modules (quote-calculator, disabled in production) may reference it
# Flask lazy-loading will create default config if missing

# Make startup script executable
RUN chmod +x startup.sh

# Add application directories to Python path
# This ensures tools, implementations, and infrastructure modules can be imported
ENV PYTHONPATH="/app:/app/tools:/app/AI_infrastructure:/app/google_workspace:/app/Microsoft_365_Connection:${PYTHONPATH}"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV RENDER=true
ENV ENVIRONMENT=production

# ============================================================================
# WHISPER MODEL PRE-DOWNLOAD (Optional - adds ~2 min to first build)
# ============================================================================
# Whisper Configuration (Audio Transcription)
# WHISPER_MODEL_SIZE: Controls which Whisper model to use
#   - base (default): 145MB, fast, good accuracy (recommended for production)
#   - tiny: 75MB, fastest, lower accuracy
#   - small: 483MB, slower, better accuracy
#   - medium/large: 1.5GB+, very slow, highest accuracy (not recommended for Render)
# Set via Render Dashboard → Environment Variables to override
ENV WHISPER_MODEL_SIZE=base

# Pre-download Whisper model during build (OPTIONAL)
# First build: Adds ~2-3 minutes (downloads model to /data/.cache/whisper)
# Subsequent builds: Instant (model already cached on persistent disk)
# Alternative: Comment out for lazy loading (model downloads on first transcription request)
RUN --mount=type=cache,target=/data/.cache,sharing=locked \
    python -c "import whisper; whisper.load_model('${WHISPER_MODEL_SIZE:-base}')" || echo "Whisper model pre-download skipped (will lazy-load on first request)"

# Expose Flask port (5001 for local, 10000 for Render)
EXPOSE 5001

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5001}/health || exit 1

# Run startup script (handles persistent disk initialization + Flask app)
# Note: Render sets PORT environment variable to 10000
CMD ["./startup.sh"]
