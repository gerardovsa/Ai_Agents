# AI Agents Platform - Docker Configuration
# Optimized for Render.com deployment with sandbox code execution support

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - curl: For health checks and API calls
# - git: For potential git operations in tools
# - build-essential: For compiling Python packages with C extensions
# - unixodbc unixodbc-dev: For pyodbc SQL Server connections
# - freetds-dev: For pymssql SQL Server connections
# - tesseract-ocr: For pytesseract OCR text extraction
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application
COPY . .

# Ensure persistent disk mount point exists
# /data - for Render persistent disk mount point (10GB)
# /app/data - already contains database-config.json from COPY . .
RUN mkdir -p /data

# Verify database-config.json exists in /app/data (copied from COPY . .)
# Startup script will copy this to persistent disk (/data) on first run
RUN if [ -f /app/data/database-config.json ]; then \
    echo "✓ database-config.json found in /app/data"; \
    ls -lh /app/data/database-config.json; \
    else \
    echo "⚠ Warning: database-config.json not found, will be created at runtime"; \
    fi

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
