# 🔐 Module Creator - Credential Testing Guide

## Overview

The Module Creator Enhanced now includes **built-in credential management** for testing modules that connect to external APIs. This allows you to:

1. **Add test credentials** for any platform
2. **Test API connections** before deploying your module
3. **Auto-inject credentials** into the live preview iframe
4. **Verify authentication** without hardcoding keys

---

## 🎯 Features

### ✅ What's Included

- **17+ Pre-configured Platforms** (OpenAI, Stripe, Shopify, Pinecone, etc.)
- **Custom API Support** (bring your own endpoints)
- **Real API Testing** (uses `/api/auth/credentials/test` endpoint)
- **Secure Storage** (credentials stored in browser memory only, never saved to disk)
- **Status Indicators** (Untested, Success, Error badges)
- **One-Click Injection** (inject credentials into iframe for testing)

---

## 📋 How to Use

### Step 1: Open Credential Panel

1. Open Module Creator: `http://localhost:5001/dev-tools/module-creator-enhanced.html`
2. In the left sidebar, find **"Test Credentials"** section
3. Click the **dropdown arrow** (▼) to expand the panel

### Step 2: Add Credentials

**For OpenAI:**
```
1. Select Platform: "OpenAI"
2. Enter API Key: sk-proj-abc123...
3. Click "Test Connection" (optional but recommended)
4. Click "Save"
```

**For Shopify:**
```
1. Select Platform: "Shopify"
2. Enter API Key: shpat_abc123...
3. Enter Shop Domain: mystore.myshopify.com
4. Click "Test Connection"
5. Click "Save"
```

**For Custom API:**
```
1. Select Platform: "Custom API"
2. Enter API Key: your_custom_key
3. Click "Save" (test connection may not work for custom)
```

### Step 3: Test Connection

The **"Test Connection"** button makes a real API call to verify credentials:

**What happens:**
1. Sends POST request to `/api/auth/credentials/test`
2. Backend calls the actual platform API (non-destructive read-only call)
3. Returns success/failure with details
4. Updates credential status badge

**Example Results:**

**✅ Success (OpenAI):**
```
✅ Connection Successful
Connected to OpenAI successfully
Details: {"models": ["gpt-4", "gpt-3.5-turbo"], "model_count": 2}
```

**❌ Error (Invalid Key):**
```
❌ Connection Failed
Invalid API key provided
```

### Step 4: Inject into Preview

Once credentials are saved, you can inject them into your module preview:

**Method 1: Manual Injection**
1. Click the **syringe icon** (💉) next to a saved credential
2. Credential is sent to iframe via `postMessage`
3. Your module code receives it via event listener

**Method 2: Auto-Injection (in your module code)**
```javascript
// Listen for credential injection
window.addEventListener('message', (event) => {
    if (event.data.type === 'INJECT_CREDENTIAL') {
        const platform = event.data.platform;
        const credentials = event.data.credentials;
        
        // Use credentials in your module
        console.log('Received credentials for:', platform);
        console.log('API Key:', credentials.API_KEY);
        
        // Make authenticated API call
        fetch('https://api.example.com/data', {
            headers: {
                'Authorization': `Bearer ${credentials.API_KEY}`
            }
        });
    }
});
```

**Method 3: Access All Credentials**
```javascript
// From within iframe, access parent's credentials
if (window.parent.moduleCreator) {
    const allCreds = window.parent.moduleCreator.getAllTestCredentials();
    console.log('Available platforms:', Object.keys(allCreds));
    
    // Use specific platform
    const openaiKey = allCreds.openai?.API_KEY;
}
```

---

## 🧪 Testing Workflow Example

### Example: Building a "Shopify Orders" Module

**1. Create Module Structure**
```
Module ID: shopify-orders
Module Name: Shopify Orders Dashboard
```

**2. Add Shopify Credentials**
```
Platform: Shopify
API Key: shpat_your_key_here
Shop Domain: yourstore.myshopify.com
```

**3. Test Connection**
```
Click "Test Connection"
✅ Result: "Shopify connection successful"
Details: {"shop_name": "Your Store", "plan": "basic"}
```

**4. Write Module Code (HTML)**
```html
<div id="shopify-orders">
    <h2>Recent Orders</h2>
    <button id="load-orders">Load Orders</button>
    <div id="orders-list"></div>
</div>
```

**5. Write Module Code (JavaScript)**
```javascript
class ShopifyOrdersModule {
    constructor() {
        this.credentials = null;
        this.init();
    }
    
    init() {
        // Listen for credential injection
        window.addEventListener('message', (event) => {
            if (event.data.type === 'INJECT_CREDENTIAL' && 
                event.data.platform === 'shopify') {
                this.credentials = event.data.credentials;
                console.log('✅ Shopify credentials received');
            }
        });
        
        // Bind load orders button
        document.getElementById('load-orders').onclick = () => {
            this.loadOrders();
        };
    }
    
    async loadOrders() {
        if (!this.credentials) {
            alert('Please inject Shopify credentials first');
            return;
        }
        
        const shopDomain = this.credentials.shop_domain;
        const apiKey = this.credentials.API_KEY;
        
        const response = await fetch(
            `https://${shopDomain}/admin/api/2024-01/orders.json`,
            {
                headers: {
                    'X-Shopify-Access-Token': apiKey
                }
            }
        );
        
        const data = await response.json();
        this.renderOrders(data.orders);
    }
    
    renderOrders(orders) {
        const list = document.getElementById('orders-list');
        list.innerHTML = orders.map(order => `
            <div class="order">
                <strong>Order #${order.order_number}</strong>
                <span>${order.total_price} ${order.currency}</span>
            </div>
        `).join('');
    }
}

