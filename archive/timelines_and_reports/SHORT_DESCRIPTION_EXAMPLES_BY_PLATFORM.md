# Short Description Examples by Platform Type

**Reference Guide** for writing platform-specific short descriptions  
**Created:** December 10, 2025

---

## 🎯 Format Template

```
[ACTION_VERB] [PRIMARY_OBJECT] [KEY_FEATURES/CRITERIA]
```

**Length:** 50-120 characters (8-18 words optimal)

---

## 📧 Email Platforms (Gmail, Outlook)

### Action Verbs
- Search, Send, Read, Create, Update, Delete, Archive, Label, Filter, Forward, Reply, Compose

### Examples

**GOOD:**
- `"Search Gmail inbox for emails by sender, subject, date, or keywords"`
- `"Send Outlook email with attachments, CC, BCC, and formatting"`
- `"Read Gmail message content with attachments and metadata"`
- `"Create draft email in Outlook with template and recipients"`
- `"Archive Gmail messages by label, date range, or search query"`

**BAD:**
- `"This tool searches emails"` (no platform, no specifics)
- `"GET /gmail/messages?q={query}"` (API terminology)
- `"gmail_search_messages"` (just repeating tool name)

---

## 📄 Document Platforms (Google Docs, Word)

### Action Verbs
- Create, Update, Format, Insert, Delete, Export, Share, Convert, Generate, Edit

### Examples

**GOOD:**
- `"Create Google Doc from markdown with formatting, images, and tables"`
- `"Update Word document with text, styles, headings, and layout"`
- `"Export Google Doc to PDF, HTML, or markdown format"`
- `"Insert image, table, or heading into Word document"`
- `"Format Google Doc text with bold, italic, colors, and alignment"`

**BAD:**
- `"Document creation tool"` (too vague)
- `"batchUpdate requests to Google Docs API"` (too technical)

---

## 📊 Spreadsheet Platforms (Google Sheets, Excel)

### Action Verbs
- Read, Write, Update, Calculate, Query, Format, Chart, Filter, Sort, Merge

### Examples

**GOOD:**
- `"Read Google Sheets data by range, sheet name, or query filter"`
- `"Write Excel data to specific cells, rows, or named ranges"`
- `"Calculate Google Sheets formulas with cell references and functions"`
- `"Format Excel cells with colors, borders, number formats, and styles"`
- `"Create chart in Google Sheets from data range with styling"`

**BAD:**
- `"Spreadsheet operations"` (no action, no platform)
- `"values().get() method wrapper"` (implementation detail)

---

## 💰 Calculator/Quoting Platforms

### Action Verbs
- Calculate, Quote, Price, Estimate, Generate, Compare

### Examples

**GOOD:**
- `"Calculate printing quote for flyers with sizing, stock, and finish options"`
- `"Calculate booklet quote with page count, binding, and paper specifications"`
- `"Calculate business card quote with dimensions, quantity, and cellophane"`
- `"Calculate banner quote with material, size, and finishing selections"`
- `"Generate pricing estimate for vinyl stickers with shape and quantity"`

**BAD:**
- `"Quote tool"` (too vague, no product type)
- `"Runs pricing calculation algorithm"` (technical, not user-focused)
- `"calculate_flyers function"` (code reference)

---

## 📅 Calendar Platforms (Google Calendar, Microsoft Calendar)

### Action Verbs
- Create, Update, Delete, List, Find, Schedule, Reschedule, Cancel, Invite

### Examples

**GOOD:**
- `"Create Google Calendar event with date, time, attendees, and location"`
- `"List Microsoft Calendar events by date range, calendar, or search query"`
- `"Update Google Calendar event time, title, or attendee list"`
- `"Find available meeting slots in Microsoft Calendar for multiple people"`
- `"Delete Google Calendar event by ID or search criteria"`

**BAD:**
- `"Calendar management"` (no specific action)
- `"POST /calendar/events endpoint"` (API reference)

---

## 💳 Payment Platforms (Stripe, PayPal)

### Action Verbs
- Create, Process, Refund, List, Retrieve, Update, Cancel, Charge, Transfer

