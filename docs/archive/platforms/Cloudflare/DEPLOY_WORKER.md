# 🚀 HOW TO DEPLOY THE MUSTCARE WORKER

## What This Worker Does:
Acts as an API Gateway/Proxy between your Chrome extension and the backend server (34.143.73.2)

## Option 1: Deploy via Cloudflare Dashboard (EASIEST)

### Step 1: Copy the Worker Code
Open file: `mustcare-worker.js` and copy all the code

### Step 2: Create New Worker
1. Go to: https://dash.cloudflare.com/d31a1c9ec65f373f4008216c30b071cc/workers-and-pages
2. Click **"Create Application"**
3. Select **"Create Worker"**
4. Name it: **mustcare-worker**
5. Click **"Deploy"**

### Step 3: Edit the Worker
1. Click **"Edit Code"**
2. **Delete** all the default code
3. **Paste** the code from `mustcare-worker.js`
4. Click **"Save and Deploy"**

### Step 4: Add Route
1. Click **"Settings"** tab
2. Click **"Triggers"**
3. Click **"Add Route"**
4. Enter: `mustcare.valorsynergysuite.com/*`
5. Select Zone: `valorsynergysuite.com`
6. Click **"Save"**

### Step 5: Test
```
https://mustcare.valorsynergysuite.com/health
```
Should return: `{"status":"ok","timestamp":"...","worker":"mustcare-api-gateway"}`

---

## Option 2: Deploy via Wrangler CLI (ADVANCED)

### Prerequisites:
```powershell
# Install Node.js (if not already installed)
# Then install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

### Deploy:
```powershell
cd c:\Users\gpoli\GIT\AI_agents\Cloudflare

# Deploy the worker
wrangler deploy

# View logs
wrangler tail
```

---

## 🧪 Testing After Deployment

### Test 1: Health Check
```powershell
curl https://mustcare.valorsynergysuite.com/health
```
Expected: `{"status":"ok",...}`

### Test 2: API Endpoint
```powershell
curl https://mustcare.valorsynergysuite.com/api/admin/workspaces
```
Expected: Response from your backend (not 404)

### Test 3: Chrome Extension
Open your extension and try to login/use it normally

---

## 🔧 What Changed from the Old Worker?

### ✅ Added:
- **Global try-catch** - Won't crash anymore
- **JSON error responses** - No more HTML error pages
- **CORS headers** - Proper cross-origin support
- **Health check endpoint** - Easy testing
- **Timeout protection** - Won't hang forever
- **Logging** - Can see what's happening

### ❌ Removed:
- Whatever was causing Error 1101

---

## ⚠️ Important Notes:

1. **Backend URL**: Currently set to `http://34.143.73.2`
   - If your backend is on a different URL/port, update line 47 in the Worker

2. **HTTPS**: The backend URL uses HTTP
   - If your backend requires HTTPS, change to `https://...`

3. **Authentication**: The Worker passes through all headers
   - Your auth should work as before

4. **Routes**: Make sure the route `mustcare.valorsynergysuite.com/*` is added
   - This ensures all traffic goes through the Worker

---

## 🐛 Troubleshooting

### Still getting 404?
- Check that the route is properly configured
- Verify backend server is running on 34.143.73.2
- Test backend directly: `curl http://34.143.73.2/api/health`

### Still getting Error 1101?
- Check Worker logs in Dashboard → Workers → mustcare-worker → Logs
- The error message will now be in JSON format

### Can't deploy?
- Make sure you have Workers Edit permission on your API token
- Try deploying via Dashboard instead of CLI

---

**Ready to deploy?** Choose Option 1 (Dashboard) for the easiest method!
