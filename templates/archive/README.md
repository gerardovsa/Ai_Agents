# 📦 Archived Templates

This folder contains deprecated or replaced template files that are no longer actively used in the application.

## Archived Files

### `login.html.archived` (October 28, 2025)
**Original File:** `templates/login.html` (845 lines)  
**Reason:** Replaced by embedded login in `UI/business-ai-platform-v2.html`

**Why Archived:**
- The application now uses a single-page architecture with embedded authentication
- The new login UI in `business-ai-platform-v2.html` provides:
  - Better user experience (no page reload)
  - OAuth integration (Microsoft 365, Google)
  - Modern dark theme design
  - Improved animations and interactions
  - Consistent styling with the main dashboard

**Original Route:** `@app.route('/login')` in `app.py`  
**New Implementation:** Embedded overlay in business-ai-platform-v2.html (lines 3265-3307)

**Migration Notes:**
- All authentication flows now use the embedded login UI
- OAuth callbacks redirect to the business platform page
- JWT tokens are stored in localStorage
- User sessions managed by Flask backend

**If you need to restore this file:**
1. Rename `login.html.archived` back to `login.html`
2. Move to `templates/` directory
3. Ensure Flask route in `app.py` is active
4. Update authentication flows to use this template

---

**Archived by:** GitHub Copilot  
**Date:** October 28, 2025  
**Project:** Business AI Platform V2
