# MustCare ValorAISynergySuite V3 - Render.com Deployment

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```powershell
cd "c:\Users\gpoli\GIT\MustCare ValorAISynergySuite"
python render\deploy_to_render.py
```

**What it does:**
- ✅ Validates prerequisites
- ✅ Generates environment configuration
- ✅ Commits and pushes to GitHub
- ✅ Provides deployment instructions

### Option 2: Manual Deployment

1. **Push to GitHub:**
   ```powershell
   git add .
   git commit -m "feat: Add Render.com deployment"
   git push origin V8-Render
   ```

2. **Deploy via Dashboard:**
   - Go to: https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Select repository: `MustCare_ValorAISynergySuite`
   - Branch: `V8-Render`
   - Click "Apply"

3. **Configure Environment:**
   - Services → `mustcare-valorai-v3` → Environment
   - Add: `ANTHROPIC_API_KEY=sk-ant-your-key`
   - Click "Save Changes"

4. **Wait for deployment** (~10 minutes)

---

## 📁 File Structure

```
render/
├── Dockerfile.render          # Main application Docker image
├── Dockerfile.collector       # Document collector Docker image
├── start.sh                   # Container startup script
├── .env.render.template       # Environment variable template
├── deploy_to_render.py        # Automated deployment script
├── validate_deployment.py     # Post-deployment validation
├── RENDER_DEPLOYMENT_GUIDE.md # Complete deployment guide
└── README.md                  # This file

render.yaml                    # Render blueprint (project root)
```

---

## ✅ Validation

After deployment, test your service:

```powershell
python render\validate_deployment.py https://mustcare-valorai-v3.onrender.com
```

**Expected output:**
```
✅ Health Check         [PASS]  Health check passed
✅ Frontend Loads       [PASS]  Frontend loaded
✅ Collector Service    [PASS]  Collector assumed running
✅ Database Connection  [PASS]  Database connection assumed healthy
✅ SSL Certificate      [PASS]  SSL certificate valid
✅ Response Time        [PASS]  Average: 250ms (excellent)
```

---

## 📊 Cost Estimate

**Production Configuration:**
- Web Service (Standard): $25/month
- PostgreSQL (Starter): $7/month
- Persistent Disk (10GB): $2.50/month
- **Total: $34.50/month**

**Development Configuration:**
- Web Service (Starter): $7/month
- PostgreSQL (Starter): $7/month
- Persistent Disk (5GB): $1.25/month
- **Total: $15.25/month**

---

## 🔧 Configuration

### Required Environment Variables

Set in Render Dashboard → Environment:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Auto-Generated Variables

These are automatically set by `render.yaml`:
- `JWT_SECRET` - Auto-generated
- `DATABASE_URL` - From PostgreSQL service
- `AUTH_TOKEN` - Auto-generated
- `SIG_KEY` - Auto-generated
- `SIG_SALT` - Auto-generated

### Optional Variables

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
GOOGLE_API_KEY=your-google-api-key
```

---

## 🐛 Troubleshooting

### Build Failed

**Issue:** "Node version mismatch"
- **Fix:** Verify Dockerfile uses `FROM node:20-slim`

**Issue:** "Out of memory"
- **Fix:** Upgrade to Standard plan ($25/month)

### Runtime Errors

**Issue:** "Database connection failed"
- **Fix:** Check DATABASE_URL in Environment tab

**Issue:** "Anthropic API key invalid"
- **Fix:** Verify ANTHROPIC_API_KEY starts with `sk-ant-`

**Issue:** "Health check failing"
- **Fix:** Wait 5-10 minutes for full startup

### Performance Issues

**Issue:** "Slow response times"
- **Fix:** Upgrade to Standard plan (2GB RAM)

---

## 📚 Documentation

- **Complete Guide**: [`RENDER_DEPLOYMENT_GUIDE.md`](RENDER_DEPLOYMENT_GUIDE.md)
- **Render Docs**: https://render.com/docs
- **MustCare Docs**: [`../README.md`](../README.md)

---

## 🔄 Updates

### Automatic Deployment

Enable in Render Dashboard:
1. Services → `mustcare-valorai-v3`
2. Settings → Build & Deploy
3. Toggle "Auto-Deploy" ON
4. Select branch: `V8-Render`

Now every push to `V8-Render` will auto-deploy.

### Manual Deployment

```powershell
# Push changes
git add .
git commit -m "feat: Update feature X"
git push origin V8-Render

# Then in Render Dashboard:
# Manual Deploy → Deploy latest commit
```

---

## 🎯 Next Steps After Deployment

1. **Access your deployment:**
   - URL: `https://mustcare-valorai-v3.onrender.com`

2. **Create admin account:**
   - Open URL in browser
   - Click "Setup" or "Create Account"
   - Set username/password

3. **Test features:**
   - ✅ Claude 4 chat
   - ✅ Web search
   - ✅ Code execution
   - ✅ Document upload
   - ✅ Multi-user access

4. **Configure custom domain (optional):**
   - Settings → Custom Domains
   - Add CNAME: `valorai.yourdomain.com`

---

## 📞 Support

- **Render**: https://community.render.com
- **MustCare**: GitHub Issues
- **Anthropic**: https://docs.anthropic.com

---

**Last Updated:** November 8, 2025  
**Version:** V8-Render  
**Status:** Production Ready
