# Quick Reference - Microsoft Outlook & Xero Changes

## Microsoft Outlook Email - PERMANENTLY DISABLED ✋

### What Changed:
- **`microsoft_outlook_send_email`** now ONLY saves drafts
- Does NOT send emails automatically
- Users must manually send from Outlook app

### When User Asks to Send Email via Outlook:

**❌ Don't Say:**
- "Email sent to..."
- "I've sent the email..."
- "Message delivered to..."

**✅ Do Say:**
- "I've saved your email as a DRAFT in Outlook"
- "Your email is ready in your Outlook Drafts folder"
- "Please open Outlook and manually send this email from Drafts"

### Alternative Sending Methods:
- **Gmail:** Use `gmail_send_email` (actually sends)
- **Resend:** Use `resend_send_email` (transactional emails)
- **Outlook:** Draft-only, manual sending required

---

## Xero Accounting Tools - NOW WORKING ✅

### What Was Fixed:
- Added Xero platform to credential injection system
- Xero tools now receive proper authentication
- All 15 Xero tools operational

### How to Use Xero Tools:

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Get invoices from InHouse Print (business_id: 1)
invoices = registry.execute_tool(
    'xero_get_invoices',
    business_id=1,
    status='AUTHORISED',
    _user_id=1
)

# Get contacts from InHouse Publishing (business_id: 2)
contacts = registry.execute_tool(
    'xero_get_contacts',
    business_id=2,
    search='Smith',
    _user_id=1
)

# Get bank transactions from InHouse Signs (business_id: 3)
transactions = registry.execute_tool(
    'xero_get_bank_transactions_by_date_range',
    business_id=3,
    from_date='2025-11-01',
    to_date='2025-11-30',
    _user_id=1
)
```

### Business IDs:
- **1** = InHouse Print
- **2** = InHouse Publishing  
- **3** = InHouse Signs

### Credentials Required in `.env.master`:
```bash
# InHouse Print
XERO_PRINT_CLIENT_ID=your_client_id
XERO_PRINT_CLIENT_SECRET=your_client_secret

# InHouse Publishing
XERO_PUB_CLIENT_ID=your_client_id
XERO_PUB_CLIENT_SECRET=your_client_secret

# InHouse Signs
XERO_SIGNS_CLIENT_ID=your_client_id
XERO_SIGNS_CLIENT_SECRET=your_client_secret
```

---

## Files Modified Summary

| File | What Changed |
|------|-------------|
| `tools/schemas/microsoft_outlook_tools.json` | Added PERMANENT disable warnings |
| `tools/implementations/microsoft_outlook_tools.py` | Updated docstring, draft-only behavior |
| `AI_infrastructure/auth/credential_injector.py` | Added Xero platform support |
| `AI_infrastructure/prompts/tool_usage_system_prompt.md` | Added Outlook restrictions section |

---

## Testing Commands

### Test Microsoft Outlook (via AI):
```
User: "Send an email to test@example.com via Outlook"

Expected Response:
"I've saved your email as a DRAFT in Outlook. 
Please open Outlook and manually send it from your Drafts folder."
```

### Test Xero (via Python):
```python
cd C:\Users\gpoli\GIT\AI_Agents_v9
python validate_changes.py  # Run validation
```

### Test Xero Tool:
```python
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(r.execute_tool('xero_get_contacts', business_id=1, _user_id=1))"
```

---

## Troubleshooting

### Outlook Issues:
**Problem:** User complains email wasn't sent  
**Solution:** Explain draft-only behavior, direct to Outlook Drafts folder

**Problem:** Developer tries to reactivate sending  
**Solution:** Point to warnings in schema/code, explain security requirements

### Xero Issues:
**Problem:** "XeroAPIClient not available"  
**Solution:** Check that `UI/external/modules/xero/xero_routes.py` exists

**Problem:** "Failed to get Xero access token"  
**Solution:** Verify credentials in `.env.master` for correct business_id

**Problem:** "Invalid business_id"  
**Solution:** Use 1 (Print), 2 (Publishing), or 3 (Signs)

---

## Key Contacts

- **Outlook Issues:** Security/Compliance Team
- **Xero Issues:** Finance/Accounting Team  
- **Technical Issues:** Development Team

---

**Last Updated:** December 1, 2025  
**Status:** ✅ Production Ready
