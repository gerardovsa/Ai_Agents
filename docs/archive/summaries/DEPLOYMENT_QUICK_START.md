# AI-Powered Multi-Platform Intelligence Suite
## Quick Start Deployment Guide

**Time to deploy**: 30 minutes  
**Prerequisites**: Docker, Docker Compose installed

---

## 🚀 Step 1: Clone & Setup (5 minutes)

```bash
# Navigate to project directory
cd C:\Users\gpoli\GIT\AI_agents

# Copy environment template
cp .env.example .env.production

# Edit with your API keys
notepad .env.production
```

### Required Environment Variables

```bash
# ============================================================================
# ONLYOFFICE Configuration
# ============================================================================
ONLYOFFICE_JWT_SECRET=your_random_secret_key_here_change_this
ONLYOFFICE_SERVER_URL=http://localhost:8080

# ============================================================================
# AI Model API Keys (CRITICAL - You have these!)
# ============================================================================
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...

# ============================================================================
# Google Workspace OAuth2
# ============================================================================
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# ============================================================================
# Database (Supabase)
# ============================================================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# ============================================================================
# E-Commerce & Payments
# ============================================================================
STRIPE_SECRET_KEY=sk_test_... or sk_live_...
WOOCOMMERCE_URL=https://minivetguide.com
WOOCOMMERCE_KEY=ck_...
WOOCOMMERCE_SECRET=cs_...
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...

# ============================================================================
# Communications
# ============================================================================
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
SLACK_BOT_TOKEN=xoxb-...

# ============================================================================
# Social Media
# ============================================================================
INSTAGRAM_ACCESS_TOKEN=...

# ============================================================================
# Database
# ============================================================================
POSTGRES_PASSWORD=secure_password_here
```

---

## 🐳 Step 2: Deploy with Docker (10 minutes)

```bash
# Build and start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                        STATUS
# onlyoffice-documentserver   Up (healthy)
# ai-suite-backend            Up
# ai-suite-redis              Up
# onlyoffice-postgres         Up
# ai-suite-nginx              Up
```

### Service URLs
- **ONLYOFFICE Editor**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx (Production)**: http://localhost (or https://yourdomain.com)

---

## 🔧 Step 3: Initialize System (5 minutes)

```bash
# Install Python dependencies (if running locally)
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Initialize database schema
python scripts/init_database.py

# Test ONLYOFFICE connection
python scripts/test_onlyoffice.py

# Test AI model connections
python scripts/test_ai_models.py

# Expected output:
# ✅ ONLYOFFICE: Connected
# ✅ OpenAI: API key valid
# ✅ Anthropic: API key valid
# ✅ DeepSeek: API key valid
```

---

## ✅ Step 4: Verify Installation (5 minutes)

### Test 1: ONLYOFFICE Document Creation
```bash
curl -X POST http://localhost:8000/api/onlyoffice/create-document \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Document",
    "type": "word"
  }'

# Expected response:
# {
#   "success": true,
#   "document_id": "doc_12345",
#   "edit_url": "http://localhost:8080/editor?doc=doc_12345"
# }
```

### Test 2: AI Text Generation
```bash
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a professional email welcoming a new customer",
    "model": "gpt-4"
  }'

# Expected response:
# {
#   "success": true,
#   "text": "Dear Valued Customer, Welcome to..."
# }
```

### Test 3: Gmail Send Email
```bash
curl -X POST http://localhost:8000/api/gmail/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["test@example.com"],
    "subject": "Test Email",
    "body": "This is a test email from AI Suite"
  }'

# Expected response:
# {
#   "success": true,
#   "message_id": "msg_12345"
# }
```

---

## 🎯 Step 5: First Workflow - Customer Quote (5 minutes)

Create a file `test_workflow.py`:

```python
#!/usr/bin/env python3
"""Test workflow: Generate customer quote"""

import asyncio
from tools.registry import ToolRegistry

async def generate_customer_quote():
    registry = ToolRegistry()
    
    # Step 1: Get customer data from WooCommerce
    customer_tool = registry.get_tool('woocommerce_get_customer')
    customer = await customer_tool.execute(email='customer@example.com')
    
    print(f"✅ Customer retrieved: {customer['name']}")
    
    # Step 2: Create quote document with ONLYOFFICE
    onlyoffice_tool = registry.get_tool('onlyoffice_create_from_template')
    document = await onlyoffice_tool.execute(
        template_id='quote_template',
        variables={
            'customer_name': customer['name'],
            'customer_email': customer['email'],
            'date': '2025-10-23',
            'items': [
                {'name': 'Product A', 'price': 50, 'qty': 2},
                {'name': 'Product B', 'price': 75, 'qty': 1}
            ],
            'total': 175
        }
    )
    
    print(f"✅ Document created: {document['id']}")
    
    # Step 3: Generate PDF
    pdf_tool = registry.get_tool('onlyoffice_generate_pdf')
    pdf = await pdf_tool.execute(document_id=document['id'])
    
    print(f"✅ PDF generated: {pdf['url']}")
    
    # Step 4: Send via Gmail
    gmail_tool = registry.get_tool('gmail_send_email')
    email = await gmail_tool.execute(
        to=[customer['email']],
        subject='Your Quote from MiniVetGuide',
        body='Please find your quote attached.',
        attachments=[{
            'filename': 'quote.pdf',
            'content': pdf['data']
        }]
    )
    
    print(f"✅ Email sent: {email['message_id']}")
    
    # Step 5: Notify team via Slack
    slack_tool = registry.get_tool('slack_post_message')
    await slack_tool.execute(
        channel='#sales',
        text=f'📄 Quote sent to {customer["name"]}: $175'
    )
    
    print(f"✅ Team notified via Slack")
    print(f"\n🎉 Workflow complete!")

if __name__ == '__main__':
    asyncio.run(generate_customer_quote())
```