window.shopifyModule = new ShopifyOrdersModule();
```

**6. Test in Live Preview**
```
1. Click syringe icon (💉) next to Shopify credential
2. Check console: "✅ Shopify credentials received"
3. Click "Load Orders" button in preview
4. Orders load from real Shopify API!
```

---

## 🔒 Security Notes

### ✅ Safe Practices

1. **Credentials stored in browser memory only**
   - Never written to disk
   - Lost when page refreshes (by design)
   - Not accessible to other browser tabs

2. **Test endpoint uses real authentication**
   - Requires valid JWT token
   - Calls backend API securely
   - Credentials encrypted in transit

3. **Preview iframe isolation**
   - Uses `postMessage` (secure cross-frame communication)
   - Credentials only injected when you click the button
   - No automatic credential exposure

### ⚠️ Important Warnings

1. **Don't commit credentials to Git**
   - These are for testing only
   - Use environment variables in production

2. **Refresh clears all credentials**
   - Credentials are not persistent
   - You'll need to re-enter after page reload

3. **Use test/development keys**
   - Never use production API keys
   - Create separate test accounts when possible

---

## 📊 Supported Platforms

| Platform | Fields Required | Test Method |
|----------|----------------|-------------|
| **OpenAI** | API Key | List models |
| **Anthropic** | API Key | List models |
| **Pinecone** | API Key | List indexes |
| **Stripe** | Secret Key | Get account |
| **Shopify** | API Key, Shop Domain | Get shop details |
| **Twilio** | Account SID, Auth Token | Verify account |
| **SendGrid** | API Key | Verify key |
| **Supabase** | URL, Anon Key | Test connection |
| **Custom** | API Key | Manual testing |

---

## 🐛 Troubleshooting

### Issue: "Test Connection" Returns 404

**Cause:** Flask server not running or auth endpoint missing

**Fix:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
BISTART
```

### Issue: Credentials Not Injecting

**Cause:** Iframe not receiving `postMessage`

**Fix:**
```javascript
// In your module JavaScript, add this listener at the TOP
window.addEventListener('message', (event) => {
    console.log('Message received:', event.data);
    
    if (event.data.type === 'INJECT_CREDENTIAL') {
        console.log('✅ Credential injected:', event.data.platform);
        // Store credentials
        window.myCredentials = event.data.credentials;
    }
});
```

### Issue: "Invalid API Key" Error

**Cause:** Wrong key format or expired key

**Fix:**
1. Verify key format (OpenAI starts with `sk-proj-`)
2. Check platform documentation for key format
3. Generate new key from platform dashboard

### Issue: Credentials Lost After Refresh

**Cause:** This is expected behavior (security feature)

**Solution:**
- Re-enter credentials after refresh
- Or: Use browser localStorage (less secure)
```javascript
// Save to localStorage (use with caution)
localStorage.setItem('test_credential_openai', apiKey);

// Restore after refresh
const savedKey = localStorage.getItem('test_credential_openai');
```

---

## 🎓 Best Practices

### 1. Test Early, Test Often
```
✅ Add credentials FIRST before writing code
✅ Test connection BEFORE building module
✅ Use real data for realistic testing
```

### 2. Handle Missing Credentials Gracefully
```javascript
if (!this.credentials) {
    // Show helpful message
    this.showMessage('Please inject credentials to continue');
    return;
}
```

### 3. Use Environment Variables in Production
```javascript
// Development (Module Creator)
const apiKey = credentials.API_KEY;

// Production (deployed module)
const apiKey = process.env.OPENAI_API_KEY;
```

### 4. Add Loading States
```javascript
async loadData() {
    this.showLoading(true);
    
    try {
        const response = await fetch(API_URL, {
            headers: { 'Authorization': `Bearer ${this.credentials.API_KEY}` }
        });
        const data = await response.json();
        this.render(data);
    } catch (error) {
        this.showError(error.message);
    } finally {
        this.showLoading(false);
    }
}
```

---

## 📞 Support

**Documentation:**
- Main docs: `AI_PROMPT.md`
- Credential system: `CREDENTIAL_SECURITY_IMPROVEMENTS_NOV29.md`
- Testing guide: `test_credential_security.py`

**Test Endpoint:**
```bash
curl -X POST http://localhost:5001/api/auth/credentials/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT" \
  -d '{
    "platform": "openai",
    "credentials": {"API_KEY": "sk-test..."},
    "settings": {}
  }'
```

---

**Now you can build and test modules with real API credentials without ever hardcoding keys! 🎉**
