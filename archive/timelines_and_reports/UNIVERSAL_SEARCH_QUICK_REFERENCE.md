# Universal Search - Quick Reference Card
**Updated:** December 8, 2025  
**Version:** 2.0 (Cloud Storage + Outlook)

---

## 🔍 13 Searchable Sources

### Internal Sources (Always Available)
1. **Documents** - Files in document library
2. **Threads** - Chat conversations
3. **Messages** - Individual chat messages
4. **Synergy Sessions** - Multi-agent sessions
5. **Vector Database** - AI-indexed documents

### External Sources (Requires OAuth)

**Google Services:**
6. **Gmail** - Email messages
7. **Google Drive** - Files and folders

**Microsoft Services:**
8. **Outlook** - Email messages
9. **OneDrive** - Personal cloud files
10. **SharePoint** - Team site documents

**Other Services:**
11. **Slack** - Workspace messages
12. **Xero** - Invoices & contacts (3 businesses)
13. **InHousePrint** - Print projects & clients

---

## ⚡ Quick Commands

### Search Everything
```
Query: "budget 2025"
→ Searches all enabled sources
→ Returns ~50 results in 2 seconds
```

### Search Specific Platform
```
Enable only: ☑ Google Drive
Query: "quarterly report"
→ Searches Drive only
→ Faster, more focused results
```

### Cross-Platform Search
```
Enable: ☑ Gmail ☑ Outlook
Query: "invoice from john"
→ Searches both email platforms
→ Unified results view
```

---

## 🔐 OAuth Setup (One-Time)

### Connect Google (Gmail + Drive)
```
1. Account Settings → Integrations
2. Click "Connect Google"
3. Authorize permissions
4. ✅ Gmail & Drive enabled
```

### Connect Microsoft (Outlook + OneDrive + SharePoint)
```
1. Account Settings → Integrations
2. Click "Connect Microsoft"
3. Authorize permissions
4. ✅ Outlook, OneDrive, SharePoint enabled
```

### Connect Other Services
```
Slack: Account Settings → Connect Slack
Xero: Pre-configured (3 businesses)
InHousePrint: Pre-configured (internal)
```

---

## 🎯 Search Tips

### Best Practices
- **Use quotes** for exact phrases: `"annual report 2025"`
- **Keep it simple** - single keywords work best
- **Enable multiple sources** for comprehensive results
- **Check connection status** (grayed checkboxes = not connected)

### Search Examples

**Find document by name:**
```
"project plan"
→ Finds: Project Plan.docx, project-plan.pdf, etc.
```

**Find email from person:**
```
"from:john budget"
→ Gmail/Outlook: Emails from John about budget
```

**Find files by content:**
```
"microsoft partnership agreement"
→ Google Drive/OneDrive: Files containing these words
```

**Find across all sources:**
```
"Q1 2025 budget"
→ Documents, Drive, OneDrive, SharePoint, Gmail, Outlook
→ Invoices in Xero, projects in InHousePrint
```

---

## 🚨 Troubleshooting

### Checkbox Grayed Out
**Problem:** Source checkbox is disabled  
**Solution:** Complete OAuth for that platform

### No Results
**Problem:** Search returns 0 results  
**Causes:**
- Typo in search query
- Platform has no matching data
- Credentials expired (re-authenticate)

### Search Slow
**Problem:** Taking >5 seconds  
**Solutions:**
- Disable SharePoint (searches 3 sites)
- Reduce number of enabled sources
- Check internet connection

### Error Messages

**"Google credentials not found"**
→ Connect Google in Account Settings

**"Microsoft credentials not found"**
→ Connect Microsoft in Account Settings

**"401 Unauthorized"**
→ Token expired, re-authenticate

**"429 Rate Limit"**
→ Too many searches, wait 1 minute

---

## 📊 Result Display

### Result Card Format

**File Result (Drive/OneDrive/SharePoint):**
```
📄 Budget 2025.xlsx
   Modified: 2 days ago
   Size: 44.6 KB
   Owner: John Smith
   [Open in Drive]
```

**Email Result (Gmail/Outlook):**
```
✉️ Budget Approval Request
   From: John Smith
   Received: Today at 8:30 AM
   Preview: Hi team, please review...
   📎 Has attachments
   [Open in Gmail]
```

