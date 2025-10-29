# 📊 Business AI Platform - Tab Structure Reference

**Visual guide to all platform tabs and their data sources**

---

## 🗂️ Tab Navigation Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                       BUSINESS AI PLATFORM                          │
│                                                                     │
│  [🏠 Home] [💬 Comm] [💰 Sales] [📊 Analytics] [📄 Docs]          │
│  [📦 Stock] [🎙️ Transcripts] [📅 Schedule] [🤖 Automation]        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ 🏠 **Home Dashboard**

### **Purpose**: Executive overview of all business metrics

### **Content Sections**:
- **Stats Grid** (4 metrics)
  - Messages Sent (Slack, Gmail, Twilio)
  - Total Revenue (WooCommerce, Stripe, PayPal)
  - Documents Processed (Google Docs/Drive, CloudConvert)
  - AI Tool Executions (Tool Registry)

- **Platform Status Grid**
  - Shows 19 platforms with connection status
  - Real-time health checks
  - Quick reconnect actions

- **Recent Activity Feed**
  - Cross-platform event timeline
  - AI actions log
  - System notifications

### **Data Sources**:
```javascript
GET /api/v1/platforms/status
GET /api/v1/dashboard/stats
GET /api/v1/activity/recent
```

### **Visualizations**:
- None (pure dashboard)

---

## 2️⃣ 💬 **Communication Hub**

### **Purpose**: Unified messaging across Slack, Gmail, Twilio

### **Platform Tools**:
| Platform | Tools | Use Cases |
|----------|-------|-----------|
| **Slack** | 8 tools | Send messages, manage channels, get threads |
| **Gmail** | 6 tools | Send/read emails, manage labels |
| **Twilio** | 5 tools | SMS, voice calls, number management |

### **Content Sections**:
1. **Platform Selector** (tabs for Slack/Gmail/Twilio)
2. **Send Message Form**
   - Recipient/channel selector
   - Message composer with AI suggestions
   - Attachment support
3. **Message History Table** (Tabulator)
   - Columns: Platform, Recipient, Message Preview, Timestamp, Status
   - Filters: Platform, Date Range, Status
   - Actions: View full message, Resend, Delete
4. **Analytics Panel**
   - Message volume by platform (line chart)
   - Response time averages (bar chart)
   - Success/failure rates (pie chart)

### **Data Sources**:
```javascript
POST /api/v1/tools/execute
  - slack_send_message
  - gmail_send_email
  - twilio_send_sms

GET /api/v1/communication/history
GET /api/v1/communication/analytics
```

### **Visualizations**:
- **Chart.js Line**: Message volume over time (last 30 days)
- **Chart.js Bar**: Platform comparison (messages sent per platform)
- **Chart.js Pie**: Message status distribution (sent, failed, pending)

### **UI Components** (from existing UIs):
- Tabulator table with dark theme (from stock_management)
- Message composer with AI assist (new)
- Platform status indicators (from transcript_processor)

---

## 3️⃣ 💰 **Sales & E-Commerce**

### **Purpose**: Order management and revenue analytics

### **Platform Tools**:
| Platform | Tools | Use Cases |
|----------|-------|-----------|
| **WooCommerce** | 12 tools | Orders, products, customers, inventory |
| **Stripe** | 10 tools | Payments, refunds, subscriptions |
| **PayPal** | 8 tools | Transactions, invoices, disputes |

### **Content Sections**:
1. **Revenue Stats Grid** (4 cards)
   - Today's Revenue
   - Orders Count
   - Average Order Value
   - Top Product

2. **Orders Table** (Tabulator)
   - Columns: Order ID, Customer, Products, Total, Status, Date
   - Filters: Status, Date Range, Payment Method
   - Actions: View Details, Refund, Email Customer
   - Row Tagging: Green (fulfilled), Orange (pending), Red (issue)

3. **Product Performance**
   - Best sellers list
   - Low stock alerts
   - Category breakdown (sunburst chart)

4. **Revenue Trends Chart**
   - Daily/Weekly/Monthly toggle
   - Comparison to previous period
   - Goal line overlay

### **Data Sources**:
```javascript
POST /api/v1/tools/execute
  - woocommerce_list_orders
  - stripe_list_payments
  - paypal_get_transactions

GET /api/v1/sales/stats
GET /api/v1/sales/trends
GET /api/v1/products/performance
```

### **Visualizations**:
- **Chart.js Line**: Revenue trends (daily/weekly/monthly)
- **Plotly Sunburst**: Product category hierarchy
- **Chart.js Doughnut**: Payment method distribution
- **Chart.js Bar**: Top 10 products by revenue

