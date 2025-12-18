# Mini Docker Setup for Computer Use Testing

This is a **standalone, minimal Docker setup** just for testing Computer Use. It doesn't interfere with the main project's Docker configuration.

## Quick Start

### Option 1: Docker Compose (Easiest)

```powershell
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Manual Docker Commands

```powershell
# Build the image
docker build -f Dockerfile.computer-use -t computer-use-test:latest .

# Run the container
docker run -d `
  --name computer-use-test `
  -p 5900:5900 `
  --shm-size=2g `
  computer-use-test:latest

# Check it's running
docker ps | Select-String "computer-use-test"

# View logs
docker logs -f computer-use-test

# Stop and remove
docker stop computer-use-test
docker rm computer-use-test
```

## Testing Computer Use

Once the container is running:

```powershell
# Run the automated test
python test_computer_use_auto.py
```

The test will:
1. Connect to the Docker container
2. Have Claude browse isb.eco
3. Extract information about the organization
4. Save a screenshot
5. Report findings

## What's Inside

- **Ubuntu 22.04** - Lightweight base
- **Xvfb** - Virtual X11 display (1920x1080)
- **Chromium** - Browser for web navigation
- **VNC** - Remote desktop access (port 5900)
- **xdotool** - Mouse/keyboard control

## Debugging

### View the browser screen

You can connect with a VNC viewer to see what Claude sees:

```powershell
# Install VNC Viewer from: https://www.realvnc.com/en/connect/download/viewer/
# Connect to: localhost:5900
# Password: computeruse
```

### Check container health

```powershell
docker inspect computer-use-test | Select-String "Health"
```

### Restart container

```powershell
docker restart computer-use-test
```

## Files in This Setup

```
TESTS/
├── Dockerfile.computer-use     # Docker image definition
├── docker-compose.yml          # Compose configuration
├── start-browser.sh            # Container startup script
├── test_computer_use_auto.py   # Automated test
└── README_DOCKER.md            # This file
```

## Important Notes

✅ **Isolated** - This Docker setup is completely separate from the main project  
✅ **Minimal** - Only ~400MB (vs 2GB+ for full Computer Use images)  
✅ **Fast** - Starts in 5-10 seconds  
✅ **Safe** - Non-root user, sandboxed browser  

❌ **Not for production** - This is for testing only  
❌ **No Python** - The executor runs on your host machine  
❌ **No persistence** - Container state is lost on restart  

## Troubleshooting

### "Cannot connect to Docker daemon"
```powershell
# Start Docker Desktop
# Wait for it to fully start
docker ps  # Should work without errors
```

### "Port 5900 already in use"
```powershell
# Stop any conflicting containers
docker stop $(docker ps -q --filter "publish=5900")
```

### "Container exits immediately"
```powershell
# Check logs
docker logs computer-use-test

# Common fix: rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### "Test hangs at screenshot"
```powershell
# Container might not be ready
docker exec computer-use-test pgrep -x Xvfb  # Should return a PID

# Restart container
docker restart computer-use-test
sleep 10
python test_computer_use_auto.py
```

## Cleanup

Remove everything:

```powershell
# Stop and remove container
docker-compose down

# Remove image
docker rmi computer-use-test:latest

# Full cleanup (including build cache)
docker-compose down --rmi all --volumes
```

## Next Steps

After successful testing:

1. **Use the tools** - `auto_enter_verification_results()` is ready
2. **Production setup** - Use the main project's Computer Use infrastructure
3. **Scale up** - Add more containers for parallel processing
4. **Monitor** - Check execution logs and screenshots

---

**Status:** Ready for testing 🚀  
**Size:** ~400MB  
**Startup:** 5-10 seconds  
**Purpose:** Computer Use API testing only
