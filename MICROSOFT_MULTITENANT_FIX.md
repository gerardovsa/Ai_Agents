# Microsoft 365 Multi-Tenant Authentication Fix

## 🎯 Problem Summary

**Error:** `invalid_client` when trying to sign in with Microsoft 365 account

**Root Cause:** Azure AD app is configured as **single-tenant** but your platform needs **multi-tenant** support to work with ANY Microsoft 365 organization.

**Your OAuth Configuration:** ✅ Already correct for multi-tenant
- Environment: `MICROSOFT_TENANT_ID=common` ✅
- OAuth Manager: Uses `"common"` endpoint ✅  
- Code: Multi-tenant support already built-in ✅

**The Issue:** Azure AD app registration in Azure Portal is configured as single-tenant

---

## ✅ Quick Fix (Recommended)

### Automated Fix (If Azure CLI installed)

```powershell
# Run automated fixer
python fix_azure_multitenant.py
```

This script will:
1. Login to Azure (opens browser)
2. Find your app by Client ID
3. Update `signInAudience` to `AzureADMultipleOrgs`
4. Verify redirect URIs
5. Confirm changes

**Then:**
```powershell
# Wait 2-3 minutes for Azure to propagate changes
Start-Sleep -Seconds 180

# Restart server
BISTOP
BISTART

# Try Microsoft login again
```

---

## 📋 Manual Fix (If Azure CLI not available)

### Step 1: Open Azure Portal

1. Go to: https://portal.azure.com
2. Navigate: **Azure Active Directory** → **App registrations**
3. Find your app by searching for: `324f7fef-50ac-4948-9f34-5f95b03ad818`

### Step 2: Enable Multi-tenant (Option A - Authentication Page)

1. Click on your app
2. Click **Authentication** in left sidebar
3. Under **Supported account types**, select:
   ```
   ● Accounts in any organizational directory (Any Azure AD directory - Multitenant)
   ```
4. Under **Platform configurations** → **Web** → **Redirect URIs**:
   - Verify this URI exists: `http://localhost:5001/api/auth/microsoft/callback`
   - If not, click **Add URI** and add it
5. Click **Save**

### Step 2: Enable Multi-tenant (Option B - Manifest)

1. Click on your app
2. Click **Manifest** in left sidebar
3. Find line: `"signInAudience": "AzureADMyOrg"`
4. Change to: `"signInAudience": "AzureADMultipleOrgs"`
5. Find `"replyUrlsWithType"` array
6. Ensure it contains:
   ```json
   {
     "url": "http://localhost:5001/api/auth/microsoft/callback",
     "type": "Web"
   }
   ```
7. Click **Save**

### Step 3: Restart Server

```powershell
BISTOP
Start-Sleep -Seconds 180  # Wait 3 minutes for Azure propagation
BISTART
```

### Step 4: Test Login

Try signing in with Microsoft 365 again. Should work now!

---

## 🔍 Verification

After making changes, verify multi-tenant configuration:

```powershell
# Run diagnostics
python diagnose_m365_oauth.py
```

Expected output:
```
✓ Tenant ID: common (common = multi-tenant)
✓ Client ID: 324f7fef-50ac-4948-9f34-5f95b03ad818
✓ Redirect URI: http://localhost:5001/api/auth/microsoft/callback
```

---

## 🚨 If Still Getting "invalid_client" Error

If multi-tenant is configured correctly but you still get the error, it's likely:

### Issue: Client Secret Expired or Incorrect

**Fix:**
1. Azure Portal → Your app → **Certificates & secrets**
2. Under **Client secrets**:
   - Check if secret exists
   - Check expiration date
3. If expired or unsure, create **NEW secret**:
   - Click **New client secret**
   - Description: `Valor AI Platform`
   - Expires: `24 months`
   - Click **Add**
4. **COPY the Value** (not the Secret ID!)
5. Update `.env.master`:
   ```
   MICROSOFT_CLIENT_SECRET=<paste_new_value_here>
   ```
6. Restart: `BISTOP` then `BISTART`

---

## 📊 What This Enables

Once multi-tenant is configured, your platform can:

✅ Accept sign-ins from **ANY Microsoft 365 organization**
- `gerardo@vetsuccessacademy.com` ✅
- `gerardo@minivetguide.onmicrosoft.com` ✅  
- `user@anydomain.onmicrosoft.com` ✅
- `user@company.com` (if company uses M365) ✅

✅ Use Microsoft tools with **any user's credentials**
- Outlook email
- Microsoft Teams
- OneDrive
- Calendar
- Excel Online
- Word Online
- OneNote
- SharePoint
- And more...

✅ **Multi-organization support** for SaaS deployment