### **UI Components**:
- Row tagging system (from stock_management)
- Bulk actions (refund multiple orders)
- Cell popup viewer for order details

---

## 4️⃣ 📊 **Analytics & Reports**

### **Purpose**: Custom data queries and visualization builder

### **Platform Tools**:
| Platform | Tools | Use Cases |
|----------|-------|-----------|
| **Supabase** | 8 tools | SQL queries, table management |
| **Google Sheets** | 12 tools | Read/write data, chart creation |
| **Google Analytics** | 6 tools | Website metrics, conversions |

### **Content Sections**:
1. **Query Builder**
   - SQL editor with syntax highlighting (Prism.js)
   - Table browser (left sidebar)
   - Saved queries library
   - AI query generator

2. **Results Table** (Tabulator)
   - Auto-columns based on query results
   - Export to CSV/Excel/PDF
   - Column hiding/reordering
   - Inline filtering

3. **Auto-Visualization**
   - AI-detected chart type based on data structure
   - Chart type selector (line, bar, pie, scatter, heatmap)
   - Interactive legends
   - Export to PNG/SVG

4. **Report Generator**
   - Schedule reports (daily/weekly/monthly)
   - Email distribution list
   - Template library

### **Data Sources**:
```javascript
POST /api/v1/tools/execute
  - supabase_execute_query
  - gsheets_read_range
  - google_analytics_get_report

GET /api/v1/analytics/saved_queries
POST /api/v1/analytics/generate_report
```

### **Visualizations**:
- **Dynamic**: Based on query results
  - Time series → Line chart
  - Categories → Bar chart
  - Hierarchical → Sunburst
  - Correlation → Scatter plot

### **UI Components**:
- SQL editor (from stock_management SQL tab)
- Tabulator with auto-columns
- Chart type selector with live preview

---

## 5️⃣ 📄 **Document Management**

### **Purpose**: File operations across Google Drive, Docs, CloudConvert

### **Platform Tools**:
| Platform | Tools | Use Cases |
|----------|-------|-----------|
| **Google Drive** | 10 tools | List, upload, download, share files |
| **Google Docs** | 8 tools | Create, edit, export documents |
| **CloudConvert** | 6 tools | Format conversion (PDF, DOCX, etc) |

### **Content Sections**:
1. **File Browser**
   - Tree view of folders (left panel)
   - File grid with thumbnails (main panel)
   - Breadcrumb navigation

2. **File Operations Panel**
   - Upload (drag & drop)
   - Convert format (CloudConvert integration)
   - Generate document from template (AI-powered)
   - Share settings

3. **Recent Files Table**
   - Columns: Name, Type, Modified Date, Owner, Size
   - Quick actions: Preview, Download, Share, Delete

4. **File Type Analytics**
   - Pie chart: Storage by file type
   - Bar chart: Most accessed files

### **Data Sources**:
```javascript
POST /api/v1/tools/execute
  - google_drive_list_files
  - google_docs_create_document
  - cloudconvert_convert_file

GET /api/v1/documents/recent
GET /api/v1/documents/analytics
```

### **Visualizations**:
- **Chart.js Pie**: Storage distribution by file type
- **Chart.js Bar**: Most accessed files (last 30 days)

---

## 6️⃣ 📦 **Stock Management** *(Migrated from existing UI)*

### **Purpose**: Print shop inventory and job analytics

### **Data Sources**:
- SQLite database (local)
- AI-extracted job ticket data

### **Content Sections**:
1. **Stock Master Table** (Tabulator - 15+ columns)
2. **Industry/Geographic Analysis** (Plotly sunburst)
3. **Consumption Trends** (Chart.js line charts)
4. **SQL Query Builder** (custom editor)
5. **Report Generator** (text-based reports)

### **Migration Notes**:
```javascript
// Components to migrate:
- Dark theme Tabulator CSS overrides
- Row tagging system (localStorage-based)
- Cell popup viewer (draggable modal)
- Sunburst chart for industry breakdown
- Hamburger menu with thread saving
```

---

## 7️⃣ 🎙️ **Transcript Processing** *(Migrated from existing UI)*

### **Purpose**: Meeting transcript import and AI processing

### **Data Sources**:
- Google Sheets API
- CSV uploads
- Manual paste
- Backend processing queue (SSE streaming)

### **Content Sections**:
1. **Import Tab** (multi-source)
2. **Processing Queue** (SSE-streamed logs)
3. **Backend Monitor** (real-time status)
4. **Distribution Queue** (email/Slack delivery)
5. **Database Viewer** (processed transcripts)

### **Migration Notes**:
```javascript
// Components to migrate:
- Multi-source import forms
- SSE connection for real-time logs
- Processing queue Tabulator table
- Distribution status tracking
- Custom SQL editor (Prism.js)
```

