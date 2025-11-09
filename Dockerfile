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
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application (includes data/database-config.json via .dockerignore exception)
COPY . .

# Ensure data directory exists for runtime database creation
RUN mkdir -p /app/data

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

# Run Flask app
# Note: Render sets PORT environment variable to 10000
CMD ["python", "AI_infrastructure/flask_app.py"]
