# Professional Verification Module - Rapid Deployment Docker
# =============================================================
# Lightweight Python container with NO browser automation dependencies
# Perfect for testing core verification logic without Docker overhead

FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies (NO Docker-in-Docker, NO browsers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only essential files for verification engine
COPY verification_engine.py .
COPY report_generator.py .
COPY manifest.json .
COPY tools/ ./tools/

# Copy test files
COPY test_no_docker.py .
COPY smoke_test.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    anthropic \
    flask \
    reportlab \
    python-whois \
    requests

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MODULE_NAME=professional-verification

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import verification_engine; print('OK')" || exit 1

# Default command: run tests
CMD ["python", "test_no_docker.py"]

# Usage:
# Build:   docker build -t professional-verification:latest .
# Test:    docker run --rm professional-verification:latest
# Shell:   docker run -it --rm professional-verification:latest /bin/bash
# API:     docker run -p 5001:5001 professional-verification:latest python -m flask run
