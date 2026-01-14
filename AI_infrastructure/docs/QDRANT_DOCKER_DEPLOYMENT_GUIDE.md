# AI Agent: Deploy Qdrant Docker Container

## 🎯 TASK: Deploy Qdrant Vector Database on Customer Server

This guide provides step-by-step instructions for AI agents to deploy Qdrant on a customer's server (Windows or Linux).

---

## 📋 PREREQUISITES

1. Docker installed on customer server
2. Server has internet access (to pull Docker image)
3. Available ports: 6333 (HTTP API), 6334 (gRPC, optional)
4. Storage space: Minimum 10GB for data volume

---

## 🪟 WINDOWS DEPLOYMENT

### Step 1: Check Docker Installation

```powershell
# Verify Docker is installed
docker --version

# Expected output: Docker version 24.x.x or higher
```

**If Docker not found:**
```powershell
# Install Docker Desktop
Start-Process "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
# Follow installation wizard, restart required
```

### Step 2: Create Data Directory

```powershell
# Create directory for Qdrant data
New-Item -ItemType Directory -Path "C:\qdrant_data" -Force

# Verify creation
Test-Path "C:\qdrant_data"
# Expected: True
```

### Step 3: Pull Qdrant Image

```powershell
# Pull latest Qdrant image from Docker Hub
docker pull qdrant/qdrant:latest

# Verify image downloaded
docker images | Select-String "qdrant"
# Expected: qdrant/qdrant   latest   xxxxx   xxx MB
```

### Step 4: Run Qdrant Container

```powershell
# Run Qdrant with persistent storage
docker run -d `
  --name qdrant-server `
  --restart unless-stopped `
  -p 6333:6333 `
  -p 6334:6334 `
  -v C:\qdrant_data:/qdrant/storage `
  -e QDRANT__SERVICE__HTTP_PORT=6333 `
  -e QDRANT__SERVICE__GRPC_PORT=6334 `
  qdrant/qdrant:latest

# Expected output: Container ID (64 characters)
```

**Parameters explained:**
- `-d`: Run in detached mode (background)
- `--name qdrant-server`: Container name
- `--restart unless-stopped`: Auto-restart on reboot
- `-p 6333:6333`: HTTP API port
- `-p 6334:6334`: gRPC port (optional)
- `-v C:\qdrant_data:/qdrant/storage`: Persistent volume
- `-e QDRANT__SERVICE__HTTP_PORT`: Configure HTTP port
- `-e QDRANT__SERVICE__GRPC_PORT`: Configure gRPC port

### Step 5: Verify Container Running

```powershell
# Check container status
docker ps | Select-String "qdrant"

# Expected output:
# CONTAINER ID   IMAGE              STATUS         PORTS                    NAMES
# abc123def456   qdrant/qdrant      Up 10 seconds  0.0.0.0:6333->6333/tcp  qdrant-server
```

### Step 6: Test Connection

```powershell
# Test HTTP API endpoint
curl http://localhost:6333/health

# Expected response: {"title":"qdrant - vector search engine","version":"1.7.x"}
```

```powershell
# List collections (should be empty initially)
curl http://localhost:6333/collections

# Expected response: {"result":{"collections":[]}}
```

### Step 7: Check Logs

```powershell
# View container logs
docker logs qdrant-server

# Expected: Server startup messages, no errors
```

### Step 8: Return Connection Details

```json
{
  "success": true,
  "deployment_type": "customer_server",
  "host": "localhost",
  "port": 6333,
  "container_id": "<container_id_from_step_4>",
  "container_name": "qdrant-server",
  "data_path": "C:\\qdrant_data",
  "api_endpoint": "http://localhost:6333",
  "health_check": "http://localhost:6333/health",
  "status": "running",
  "message": "Qdrant deployed successfully on Windows server"
}
```

---

## 🐧 LINUX DEPLOYMENT

### Step 1: Check Docker Installation

```bash
# Verify Docker is installed
docker --version

# Expected output: Docker version 24.x.x or higher
```

**If Docker not found:**
```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in for group changes
```

