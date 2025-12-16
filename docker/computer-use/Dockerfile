# Professional Verification - Browser Container Image
# ================================================
# Ubuntu 22.04 with desktop environment for Anthropic Computer Use
#
# Includes:
# - Xvfb (Virtual framebuffer for headless display)
# - x11vnc (VNC server for remote viewing)
# - fluxbox (Lightweight window manager)
# - xdotool (Keyboard/mouse automation)
# - scrot (Screenshot tool)
# - Chromium & Firefox browsers
# - Python 3.11 with pip
#
# BUILD: docker build -t professional-verification-browser:latest .
# RUN:   docker run -d -p 5900:5900 professional-verification-browser:latest
# VNC:   Connect to localhost:5900 to view desktop

FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install desktop environment and tools
RUN apt-get update && apt-get install -y \
    # Virtual display server
    xvfb \
    x11vnc \
    fluxbox \
    # Automation tools
    xdotool \
    scrot \
    imagemagick \
    # Browsers
    chromium-browser \
    firefox \
    # Python
    python3.11 \
    python3-pip \
    # Utilities
    wget \
    curl \
    git \
    vim \
    # Fonts for better rendering
    fonts-liberation \
    fonts-noto \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Install Python packages for automation
RUN pip3 install --no-cache-dir \
    requests \
    beautifulsoup4 \
    selenium \
    pyautogui

# Set environment variables
ENV DISPLAY=:1
ENV DISPLAY_WIDTH=1920
ENV DISPLAY_HEIGHT=1080
ENV VNC_PASSWORD=valorai

# Create workspace
RUN mkdir -p /workspace
WORKDIR /workspace

# Copy startup script
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Expose VNC port
EXPOSE 5900

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD x11vnc -display :1 -version || exit 1

# Start all services
CMD ["/usr/local/bin/start.sh"]
