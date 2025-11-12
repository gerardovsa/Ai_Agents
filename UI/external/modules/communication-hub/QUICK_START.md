# Communication Hub - Quick Start Guide

**Get started with the unified inbox and AI integration in 5 minutes!**

---

## 🚀 Quick Setup

### 1. Connect Your Email Accounts

**Before using Communication Hub, you need to connect at least one email account:**

#### Gmail:
1. Click **Settings** icon (bottom of sidebar)
2. Navigate to **Account Linking**
3. Click **Connect Gmail**
4. Authorize access in Google OAuth popup
5. ✅ Gmail connected!

#### Outlook:
1. Click **Settings** icon (bottom of sidebar)
2. Navigate to **Account Linking**
3. Click **Connect Outlook**
4. Authorize access in Microsoft OAuth popup
5. ✅ Outlook connected!

### 2. Open Communication Hub

1. Find the **chat bubble icon** 💬 in the left sidebar
2. Click it to open Communication Hub
3. Your unified inbox loads automatically!

---

## 📧 Basic Email Operations

### View Emails
- **All emails** from Gmail and Outlook appear in one table
- **Filter by account** using the dropdown (top left)
- **Click any email** to open preview panel (right side)
- **Scroll** to load more emails

### Send Email
1. Click **"Compose"** tab at top
2. Select **"From" account** (Gmail or Outlook)
3. Enter **recipient**, **subject**, and **message**
4. Click **"Send Email"** button
5. Email sent! 📤

### Search Emails
1. Click **"Search"** tab at top
2. Type your **search query**
3. Press **Enter** or click **Search** button
4. Results appear instantly from all accounts

---

## 🤖 AI Integration - 3 Methods

### Method 1: Drag-and-Drop ⭐ (RECOMMENDED)

**Fastest way to analyze emails with AI!**

1. **Click and hold** on any email row in the table
2. **Drag** the email toward the left sidebar
3. **Drop** into the AI chat panel (left side of screen)
4. **AI receives** the email automatically and starts analysis!

**What gets sent to AI:**
```
📧 Email Analysis Request

From: john@example.com
To: you@company.com
Subject: Q4 Budget Review
Date: Nov 10, 2025 2:30 PM

Email Body:
[Full email content]

Please analyze this email and provide:
1. Summary of key points
2. Suggested actions
3. Important dates or deadlines
4. Any concerns or flags
```

**Visual Feedback:**
- Purple badge appears while dragging
- Shows email subject as you drag
- Drop zone highlights when you hover over AI sidebar

---

### Method 2: Right-Click Menu

**Send to specific AI agent!**

1. **Right-click** on any email row
2. Menu appears with options:
   - 🤖 **Send to AI Prime** (instant AI analysis)
   - 👥 **Send to Agent...** (choose specific agent)
   - ↩️ Reply
   - ➡️ Forward
   - 👁️ Mark as Read/Unread
   - 🗑️ Delete

3. Click **"Send to AI Prime"** for instant analysis
4. OR click **"Send to Agent..."** to choose from:
   - AI Prime
   - Data Agent
   - Email Agent
   - Research Agent
   - Writing Agent

5. Email appears in AI chat with formatted analysis request

---

### Method 3: Quick Action Button

**One-click AI analysis from the table!**

1. Find the **robot icon** 🤖 in the "Actions" column
2. Click it
3. Email instantly sent to AI Prime for analysis

---

### Method 4: Bulk Selection (Multiple Emails)

**Analyze multiple emails at once!**

1. Click **"Select"** button in toolbar (top right)
2. **Checkboxes** appear in first column
3. **Check** multiple emails you want analyzed
4. Click **"Send to AI"** button (shows count: "Send 5 to AI")
5. AI receives all emails as a **batch analysis request**:

```
📧 Batch Email Analysis Request

Selected Emails: 5

Email 1:
- From: john@example.com
- Subject: Budget Approval
- Date: Nov 10, 2025
- Preview: Please review the Q4 budget...

Email 2:
- From: sarah@company.com
- Subject: Project Deadline
- Date: Nov 10, 2025
- Preview: The deadline has been moved to...

[... more emails ...]

Please analyze these emails and provide:
1. Common themes or topics
2. Priority order for responses
3. Suggested actions for each
4. Any important deadlines
```

6. Click **"Select"** again to exit selection mode

---

## 🎯 Pro Tips

### Keyboard Shortcuts
- **Enter** in search box = Search emails
- **Esc** = Close preview panel
- **Esc** = Close context menu

### Visual Indicators
- **Bold subject** = Unread email
- **Red badge** = Unread status
- **Green badge** = Read status
- **📧 icon** = Gmail
- **📬 icon** = Outlook

### Date Formatting
- **Today**: "2:30 PM"
- **Yesterday**: "Yesterday"
- **This week**: "Mon", "Tue", "Wed"
- **Older**: "Nov 10", "Oct 25"