### Step 2: Create Data Directory

```bash
# Create directory for Qdrant data
sudo mkdir -p /var/lib/qdrant_data
sudo chown $USER:$USER /var/lib/qdrant_data

# Verify creation
ls -ld /var/lib/qdrant_data
# Expected: drwxr-xr-x 2 username username ...
```

### Step 3: Pull Qdrant Image

```bash
# Pull latest Qdrant image
docker pull qdrant/qdrant:latest

# Verify image downloaded
docker images | grep qdrant
# Expected: qdrant/qdrant   latest   xxxxx   xxx MB
```

### Step 4: Run Qdrant Container

```bash
# Run Qdrant with persistent storage
docker run -d \
  --name qdrant-server \
  --restart unless-stopped \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /var/lib/qdrant_data:/qdrant/storage \
  -e QDRANT__SERVICE__HTTP_PORT=6333 \
  -e QDRANT__SERVICE__GRPC_PORT=6334 \
  qdrant/qdrant:latest

# Expected output: Container ID (64 characters)
```

### Step 5: Verify Container Running

```bash
# Check container status
docker ps | grep qdrant

# Expected output:
# abc123def456   qdrant/qdrant   Up 10 seconds   0.0.0.0:6333->6333/tcp   qdrant-server
```

### Step 6: Test Connection

```bash
# Test HTTP API endpoint
curl http://localhost:6333/health

# Expected response: {"title":"qdrant - vector search engine","version":"1.7.x"}
```

```bash
# List collections (should be empty initially)
curl http://localhost:6333/collections

# Expected response: {"result":{"collections":[]}}
```

### Step 7: Check Logs

```bash
# View container logs
docker logs qdrant-server

# Expected: Server startup messages, no errors
```

### Step 8: Return Connection Details

```json
{
  "success": true,
  "deployment_type": "customer_server",
  "host": "localhost",
  "port": 6333,
  "container_id": "<container_id_from_step_4>",
  "container_name": "qdrant-server",
  "data_path": "/var/lib/qdrant_data",
  "api_endpoint": "http://localhost:6333",
  "health_check": "http://localhost:6333/health",
  "status": "running",
  "message": "Qdrant deployed successfully on Linux server"
}
```

---

## 🔒 OPTIONAL: Enable API Key Authentication

### Windows:

```powershell
# Stop existing container
docker stop qdrant-server
docker rm qdrant-server

# Generate API key
$apiKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
Write-Host "Generated API Key: $apiKey"

# Run with API key
docker run -d `
  --name qdrant-server `
  --restart unless-stopped `
  -p 6333:6333 `
  -p 6334:6334 `
  -v C:\qdrant_data:/qdrant/storage `
  -e QDRANT__SERVICE__API_KEY=$apiKey `
  qdrant/qdrant:latest

# Test with API key
curl http://localhost:6333/health -H "api-key: $apiKey"
```

### Linux:

```bash
# Stop existing container
docker stop qdrant-server
docker rm qdrant-server

# Generate API key
API_KEY=$(openssl rand -base64 32)
echo "Generated API Key: $API_KEY"

# Run with API key
docker run -d \
  --name qdrant-server \
  --restart unless-stopped \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /var/lib/qdrant_data:/qdrant/storage \
  -e QDRANT__SERVICE__API_KEY=$API_KEY \
  qdrant/qdrant:latest

# Test with API key
curl http://localhost:6333/health -H "api-key: $API_KEY"
```

---

## 🌐 NETWORK ACCESS (For Remote Connections)

### Windows Firewall:

```powershell
# Allow inbound traffic on port 6333
New-NetFirewallRule -DisplayName "Qdrant HTTP API" -Direction Inbound -Protocol TCP -LocalPort 6333 -Action Allow
```

### Linux Firewall (UFW):

```bash
# Allow inbound traffic on port 6333
sudo ufw allow 6333/tcp
sudo ufw reload
```

### Get Server IP Address:

**Windows:**
```powershell
# Get primary IP address
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress

# Expected: 192.168.1.100 (example)
```

**Linux:**
```bash
# Get primary IP address
hostname -I | awk '{print $1}'

# Expected: 192.168.1.100 (example)
```

**Update connection details:**
```json
{
  "host": "192.168.1.100",  // Replace localhost with actual IP
  "port": 6333,
  "api_key": "<generated_api_key>",  // If enabled
  "message": "Qdrant accessible at http://192.168.1.100:6333"
}
```

---

## 🛠️ TROUBLESHOOTING

### Container Won't Start

```powershell
# Check logs
docker logs qdrant-server

# Common issues:
# 1. Port already in use
netstat -ano | Select-String ":6333"
# Solution: Stop conflicting service or use different port

# 2. Volume permission error
icacls C:\qdrant_data
# Solution: Grant full control to current user
```

### Connection Refused

```powershell
# Verify container is running
docker ps | Select-String "qdrant"

# Verify port binding
docker port qdrant-server

# Test localhost connection
curl http://localhost:6333/health

# If localhost works but remote doesn't, check firewall
```

### Data Not Persisting

```powershell
# Check volume mount
docker inspect qdrant-server | Select-String "Mounts"

# Verify data directory exists
Test-Path "C:\qdrant_data"

# Check data files
Get-ChildItem "C:\qdrant_data" -Recurse
```

---

## 🔄 CONTAINER MANAGEMENT

### Stop Container:

```powershell
# Windows
docker stop qdrant-server
```

```bash
# Linux
docker stop qdrant-server
```

### Restart Container:

```powershell
# Windows
docker restart qdrant-server
```

```bash
# Linux
docker restart qdrant-server
```

### Remove Container:

```powershell
# Windows (preserves data in C:\qdrant_data)
docker stop qdrant-server
docker rm qdrant-server
```

```bash
# Linux (preserves data in /var/lib/qdrant_data)
docker stop qdrant-server
docker rm qdrant-server
```

### View Resource Usage:

```powershell
# Windows
docker stats qdrant-server
```

```bash
# Linux
docker stats qdrant-server
```

---

## ✅ SUCCESS CRITERIA

- [ ] Docker installed and running
- [ ] Qdrant container running (status: Up)
- [ ] Health check returns 200 OK
- [ ] Collections API accessible
- [ ] Data directory created and writable
- [ ] Ports 6333/6334 open (if remote access needed)
- [ ] API key configured (if authentication enabled)
- [ ] Connection details returned to application

---

## 📞 NEXT STEPS

After successful deployment, customer should:

1. **Add connection to Vector Database Module:**
   - Open AI Agents Platform → Vector Database
   - Select "Qdrant" provider
   - Enter connection details (host, port, API key)
   - Click "Test Connection"

2. **Create first collection:**
   - Click "Create Collection"
   - Name: `customer_docs`
   - Vector size: 1536 (for Voyager/OpenAI embeddings)
   - Distance metric: Cosine

3. **Upload documents:**
   - Click "Upload Documents"
   - Select PDFs, DOCX, TXT, MD files
   - System automatically generates embeddings
   - Vectors stored in Qdrant

4. **Test search:**
   - Use "Search" tab
   - Enter query: "find sales reports"
   - View semantic search results

---

## 🚀 PERFORMANCE TIPS

1. **Use SSD storage:** Mount volume to SSD for 10x faster queries
2. **Increase memory:** Allocate 4GB+ RAM for large datasets
3. **Enable gRPC:** Use port 6334 for faster bulk operations
4. **Index optimization:** Qdrant auto-optimizes, but manual tuning available
5. **Monitoring:** Check `docker stats qdrant-server` for resource usage

---

## 📚 ADDITIONAL RESOURCES

- Qdrant Documentation: https://qdrant.tech/documentation/
- Docker Documentation: https://docs.docker.com/
- API Reference: https://qdrant.tech/documentation/quick-start/
- GitHub: https://github.com/qdrant/qdrant

---

**Deployment Time:** 5-10 minutes
**Difficulty:** Easy
**Requirements:** Docker Desktop (Windows) or Docker Engine (Linux)