---

## 🔧 Technical Details

### OAuth Endpoints (Already Correct)

Your configuration uses the **common** endpoint:

```
Auth: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
Token: https://login.microsoftonline.com/common/oauth2/v2.0/token
```

This is correct for multi-tenant. The `common` endpoint:
- Works with **any** Azure AD tenant
- Works with **any** organizational directory
- Dynamically handles tenant-specific authentication

### Sign-in Audience Values

| Value | Description | Your Need |
|-------|-------------|-----------|
| `AzureADMyOrg` | Single tenant only | ❌ Current (causing error) |
| `AzureADMultipleOrgs` | Any Azure AD directory | ✅ **Required** |
| `AzureADandPersonalMicrosoftAccount` | Azure AD + personal MSA | ⚠️ Not needed |
| `PersonalMicrosoftAccount` | Personal MSA only | ❌ Not needed |

You need: **AzureADMultipleOrgs**

### Redirect URI

Must be registered in Azure AD app:
```
http://localhost:5001/api/auth/microsoft/callback
```

This is where Microsoft redirects after user authorizes.

---

## 🧪 Testing Multi-tenant

After fixing, test with different organizations:

### Test Case 1: MiniVetGuide Tenant
```
Email: gerardo@minivetguide.onmicrosoft.com
Password: Vetsuccess11!
```

### Test Case 2: VetSuccessAcademy Domain
```
Email: gerardo@vetsuccessacademy.com
(If this domain is configured in a M365 tenant)
```

### Test Case 3: AI Agent Integration
```powershell
# Start server
BISTART

# Wait for tools to load (15 seconds)
Start-Sleep -Seconds 15

# Test Microsoft tool via AI agent
CHAT "List my Outlook emails"
```

Expected: AI agent uses your M365 credentials from database to access Outlook

---

## 📁 Files Modified/Created

### New Diagnostic Tools
- `diagnose_m365_oauth.py` - Diagnoses invalid_client error
- `fix_azure_multitenant.py` - Automated Azure AD configuration
- `MICROSOFT_MULTITENANT_FIX.md` - This guide

### Existing Files (Already Correct)
- `.env.master` - `MICROSOFT_TENANT_ID=common` ✅
- `Microsoft_365_Connection/microsoft365_oauth_manager.py` - Multi-tenant support ✅
- `AI_infrastructure/routes/microsoft_auth_routes.py` - Uses common endpoint ✅

---

## 🎓 Understanding the Error

### What "invalid_client" Means

The error occurs when Microsoft's OAuth server rejects your client credentials:

```
Error: invalid_client
Description: The client identifier provided in the request is invalid
```

**Possible Causes:**
1. **Client ID doesn't exist** (not your issue - ID is valid)
2. **Client Secret is wrong** (possible - check if needed)
3. **App not configured for requested tenant** (MOST LIKELY - you have this)

Your case: **App not configured for multi-tenant**, so when `gerardo@minivetguide.onmicrosoft.com` tries to sign in, Azure says "this app only works with one specific tenant, not yours."

### Why Multi-tenant Fixes It

When you set `signInAudience` to `AzureADMultipleOrgs`:
- Azure accepts sign-ins from **any** organizational directory
- User's tenant is dynamically identified from their email
- App can work with **unlimited** organizations

---

## 🚀 Next Steps After Fix

Once multi-tenant is working:

1. **Test Microsoft Login**
   - Try signing in with `gerardo@minivetguide.onmicrosoft.com`
   - Should redirect to Microsoft login → authorize → redirect back with token

2. **Verify Token Storage**
   ```powershell
   python check_microsoft_creds.py
   ```
   Should show tokens stored in `user_platform_credentials` table

3. **Test AI Agent Tools**
   ```powershell
   CHAT "Send a test email via Outlook"
   CHAT "List my OneDrive files"
   CHAT "What's on my calendar today?"
   ```

4. **Test with Multiple Accounts**
   - Sign in with different M365 accounts
   - Each should get their own tokens
   - Each should access their own data

---

## 📞 Support

If you continue having issues:

1. **Run diagnostics:**
   ```powershell
   python diagnose_m365_oauth.py
   ```

2. **Check server logs:**
   ```powershell
   # Look for Microsoft auth errors
   Get-Content C:\Users\gpoli\GIT\AI_agents\logs\app.log | Select-String "microsoft|oauth|invalid"
   ```

3. **Verify environment:**
   ```powershell
   # Check .env.master values
   Get-Content .env.master | Select-String "MICROSOFT"
   ```

---

**Document Version:** 1.0  
**Last Updated:** October 28, 2025  
**Status:** ✅ Ready for implementation