### Examples

**GOOD:**
- `"Create Stripe payment intent with amount, currency, and customer info"`
- `"Process PayPal payment with card details and billing address"`
- `"Refund Stripe charge with amount and reason for customer"`
- `"List PayPal transactions by date range, status, or customer"`
- `"Retrieve Stripe customer payment methods and subscription details"`

**BAD:**
- `"Payment processing"` (no platform, no specifics)
- `"Stripe API integration"` (too vague)

---

## 🛒 E-commerce Platforms (WooCommerce, Shopify)

### Action Verbs
- Create, Update, List, Search, Delete, Manage, Process, Track, Inventory

### Examples

**GOOD:**
- `"Create WooCommerce product with title, price, images, and inventory"`
- `"List Shopify orders by date range, status, or customer name"`
- `"Update WooCommerce product stock quantity and availability status"`
- `"Search Shopify customers by email, name, or order history"`
- `"Process WooCommerce order with payment, shipping, and fulfillment"`

**BAD:**
- `"Product tool"` (no action, no platform)
- `"WP REST API wrapper"` (implementation detail)

---

## 🎨 Design Platforms (Adobe InDesign)

### Action Verbs
- Create, Design, Generate, Export, Merge, Template, Layout, Format, Place

### Examples

**GOOD:**
- `"Create InDesign document from template with page size and margins"`
- `"Merge CSV data into InDesign template with images and formatting"`
- `"Export InDesign document to PDF with bleed, crop marks, and quality"`
- `"Place images in InDesign layout with sizing and positioning"`
- `"Generate InDesign catalog from data with automatic page layout"`

**BAD:**
- `"Design automation"` (too vague)
- `"ExtendScript API call"` (technical implementation)

---

## 💬 Communication Platforms (Slack, Teams)

### Action Verbs
- Send, Post, Reply, React, Create, Update, List, Search, Notify

### Examples

**GOOD:**
- `"Send Slack message to channel or user with formatting and attachments"`
- `"Post Microsoft Teams message with mentions, cards, and reactions"`
- `"Create Slack channel with name, topic, and member invitations"`
- `"Search Teams messages by keyword, sender, or date range"`
- `"List Slack channels with member count and activity status"`

**BAD:**
- `"Messaging functionality"` (no platform, no action)
- `"Webhook POST request"` (technical implementation)

---

## 🗄️ Database Platforms (Supabase, SQL)

### Action Verbs
- Query, Insert, Update, Delete, Select, Join, Filter, Sort, Aggregate

### Examples

**GOOD:**
- `"Query Supabase table with filters, sorting, and pagination"`
- `"Insert SQL database record with validation and constraints"`
- `"Update Supabase row by ID with new values and timestamps"`
- `"Delete SQL database records matching search criteria"`
- `"Select Supabase data with joins, aggregations, and grouping"`

**BAD:**
- `"Database operation"` (no specific action)
- `"Execute SQL query"` (too generic)

---

## 📊 Analytics & Reporting Platforms

### Action Verbs
- Analyze, Report, Track, Measure, Visualize, Export, Monitor, Aggregate

### Examples

**GOOD:**
- `"Analyze Google Analytics traffic by source, date, and page views"`
- `"Generate Xero financial report with date range and account filters"`
- `"Track Stripe revenue metrics by product, period, and customer"`
- `"Export PayPal transaction report to CSV with filters and sorting"`
- `"Visualize sales data with charts, graphs, and trend analysis"`

**BAD:**
- `"Reporting tool"` (too vague)
- `"API data fetch"` (technical)

---

## 🤖 Automation & Workflow Platforms

### Action Verbs
- Automate, Trigger, Schedule, Execute, Monitor, Deploy, Coordinate

### Examples

**GOOD:**
- `"Automate workflow with triggers, actions, and conditional logic"`
- `"Schedule automation to run daily, weekly, or on custom schedule"`
- `"Execute multi-step automation with error handling and retries"`
- `"Monitor automation runs with logs, status, and notifications"`
- `"Deploy workflow across agents with coordination and dependencies"`