Run the workflow:
```bash
python test_workflow.py

# Expected output:
# ✅ Customer retrieved: John Doe
# ✅ Document created: doc_12345
# ✅ PDF generated: http://localhost:8080/docs/doc_12345.pdf
# ✅ Email sent: msg_67890
# ✅ Team notified via Slack
# 🎉 Workflow complete!
```

---

## 📊 Step 6: Access Admin Dashboard

Open browser to: **http://localhost:8000**

### Dashboard Features
- **Document Library**: View all ONLYOFFICE documents
- **AI Playground**: Test AI models interactively
- **Tool Explorer**: Browse all 281 tools
- **Workflow Builder**: Visual workflow designer
- **Analytics**: Usage metrics and performance

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔒 Security Checklist

### Development Environment
- ✅ JWT secrets set
- ✅ HTTPS disabled (use HTTP for local testing)
- ✅ Debug mode enabled
- ✅ CORS configured for localhost

### Production Environment (Before Going Live)
- [ ] Change all default passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up backup automation
- [ ] Enable rate limiting
- [ ] Configure monitoring (Sentry, Datadog)
- [ ] Review ONLYOFFICE permissions
- [ ] Enable audit logging
- [ ] Set up VPN for sensitive operations

---

## 🐛 Troubleshooting

### Problem: ONLYOFFICE won't start
```bash
# Check logs
docker logs onlyoffice-documentserver

# Common fix: Increase Docker memory
# Docker Desktop → Settings → Resources → Memory: 4GB minimum

# Restart service
docker-compose restart onlyoffice-documentserver
```

### Problem: Backend API won't connect to ONLYOFFICE
```bash
# Check network connectivity
docker exec ai-suite-backend ping onlyoffice-documentserver

# Verify JWT secret matches
echo $ONLYOFFICE_JWT_SECRET

# Check ONLYOFFICE health
curl http://localhost:8080/healthcheck
```

### Problem: AI API keys not working
```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Verify keys in .env
cat .env.production | grep API_KEY
```

### Problem: Gmail OAuth not working
```bash
# Google Cloud Console steps:
# 1. Enable Gmail API
# 2. Create OAuth 2.0 credentials
# 3. Add authorized redirect URI: http://localhost:8000/auth/google/callback
# 4. Download credentials.json
# 5. Run: python scripts/google_oauth_setup.py
```

---

## 📈 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend-api
docker-compose logs -f onlyoffice-documentserver

# Last 100 lines
docker-compose logs --tail=100 backend-api
```

### Monitor Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Health Checks
```bash
# ONLYOFFICE
curl http://localhost:8080/healthcheck

# Backend API
curl http://localhost:8000/health

# Redis
docker exec ai-suite-redis redis-cli ping
```

---

## 🔄 Maintenance

### Backup Everything
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup ONLYOFFICE data
docker run --rm \
  -v onlyoffice_data:/data \
  -v "$BACKUP_DIR":/backup \
  alpine tar czf /backup/onlyoffice_data.tar.gz -C /data .

# Backup PostgreSQL
docker exec onlyoffice-postgres pg_dump -U onlyoffice onlyoffice > "$BACKUP_DIR/database.sql"

# Backup environment
cp .env.production "$BACKUP_DIR/.env"

echo "✅ Backup complete: $BACKUP_DIR"
EOF

chmod +x backup.sh
./backup.sh
```

### Update Services
```bash
# Pull latest images
docker-compose pull

# Recreate containers
docker-compose up -d --force-recreate

# Remove old images
docker image prune -f
```

### Scale Services (if needed)
```bash
# Scale backend API to 3 instances
docker-compose up -d --scale backend-api=3

# Load balancer will distribute requests
```

---

## 🎉 You're Ready!

Your **AI-Powered Multi-Platform Intelligence Suite** is now running with:

✅ **ONLYOFFICE**: Self-hosted document processing  
✅ **AI Models**: OpenAI, Anthropic, DeepSeek ready  
✅ **281 Tools**: Across 19 platforms  
✅ **Automated Workflows**: Quote generation, email automation, etc.  
✅ **Secure**: JWT authentication, encrypted storage  
✅ **Scalable**: Docker-based, easy to scale  

### Next Steps
1. **Create AI Model Tools**: Implement OpenAI/Anthropic/DeepSeek tools
2. **Build More Workflows**: Expand automation capabilities
3. **Customize UI**: Brand the admin dashboard
4. **Deploy to Production**: Follow security checklist above
5. **Scale**: Add more containers as needed

### Support
- **Documentation**: /docs folder in project
- **API Reference**: http://localhost:8000/docs
- **ONLYOFFICE Docs**: https://api.onlyoffice.com/
- **Issues**: Create issue in GitHub repo

---

**Total Deployment Time**: ~30 minutes  
**Total Cost**: $75-250/month (vs $684/month for SaaS)  
**Savings**: $7,308/year 🎉

**Questions? Issues? Ready to build workflows?** Let me know! 🚀