**Xero Result (Invoice):**
```
💰 Invoice INV-2025-001
   Business: InHouse Print
   Contact: Microsoft Corporation
   Total: $15,450.00
   Status: PAID
   [View in Xero]
```

**InHousePrint Result (Project):**
```
📋 Annual Report - Microsoft
   Client: Microsoft Corporation
   Deadline: 2025-03-31
   Status: In Progress
   [Open Project]
```

---

## ⚙️ Advanced Features

### Filter by Source
After searching, click source badges to filter:
```
[📄 Documents (23)]  ← Click to show only documents
[☁️ Google Drive (12)]
[✉️ Outlook (8)]
```

### Sort Results
```
- By Date (newest first)
- By Relevance (best match first)
- By Source (group by platform)
```

### Pagination
```
- Initial: 10 results per source
- Load More: Click to see next 10
- Load All: See all results
```

---

## 📈 Performance Guide

### Expected Response Times
- **Internal sources:** <200ms
- **Google services:** 300-800ms
- **Microsoft services:** 400-1500ms
- **Total (all sources):** 1.5s - 4.0s

### Optimize Performance
1. **Enable only needed sources** (uncheck unused)
2. **Cache enabled** (repeated queries faster)
3. **Limit results** (default 10 per source)
4. **SharePoint last** (slowest source)

---

## 🔗 Quick Links

### Documentation
- Full Architecture: `UNIVERSAL_SEARCH_ARCHITECTURE_ANALYSIS.md`
- Xero/InHousePrint: `XERO_INHOUSEPRINT_SEARCH_INTEGRATION.md`
- Cloud Storage: `CLOUD_STORAGE_OUTLOOK_SEARCH_INTEGRATION.md`
- Complete Summary: `COMPLETE_UNIVERSAL_SEARCH_SUMMARY.md`

### API Endpoints
- Search: `POST /api/universal-search/search`
- Sources: `GET /api/universal-search/sources`
- Facets: `POST /api/universal-search/facets`

### OAuth Flows
- Google: `/api/google/auth`
- Microsoft: `/api/microsoft/auth`
- Slack: `/api/slack/auth`

---

## 🎓 Pro Tips

### Tip 1: Connect All Accounts First
Before using Universal Search, connect all your accounts:
- Google (Gmail + Drive)
- Microsoft (Outlook + OneDrive + SharePoint)
- Slack

### Tip 2: Use Natural Language
```
Instead of: "file:budget type:xlsx owner:john"
Just type: "john's budget spreadsheet"
→ System handles the complexity
```

### Tip 3: Check Sources Before Searching
Look at checkboxes - grayed out = not connected
Enable only sources you need for faster results

### Tip 4: Bookmark Common Searches
Universal Search saves search history
Re-run common searches with one click

### Tip 5: Cross-Reference Results
Same file in Drive and OneDrive?
Search shows both locations - choose your preference

---

## 🆘 Need Help?

### Quick Checks
1. ✅ Are checkboxes enabled (not grayed)?
2. ✅ Is internet connection stable?
3. ✅ Are credentials up-to-date (not expired)?
4. ✅ Is search query spelled correctly?

### Get Support
- Check browser console (F12) for errors
- Review documentation files (5 comprehensive guides)
- Contact system administrator
- File bug report with screenshot

---

## 🎉 Success Story

**Before Universal Search:**
```
Task: Find "budget 2025" document
Steps:
1. Open Google Drive → Search → 2 mins
2. Open OneDrive → Search → 2 mins
3. Check email (Gmail) → 3 mins
4. Check email (Outlook) → 3 mins
5. Ask colleague "Where's the budget?"
Total: 10+ minutes
```

**With Universal Search:**
```
Task: Find "budget 2025" document
Steps:
1. Type "budget 2025" in Universal Search
2. Hit Enter
Total: 3 seconds
Results: Found in Drive, OneDrive, Gmail, Outlook, Xero, SharePoint
```

**Time Saved: 99.5%** 🚀

---

**END OF QUICK REFERENCE**

Keep this card handy for fast lookups!
