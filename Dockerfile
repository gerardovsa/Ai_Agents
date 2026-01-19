# AI Agents Platform - Docker Configuration
# Optimized for Render.com deployment with sandbox code execution support
# BUILD TIME OPTIMIZATION: Layer caching to reduce 30min ΓåÆ 5-10min

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
# LAYER 2: Python Dependencies (CACHED - only rebuilds if requirements.txt changes)
# ============================================================================
# Copy ONLY requirements.txt first (not entire app)
# This creates a separate Docker layer that gets cached
# If requirements.txt doesn't change, this layer is reused (saves 10-15 minutes!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# LAYER 3: JavaScript Dependencies (CACHED - only rebuilds if package.json changes)
# ============================================================================
# Copy ONLY package.json first (not entire app)
# manifold-3d: Advanced 3D CAD operations (boolean ops, fillets, curves)
# three.js: 3D rendering engine
COPY package.json package-lock.json* ./
RUN npm install --only=production && npm cache clean --force

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

# Expose Flask port (5001 for local, 10000 for Render)
EXPOSE 5001

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5001}/health || exit 1

# Run startup script (handles persistent disk initialization + Flask app)
# Note: Render sets PORT environment variable to 10000
CMD ["./startup.sh"]
