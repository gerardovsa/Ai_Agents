# Professional Verification - Browser Container
## Docker Image for Computer Use Automation

This Docker image provides a complete browser environment for Anthropic Computer Use API integration.

### 🚀 What's Included

- **Ubuntu 22.04** base image
- **Xvfb** - Virtual framebuffer (headless display server)
- **x11vnc** - VNC server for remote desktop viewing
- **fluxbox** - Lightweight window manager
- **xdotool** - Keyboard and mouse automation
- **scrot** - Screenshot capture tool
- **Chromium & Firefox** - Web browsers
- **Python 3.11** - With automation libraries

### 📦 Build the Image

```bash
cd docker/computer-use
docker build -t professional-verification-browser:latest .
```

**Build time:** ~3-5 minutes (downloads ~500MB of packages)

### 🏃 Run the Container

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option 2: Docker Run**
```bash
docker run -d \
  --name pv-browser \
  -p 5900:5900 \
  --shm-size=2gb \
  -e DISPLAY=:1 \
  -e DISPLAY_WIDTH=1920 \
  -e DISPLAY_HEIGHT=1080 \
  professional-verification-browser:latest
```

### 🖥️ View the Desktop (Optional)

The container runs a VNC server so you can see what Computer Use is doing:

1. **Install a VNC Viewer:**
   - Windows: [TigerVNC](https://tigervnc.org/) or [RealVNC](https://www.realvnc.com/)
   - Mac: Built-in Screen Sharing or [TigerVNC](https://tigervnc.org/)
   - Linux: `vncviewer` or `tigervnc`

2. **Connect to VNC:**
   - Address: `localhost:5900`
   - Password: `valorai`

3. **You'll see:**
   - Chromium browser running
   - Automated mouse movements
   - Forms being filled
   - Screenshots being taken

### 🔧 Container Management

**Check Container Status:**
```bash
docker ps | grep pv-browser
```

**View Logs:**
```bash
docker logs pv-browser
```

**Stop Container:**
```bash
docker stop pv-browser
```

**Restart Container:**
```bash
docker restart pv-browser
```

**Remove Container:**
```bash
docker stop pv-browser
docker rm pv-browser
```

### 🏗️ How Computer Use Executor Uses This

The `ComputerUseExecutor` class automatically:

1. **Spawns containers** from this image
2. **Executes commands** via `docker exec`
3. **Captures screenshots** using `scrot`
4. **Controls mouse/keyboard** using `xdotool`
5. **Manages lifecycle** (pooling, cleanup)

Example from code:
```python
from AI_infrastructure.core.computer_use_executor import get_computer_use_executor

executor = get_computer_use_executor()
container_id = await executor.get_browser_container()

# Take screenshot
screenshot = await executor.take_screenshot(container_id)

# Move mouse and click
await executor.move_mouse(container_id, 500, 300)
await executor.click_mouse(container_id)

# Type text
await executor.type_text(container_id, "john@example.com")
```

### 🐛 Troubleshooting

**Container fails to start:**
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker logs pv-browser

# Try rebuilding
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**VNC connection refused:**
```bash
# Check VNC port is exposed
docker port pv-browser

# Verify VNC server is running
docker exec pv-browser ps aux | grep x11vnc
```

**Browser doesn't start:**
```bash
# Check Xvfb is running
docker exec pv-browser ps aux | grep Xvfb

# Restart container
docker restart pv-browser
```

**Out of memory errors:**
```bash
# Increase shared memory
docker run --shm-size=4gb ...

# Or in docker-compose.yml:
shm_size: '4gb'
```

### 📊 Resource Usage

- **Memory:** 1-2GB RAM
- **CPU:** 1-2 cores
- **Disk:** ~2GB (image size)
- **Network:** Full internet access required

### 🔐 Security Notes

1. **Network Isolation:** Container has full network access (needed for browsing)
2. **VNC Password:** Change `VNC_PASSWORD` environment variable for security
3. **Credentials:** Never hardcode credentials in image - inject at runtime
4. **Container Lifetime:** Containers are ephemeral - no persistent storage

### 🎯 Production Recommendations

1. **Container Pooling:**
   - Pre-warm 4 containers at startup
   - Reuse containers across verifications
   - Destroy after 50 uses or 1 hour

2. **Monitoring:**
   - Watch memory usage (browsers leak memory)
   - Log all container spawns/destroys
   - Alert on spawn failures

3. **Scaling:**
   - Run on dedicated Docker host
   - Limit max concurrent containers (4-8)
   - Use container orchestration (Docker Swarm/Kubernetes) for HA

### 📝 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DISPLAY` | `:1` | X11 display number |
| `DISPLAY_WIDTH` | `1920` | Screen width in pixels |
| `DISPLAY_HEIGHT` | `1080` | Screen height in pixels |
| `VNC_PASSWORD` | `valorai` | VNC server password |

### 🚀 Next Steps

1. Build the image: `docker build -t professional-verification-browser:latest .`
2. Test manually: `docker-compose up`
3. Connect VNC to verify: `localhost:5900`
4. Run verification: Use tools via Tool Registry V3
5. Monitor logs: `docker logs -f pv-browser`

---

**Created:** December 16, 2025  
**Platform:** AI Agent Professional Verification Module  
**Purpose:** Browser automation for credential verification
