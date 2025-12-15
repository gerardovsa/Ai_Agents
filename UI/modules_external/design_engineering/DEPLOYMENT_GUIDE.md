# 🚀 Deployment Guide - AI-Human CAD Collaboration Platform

## 📋 Quick Deploy Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] WebSocket server running
- [ ] Static files served (HTML/JS/CSS)
- [ ] (Optional) HTTPS/WSS for production
- [ ] (Optional) AI API keys configured

---

## 🏗️ Development Setup (5 minutes)

### 1. Install Python Dependencies

```bash
cd backend
pip install fastapi uvicorn websockets pillow cairosvg python-multipart
```

### 2. Start WebSocket Server

```bash
python websocket_server.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Serve Static Files

**Option A: Python HTTP Server**
```bash
cd ..  # Back to design_engineering directory
python -m http.server 8080
```

**Option B: VS Code Live Server**
- Install "Live Server" extension
- Right-click `cad-collaboration-demo.html`
- Click "Open with Live Server"

**Option C: Node.js (if you have it)**
```bash
npx http-server -p 8080
```

### 4. Open in Browser

```
http://localhost:8080/cad-collaboration-demo.html
```

**Expected:** See CAD platform UI with status "Connected" or "Demo Mode"

---

## 🌐 Production Deployment

### Architecture

```
┌──────────────┐     HTTPS/WSS      ┌────────────────┐
│   Browser    │◄──────────────────►│  Nginx Proxy   │
│   (Client)   │                    │  (SSL/TLS)     │
└──────────────┘                    └────────┬───────┘
                                             │
                                             ↓
                                    ┌────────────────┐
                                    │  Uvicorn       │
                                    │  (WebSocket)   │
                                    │  Port: 8000    │
                                    └────────────────┘
```

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3.8 python3.8-venv python3-pip -y

# Install system dependencies
sudo apt install libcairo2-dev libpango1.0-dev -y
```

### Step 2: Clone & Setup

```bash
# Create app directory
mkdir -p /opt/cad-platform
cd /opt/cad-platform

# Copy your files
# (Use git clone, scp, or your preferred method)

# Create virtual environment
python3.8 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pillow==10.1.0
cairosvg==2.7.1
python-multipart==0.0.6
```

### Step 3: Configure Systemd Service

```bash
sudo nano /etc/systemd/system/cad-websocket.service
```

**Service file:**
```ini
[Unit]
Description=CAD Collaboration WebSocket Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/cad-platform/backend
Environment="PATH=/opt/cad-platform/venv/bin"
ExecStart=/opt/cad-platform/venv/bin/python websocket_server.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable & start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable cad-websocket
sudo systemctl start cad-websocket
sudo systemctl status cad-websocket
```

### Step 4: Nginx Configuration

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/cad-platform
```

**Nginx config:**
```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    server_name cad.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS + WebSocket
server {
    listen 443 ssl http2;
    server_name cad.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/cad.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cad.yourdomain.com/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Static files
    root /opt/cad-platform;
    index cad-collaboration-demo.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # REST API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/cad-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d cad.yourdomain.com
```

Follow prompts, certificate will auto-renew.

### Step 6: Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

---

## 🐳 Docker Deployment

### Dockerfile (Backend)

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/

WORKDIR /app/backend

# Run server
CMD ["python", "websocket_server.py"]

EXPOSE 8000
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  websocket-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
    volumes:
      - ./backend:/app/backend
    networks:
      - cad-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./:/usr/share/nginx/html:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - websocket-server
    networks:
      - cad-network
    restart: unless-stopped

networks:
  cad-network:
    driver: bridge
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## ☁️ Cloud Deployment

### AWS (EC2 + ALB)

**1. Launch EC2 Instance**
```bash
# t3.medium or larger
# Ubuntu 22.04 LTS
# Security Group: Allow 80, 443, 22
```

**2. Install Application** (follow Production Deployment above)

**3. Create Application Load Balancer**
- Target Group → Port 8000
- Health Check → `/api/sessions/create`
- Listener 443 → Target Group
- SSL Certificate from ACM

**4. Update WebSocket URL**
In `cad-collaboration-demo.html`:
```javascript
const wsUrl = `wss://cad.yourdomain.com/ws/cad/${this.sessionId}`;
```

### Google Cloud (Cloud Run)

**Not recommended** - Cloud Run doesn't support WebSocket well.  
Use **Google Kubernetes Engine (GKE)** instead.

### Azure (App Service)

```bash
# Create App Service
az webapp up --name cad-platform --runtime "PYTHON:3.10"

# Enable WebSocket
az webapp config set --name cad-platform --resource-group myResourceGroup --web-sockets-enabled true

# Deploy
git push azure main
```

### Heroku

```bash
# Create app
heroku create cad-platform

# Add buildpack
heroku buildpacks:add heroku/python

# Deploy
git push heroku main

# Enable WebSocket (automatic on Heroku)
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# AI Integration (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Session
SESSION_TIMEOUT_MINUTES=60
MAX_PARTICIPANTS_PER_SESSION=10

# CORS
ALLOWED_ORIGINS=https://cad.yourdomain.com,http://localhost:8080
```

Update `websocket_server.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))