**BAD:**
- `"Workflow management"` (no specific action)
- `"Automation engine"` (too abstract)

---

## 🎓 Education & Course Platforms (Kajabi)

### Action Verbs
- Create, Enroll, Update, Publish, Manage, Track, Deliver, Generate

### Examples

**GOOD:**
- `"Create Kajabi course with lessons, modules, and pricing structure"`
- `"Enroll student in Kajabi course with access settings and notifications"`
- `"Publish Kajabi content to members with scheduling and drip release"`
- `"Track Kajabi student progress with completion and engagement metrics"`
- `"Generate Kajabi certificate for course completion with custom design"`

**BAD:**
- `"Course tool"` (no action, too vague)
- `"LMS integration"` (technical terminology)

---

## 📱 Social Media Platforms (Instagram)

### Action Verbs
- Post, Upload, Schedule, Update, Delete, Like, Comment, Follow, Analyze

### Examples

**GOOD:**
- `"Post Instagram image with caption, hashtags, and location tag"`
- `"Schedule Instagram story with stickers, polls, and expiration time"`
- `"Upload Instagram reel with music, effects, and cover image"`
- `"Analyze Instagram engagement metrics by post, date, and audience"`
- `"Update Instagram bio with text, links, and profile picture"`

**BAD:**
- `"Social media posting"` (no platform specified)
- `"Instagram API wrapper"` (implementation detail)

---

## 🔧 Infrastructure Platforms (Render, Cloudflare, Ngrok)

### Action Verbs
- Deploy, Configure, Monitor, Restart, Scale, Update, Backup, Restore

### Examples

**GOOD:**
- `"Deploy Render service from GitHub repo with build settings"`
- `"Configure Cloudflare DNS records with type, name, and value"`
- `"Monitor Render service logs, metrics, and health status"`
- `"Create Ngrok tunnel with port, domain, and authentication"`
- `"Scale Render service instances up or down based on load"`

**BAD:**
- `"Infrastructure management"` (too vague)
- `"API endpoint call"` (technical)

---

## 🧠 AI & Memory Platforms

### Action Verbs
- Remember, Recall, Search, Store, Retrieve, Index, Vectorize, Query

### Examples

**GOOD:**
- `"Search past conversations for relevant context by keyword or topic"`
- `"Store code snippet with tags, description, and project context"`
- `"Recall project history with timeline, decisions, and outcomes"`
- `"Retrieve user preferences, settings, and saved configurations"`
- `"Index document content for semantic search and retrieval"`

**BAD:**
- `"Memory storage"` (no specific action)
- `"Embedding generation"` (too technical)

---

## ✅ Universal Quality Checklist

Every short description MUST:

1. **Start with action verb** (not "This tool", "A tool for", etc.)
2. **Include platform name** (Gmail, Stripe, InDesign, etc.)
3. **Specify key capabilities** (with what, by what, using what)
4. **Use natural language** (how users think, not code)
5. **Be 50-120 characters** (8-18 words)
6. **Contain relevant keywords** (for semantic clustering)
7. **Match user intent** (what they'd search for)

---

## 🚫 Common Mistakes to Avoid

❌ "This tool is used to..."  
❌ "A comprehensive solution for..."  
❌ "API endpoint that handles..."  
❌ "Function to perform..."  
❌ Generic verbs without platform (just "Send email" vs "Send Gmail email")  
❌ Code/API terminology (GET, POST, REST, endpoint)  
❌ Implementation details (wrapper, integration, handler)  
❌ Too short (<50 chars) or too long (>120 chars)  
❌ Repeating the tool name exactly  
❌ No mention of platform/domain

---

## 🎯 Testing Your Description

Ask yourself:

1. **Can a user find this tool by searching the description?**
2. **Does it clearly explain what the tool does?**
3. **Is it different from similar tools on the same platform?**
4. **Would you understand it without reading the full description?**
5. **Does it contain domain keywords for semantic clustering?**

If you answer "no" to any question, revise the description.

---

**Use this guide as reference while processing each platform's tools!**
