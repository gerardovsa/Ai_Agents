# Verify Azure AD App Exists

## 🚨 Current Issue

**Error:** `invalid_client` from Microsoft OAuth
**Client ID:** `324f7fef-50ac-4948-9f34-5f95b03ad818`
**Configuration:** ✅ All correct in Flask

**Problem:** Microsoft authorization server is rejecting this Client ID

---

## 🔍 Verify App Exists in Azure Portal

### Step 1: Check if App Exists

1. Go to: https://portal.azure.com
2. Navigate: **Azure Active Directory** → **App registrations**
3. Click **"All applications"** tab (not just "Owned applications")
4. Search for: `324f7fef-50ac-4948-9f34-5f95b03ad818`

### Step 2: Check App Status

If app is found:
- ✅ **Status:** Enabled (not disabled)
- ✅ **Name:** Valor AI Platform
- ✅ **Application ID:** 324f7fef-50ac-4948-9f34-5f95b03ad818

If app is NOT found:
- ❌ **App has been deleted**
- ❌ **App is in different tenant**
- ❌ **You don't have permission to see it**

---

## 🛠️ Solutions

### Option A: App Was Deleted → Create New App

If the app doesn't exist, you need to create a new one:

```powershell
# Run this script to create new Azure AD app
python create_new_azure_app.py
```

Or manually:
1. Azure Portal → App registrations → **New registration**
2. Name: `Valor AI Platform`
3. Supported account types: **Accounts in any organizational directory (Multitenant)**
4. Redirect URI: 
   - Platform: **Web**
   - URI: `http://localhost:5001/api/auth/microsoft/callback`
5. Click **Register**
6. Copy **Application (client) ID**
7. Go to **Certificates & secrets** → **New client secret**
8. Copy the **Value** (not Secret ID)
9. Update `.env.master`:
   ```
   MICROSOFT_CLIENT_ID=<new_client_id>
   MICROSOFT_CLIENT_SECRET=<new_secret_value>
   ```
10. Restart: `BISTART`

### Option B: App Exists but Wrong Tenant

If you see the app but OAuth still fails:

1. Check which **tenant** the app is registered in
2. Verify **publisherDomain** in manifest matches your tenant
3. Make sure **signInAudience**: `AzureADMultipleOrgs`

### Option C: Permissions Issue

You might not have permission to use this app:

1. Check **Owners** section in app registration
2. Add yourself as owner if missing
3. Or ask the app owner to grant you access

---

## 🧪 Quick Test

Try accessing the app directly via Microsoft Graph API:

```powershell
# Test if app is accessible
$clientId = "324f7fef-50ac-4948-9f34-5f95b03ad818"
$response = Invoke-WebRequest -Uri "https://graph.microsoft.com/v1.0/applications?`$filter=appId eq '$clientId'" -Headers @{Authorization="Bearer <your_token>"}
```

---

## 📋 What to Check in Azure Portal

1. **App registrations** → Search for `324f7fef-50ac-4948-9f34-5f95b03ad818`
2. **Authentication** → Verify:
   - ✅ Redirect URI: `http://localhost:5001/api/auth/microsoft/callback`
   - ✅ Supported account types: Multitenant
3. **Certificates & secrets** → Verify:
   - ✅ Active client secret exists (not expired)
   - ✅ Hint matches: `0eR`
4. **API permissions** → Verify:
   - ✅ User.Read permission granted

---

## 🎯 Next Steps

1. **Verify app exists** in Azure Portal
2. If app exists:
   - Check all settings match above
   - Generate NEW client secret
   - Update `.env.master`
3. If app doesn't exist:
   - Create new app with steps above
   - Update `.env.master` with new credentials
4. Restart Flask: `BISTART`
5. Test again

---

**Current Status:**
- ✅ Flask configuration correct
- ✅ Client ID matches expected value
- ✅ Multi-tenant endpoint used
- ❌ Microsoft rejects Client ID → **App likely deleted or inaccessible**
