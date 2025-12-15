# Module Creator Quick Start 🚀

**Get started in 60 seconds!**

---

## Step 1: Start Flask (10 seconds)

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python AI_infrastructure\flask_app.py
```

**Wait for:** `Running on http://127.0.0.1:5001`

---

## Step 2: Open Module Creator (5 seconds)

```powershell
Start-Process "c:\Users\gpoli\GIT\AI_agents\dev-tools\module-creator.html"
```

**Or:** Double-click `module-creator.html` in File Explorer

---

## Step 3: Verify Connection (5 seconds)

Look at the header:
- ✅ **Backend Connected** (green dot)
- ✅ **Database Connected** (green dot)

If red, restart Flask server.

---

## Step 4: Create Your First Module (40 seconds)

### Fill Out Form:

```
Module ID:       test_module
Name:            Test Module
Version:         1.0.0
Description:     My first test module
Icon:            fas fa-cube
```

### Select Files:
- ☑ **HTML Template**
- ☑ **JavaScript Controller**
- ☑ **CSS Stylesheet**
- ☐ Flask Routes _(skip for now)_

### Features:
- ☑ **Requires Authentication**
- ☑ **Show in Sidebar**
- ☐ Auto-load
- ☐ Main Tab

### Click: **"Create Module"**

---

## Step 5: Check Results

### Console Output:
```
INFO: Module created successfully
INFO: Files created: 4
```

### Files Created:
```
c:\Users\gpoli\GIT\AI_agents\UI\modules_external\test_module\
├── manifest.json
├── test_module.html
├── test_module.js
└── test_module.css
```

---

## ✅ Success!

You've created your first module in under 60 seconds!

**Next Steps:**
1. Edit generated files in VS Code
2. Restart Flask to load new module
3. Test in main UI
4. Deploy to production

---

## 🎯 Common Tasks

### Load Existing Module
1. Select **"Existing Module"** radio button
2. Choose module from dropdown
3. Form populates automatically
4. Edit and click **"Save to Module"**

### Validate Manifest
1. Fill out form
2. Click **"Validate Manifest"**
3. Check console for errors
4. Fix issues and validate again

### Test API Endpoint
1. Click **"API Tester"** tab
2. Select method (GET/POST)
3. Enter endpoint: `/api/modules`
4. Click **"Send Request"**
5. View response

### Download Manifest
1. Click **"Manifest Editor"** tab
2. Click **"Download JSON"**
3. File saves as `manifest.json`

---

## 🔧 Troubleshooting

### Backend Disconnected (Red Dot)
**Problem:** Flask server not running  
**Solution:** `python AI_infrastructure\flask_app.py`

### Module Already Exists (409 Error)
**Problem:** Module ID taken  
**Solution:** Use different ID or load existing module

### Validation Errors
**Problem:** Invalid manifest data  
**Solution:** Check console for specific errors

---

## 📚 Full Documentation

- **Complete Guide:** `dev-tools/README.md`
- **Visual Guide:** `dev-tools/VISUAL_GUIDE.md`
- **Implementation Details:** `dev-tools/IMPLEMENTATION_SUMMARY.md`

---

**Happy Module Building! 🎉**
