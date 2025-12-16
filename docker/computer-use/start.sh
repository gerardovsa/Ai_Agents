#!/bin/bash
# Startup script for Professional Verification browser container
# Starts Xvfb, x11vnc, and fluxbox window manager

echo "================================================"
echo "Professional Verification - Browser Container"
echo "================================================"

# Start Xvfb (Virtual framebuffer)
echo "[1/4] Starting Xvfb display server..."
Xvfb :1 -screen 0 ${DISPLAY_WIDTH}x${DISPLAY_HEIGHT}x24 &
XVFB_PID=$!
sleep 2

# Start x11vnc (VNC server)
echo "[2/4] Starting x11vnc server on port 5900..."
x11vnc -display :1 -forever -shared -rfbport 5900 -passwd ${VNC_PASSWORD} &
VNC_PID=$!
sleep 2

# Start fluxbox (Window manager)
echo "[3/4] Starting fluxbox window manager..."
DISPLAY=:1 fluxbox &
FLUXBOX_PID=$!
sleep 2

# Start Chromium (Default browser)
echo "[4/4] Starting Chromium browser..."
DISPLAY=:1 chromium-browser \
    --no-sandbox \
    --disable-dev-shm-usage \
    --disable-gpu \
    --window-size=${DISPLAY_WIDTH},${DISPLAY_HEIGHT} \
    --start-maximized \
    about:blank &
CHROMIUM_PID=$!

echo ""
echo "✅ All services started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📺 Display:       ${DISPLAY}"
echo "🖥️  Resolution:    ${DISPLAY_WIDTH}x${DISPLAY_HEIGHT}"
echo "🔐 VNC Port:      5900"
echo "🔑 VNC Password:  ${VNC_PASSWORD}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To view desktop remotely:"
echo "  1. Install a VNC viewer (TigerVNC, RealVNC, etc.)"
echo "  2. Connect to: localhost:5900"
echo "  3. Enter password: ${VNC_PASSWORD}"
echo ""
echo "Container is ready for Computer Use automation!"
echo "================================================"

# Keep container running and monitor processes
while true; do
    if ! kill -0 $XVFB_PID 2>/dev/null; then
        echo "❌ Xvfb died, restarting..."
        Xvfb :1 -screen 0 ${DISPLAY_WIDTH}x${DISPLAY_HEIGHT}x24 &
        XVFB_PID=$!
    fi
    
    if ! kill -0 $VNC_PID 2>/dev/null; then
        echo "❌ VNC server died, restarting..."
        x11vnc -display :1 -forever -shared -rfbport 5900 -passwd ${VNC_PASSWORD} &
        VNC_PID=$!
    fi
    
    sleep 10
done