---

## 8️⃣ 📅 **Scheduling & Forms**

### **Purpose**: Calendar management and form response collection

### **Platform Tools**:
| Platform | Tools | Use Cases |
|----------|-------|-----------|
| **Google Calendar** | 8 tools | Events, availability, reminders |
| **Google Forms** | 6 tools | Create forms, collect responses |

### **Content Sections**:
1. **Calendar View**
   - Month/Week/Day toggle
   - Event creation modal
   - Drag-to-reschedule

2. **Upcoming Events Table**
   - Next 7 days
   - Quick actions: Join (if virtual), Reschedule, Cancel

3. **Forms Manager**
   - List of forms
   - Response count
   - Latest responses table

4. **Analytics**
   - Event density heatmap (by day/hour)
   - Form response trends

### **Data Sources**:
```javascript
POST /api/v1/tools/execute
  - google_calendar_list_events
  - google_calendar_create_event
  - google_forms_get_responses
```

### **Visualizations**:
- **Heatmap**: Event density by day/time (Plotly)
- **Chart.js Line**: Form responses over time

---

## 9️⃣ 🤖 **Automation Workflows**

### **Purpose**: Visual workflow builder connecting all platforms

### **Content Sections**:
1. **Workflow Canvas**
   - Drag-and-drop nodes
   - Mermaid.js diagram rendering
   - Trigger → Actions → Conditions

2. **Trigger Types**
   - Webhook (external API call)
   - Schedule (cron expression)
   - Platform event (new order, new email, etc)
   - Manual execution

3. **Action Library**
   - All 114 tools available as actions
   - Parameter mapping UI
   - Variable substitution ({{order_id}}, {{customer_name}})

4. **Active Workflows Table**
   - Name, Trigger, Last Run, Status, Actions
   - Toggle on/off
   - Execution history

### **Example Workflow**:
```javascript
{
  name: "New Order Notification",
  trigger: {
    type: "woocommerce_new_order",
    platform: "woocommerce"
  },
  actions: [
    {
      tool: "slack_send_message",
      params: {
        channel: "#sales",
        text: "🎉 New order #{{order_id}} - ${{order_total}}"
      }
    },
    {
      tool: "gsheets_append_row",
      params: {
        spreadsheet: "Sales Log",
        values: ["{{order_id}}", "{{customer_name}}", "{{order_total}}"]
      }
    }
  ]
}
```

### **Data Sources**:
```javascript
GET /api/v1/automation/workflows
POST /api/v1/automation/execute
GET /api/v1/automation/history
```

### **Visualizations**:
- **Mermaid.js Flowchart**: Workflow diagram
- **Chart.js Bar**: Execution success/failure rates
- **Timeline**: Workflow execution history

---

## 🎨 Component Reuse Matrix

| Component | Used In Tabs | Source UI |
|-----------|--------------|-----------|
| **Tabulator Dark Theme** | All data tables | stock_management |
| **Row Tagging (3 colors)** | Sales, Stock | stock_management |
| **Cell Popup Viewer** | All tables | stock_management |
| **Plotly Sunburst** | Sales, Stock | stock_management |
| **Chart.js Line Charts** | Comm, Sales, Analytics | stock_management |
| **SSE Streaming** | Transcripts, AI Chat | transcript_processor |
| **Multi-Source Import** | Transcripts, Documents | transcript_processor |
| **AI Chat Panel** | All tabs (context-aware) | New (unified) |
| **Notification System** | All tabs | New (unified) |
| **Theme Toggle** | All tabs | New (unified) |

---

## 📱 Responsive Behavior

### **Desktop (>1400px)**
- Full three-column layout
- AI chat always visible
- 2-3 charts side-by-side

### **Laptop (1024-1400px)**
- AI chat collapsible
- Single column charts
- Tables full width

### **Tablet (<1024px)**
- Sidebar hidden (hamburger menu)
- AI chat as drawer (overlay)
- Stacked layout

---

## 🚀 Development Order

### **Phase Priority**:
1. ✅ **Home Dashboard** (foundation)
2. ⏳ **Communication Hub** (simple CRUD operations)
3. ⏳ **Sales Dashboard** (complex visualizations)
4. ⏳ **Analytics Builder** (SQL editor + auto-viz)
5. ⏳ **Migrate Stock Management** (existing UI)
6. ⏳ **Migrate Transcripts** (existing UI)
7. ⏳ **Documents Tab** (file operations)
8. ⏳ **Scheduling Tab** (calendar integration)
9. ⏳ **Automation Workflows** (most complex)

---

**This structure ensures each tab serves a distinct business function while sharing common UI components!** 🎯
