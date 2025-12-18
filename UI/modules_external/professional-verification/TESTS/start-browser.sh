#!/bin/bash
# Start script for Computer Use browser container

# Start Xvfb (virtual display)
Xvfb :1 -screen 0 1920x1080x24 &
XVFB_PID=$!

# Wait for X server to start
sleep 2

# Start window manager
fluxbox &

# Start VNC server
x11vnc -display :1 -forever -shared -rfbport 5900 -rfbauth /home/computeruse/.vnc/passwd &

# Start Chromium in kiosk mode
chromium-browser \
    --no-sandbox \
    --disable-dev-shm-usage \
    --disable-gpu \
    --window-size=1920,1080 \
    --start-maximized \
    --disable-infobars \
    --disable-extensions \
    --disable-popup-blocking \
    --disable-notifications \
    "about:blank" &

# Keep container running
wait $XVFB_PID