# In CORS middleware
allow_origins=os.getenv('ALLOWED_ORIGINS', '*').split(',')
```

---

## 📊 Monitoring

### Health Checks

```bash
# WebSocket server status
curl http://localhost:8000/health

# Session list
curl http://localhost:8000/api/sessions
```

### Logs

```bash
# Systemd service logs
sudo journalctl -u cad-websocket -f

# Docker logs
docker-compose logs -f websocket-server

# Nginx access/error logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Metrics (Optional - Prometheus)

Add to `websocket_server.py`:
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
patch_counter = Counter('cad_patches_total', 'Total patches applied')
session_gauge = Gauge('cad_active_sessions', 'Active sessions')
latency_histogram = Histogram('cad_patch_latency_seconds', 'Patch latency')

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type='text/plain')
```

---

## 🔐 Security

### 1. Authentication (Add JWT)

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.websocket("/ws/cad/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Depends(verify_token)
):
    # ...
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/sessions/create")
@limiter.limit("5/minute")
async def create_session(request: Request):
    # ...
```

### 3. Input Validation

```python
from pydantic import BaseModel, validator

class PatchRequest(BaseModel):
    op: str
    path: str
    value: Any
    
    @validator('op')
    def validate_op(cls, v):
        if v not in ['add', 'remove', 'replace', 'move', 'copy']:
            raise ValueError('Invalid operation')
        return v
    
    @validator('path')
    def validate_path(cls, v):
        if not v.startswith('/'):
            raise ValueError('Path must start with /')
        return v
```

---

## 🧪 Testing Deployment

### 1. Local Test

```bash
# Terminal 1: Start server
python backend/websocket_server.py

# Terminal 2: Test WebSocket
wscat -c ws://localhost:8000/ws/cad/test-session

# Terminal 3: Test HTTP
curl http://localhost:8000/api/sessions
```

### 2. Load Test

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class CADUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_session(self):
        self.client.post("/api/sessions/create?design_name=LoadTest")
    
    @task
    def get_sessions(self):
        self.client.get("/api/sessions")
EOF

# Run load test
locust -f locustfile.py --host http://localhost:8000
```

Open http://localhost:8089 for UI.

### 3. WebSocket Load Test

```python
import asyncio
import websockets

async def test_websocket():
    async with websockets.connect('ws://localhost:8000/ws/cad/test') as ws:
        # Send patch
        await ws.send(json.dumps({
            'type': 'PATCH',
            'patch': {
                'op': 'add',
                'path': '/objects/test',
                'value': {'type': 't-slot-beam'}
            }
        }))
        
        # Receive response
        response = await ws.recv()
        print(response)

asyncio.run(test_websocket())
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

`.github/workflows/deploy.yml`:
```yaml
name: Deploy CAD Platform

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest backend/tests/
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/cad-platform
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart cad-websocket
```

---

## 📈 Scaling

### Horizontal Scaling (Multiple Servers)

Use **Redis** for session state sharing:

```python
import redis

redis_client = redis.Redis(host='redis-server', port=6379, db=0)

class SessionManager:
    def get_session(self, session_id):
        data = redis_client.get(f'session:{session_id}')
        if data:
            return json.loads(data)
        return None
    
    def save_session(self, session_id, data):
        redis_client.set(f'session:{session_id}', json.dumps(data))
```

### Load Balancer Configuration

```nginx
upstream cad_backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /ws/ {
        proxy_pass http://cad_backend;
        # WebSocket config...
    }
}
```

---

## 🆘 Troubleshooting

### WebSocket Connection Fails

**Check:**
```bash
# Server running?
sudo systemctl status cad-websocket

# Port accessible?
telnet localhost 8000

# Firewall?
sudo ufw status

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### CORS Errors

Update `websocket_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### High Memory Usage

```bash
# Check memory
free -h

# Limit session timeout
SESSION_TIMEOUT_MINUTES=30

# Add to systemd service
[Service]
MemoryLimit=512M
```

---

## ✅ Post-Deployment Checklist

- [ ] Server accessible via HTTPS
- [ ] WebSocket connection working (wss://)
- [ ] SSL certificate valid and auto-renewing
- [ ] Logs being collected
- [ ] Health checks passing
- [ ] Firewall configured
- [ ] Backups scheduled (if needed)
- [ ] Monitoring alerts set up
- [ ] Documentation updated

---

## 📞 Support

Issues? Check:
1. Server logs: `sudo journalctl -u cad-websocket -f`
2. Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Browser console: F12 → Console tab
4. WebSocket status: Browser Network tab → WS filter

---

**Deployment complete! 🎉**

Test at: `https://cad.yourdomain.com/cad-collaboration-demo.html`