### Email Preview Panel
- Opens on **right side** when you click email
- Shows **full email content** (HTML or plain text)
- Action buttons at bottom:
  - 🤖 Send to AI
  - ↩️ Reply
  - ➡️ Forward
  - 🗑️ Delete
- Click **X** to close panel

---

## 🔧 Troubleshooting

### "No emails found"
- **Check**: Are your accounts connected?
- **Fix**: Go to Settings → Account Linking → Connect Gmail/Outlook

### Drag-and-drop not working
- **Check**: Is the email row highlighted when you hover?
- **Fix**: Make sure AI chat panel is visible on the left

### "Failed to load emails"
- **Check**: Is the Flask server running? (BISTART)
- **Fix**: Restart server and refresh browser

### Context menu not appearing
- **Check**: Did you right-click on an email row?
- **Fix**: Make sure you're clicking inside the table, not on empty space

### AI not receiving emails
- **Check**: Is AI chat panel open?
- **Check**: Browser console for errors (F12)
- **Fix**: Verify `window.aiChat.addMessageToChat` exists

---

## 📊 Example Workflows

### Workflow 1: Morning Email Triage (5 minutes)
1. Open Communication Hub
2. Filter to "All Accounts"
3. Select mode ON
4. Check 10-15 unread emails
5. Send batch to AI Prime
6. AI provides priority ranking and action items
7. Work through emails in priority order

**Time saved:** 15-20 minutes vs manual review

---

### Workflow 2: Client Email Analysis
1. Search for client name ("Acme Corp")
2. Results show all emails from/about client
3. Drag 3-4 key emails to AI sidebar
4. AI analyzes email thread
5. AI suggests next steps and response
6. Use AI's suggested reply in Compose tab

**Time saved:** 30-45 minutes vs reading full thread

---

### Workflow 3: Quick Reply with AI Help
1. Click email to open preview
2. Click robot icon 🤖 "Send to AI"
3. AI analyzes email in sidebar
4. AI provides suggested reply
5. Copy AI's suggestion
6. Switch to Compose tab
7. Paste and customize reply
8. Send!

**Time saved:** 10-15 minutes vs drafting from scratch

---

### Workflow 4: Weekly Email Summary
1. Select mode ON
2. Check 20-30 emails from the week
3. Send batch to AI Prime with custom prompt:
   - "Summarize these emails by category"
   - "Highlight any urgent action items"
   - "Create weekly report"
4. AI generates comprehensive summary
5. Use summary for team standup or report

**Time saved:** 1-2 hours vs manual summarization

---

## 🎨 Customization

### Change Account Order
- Accounts are sorted alphabetically
- Most recently used account stays selected

### Filter by Provider
- Dropdown: "All Accounts", "Gmail", "Outlook"
- Selection persists across sessions

### Email Table Columns
- Current: Provider, From, Subject, Preview, Date, Status, Actions
- Fixed width columns for consistency
- Responsive layout adjusts to screen size

---

## 🚀 Advanced Features

### Email Threading (Coming Soon)
- Group related emails into conversations
- View full thread history
- Reply in context

### Scheduled Sending (Coming Soon)
- Compose email now
- Schedule for later delivery
- Perfect for time zone differences

### Email Templates (Coming Soon)
- Save common replies
- Insert with one click
- Customize before sending

### Slack Integration (Coming Soon)
- Add Slack messages to unified inbox
- Respond to Slack from Communication Hub
- Unified search across email + Slack

---

## 📱 Mobile Support

**Current status:** Desktop only (optimized for 1280px+ screens)

**Mobile features coming soon:**
- Responsive design for tablets
- Touch-friendly drag-and-drop
- Swipe gestures for actions

---

## 🆘 Need Help?

### Common Questions

**Q: Can I use multiple Gmail accounts?**  
A: Currently one Gmail and one Outlook account per user. Multi-account support coming soon.

**Q: Where are emails stored?**  
A: Emails are fetched in real-time from Gmail/Outlook APIs. Not stored locally.

**Q: Does AI have access to my emails?**  
A: Only emails you explicitly send to AI. No automatic background access.

**Q: Can I undo sending email to AI?**  
A: No, but you can clear the AI chat conversation.

**Q: Is my OAuth token secure?**  
A: Yes, tokens are encrypted and stored in database. Never sent to AI.

### Support Channels

- **Documentation**: `README.md` (comprehensive)
- **Backend Logs**: Check Flask console for errors
- **Browser Console**: Press F12 for JavaScript errors
- **API Testing**: Use curl/Postman to test endpoints

---

## 🎉 You're Ready!

**Congratulations! You now know how to:**
- ✅ View emails from multiple accounts
- ✅ Drag emails to AI for instant analysis
- ✅ Right-click to send to specific agents
- ✅ Bulk select for batch analysis
- ✅ Compose and send emails
- ✅ Search across all accounts

**Start using Communication Hub now and save hours every week!** 🚀

---

**Last Updated:** November 10, 2025  
**Version:** 1.0.0  
**Need more help?** Check `README.md` or `IMPLEMENTATION_CHECKLIST.md`
