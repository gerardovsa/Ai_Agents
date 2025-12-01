# Xero Accounting Module

Complete Xero integration for InHouse Print, Publishing, and Signs with UI, backend routes, and AI agent tools.

## Module Structure

```
xero/
├── manifest.json          # Module configuration
├── xero.js               # Frontend UI (900+ lines)
├── xero.css              # Styling
├── xero_routes.py        # Backend Flask routes (800+ lines)
└── README.md             # This file
```

## Features

### 🎯 Multi-Business Support
- InHouse Print (business_id: 1)
- InHouse Publishing (business_id: 2)
- InHouse Signs (business_id: 3)

### 📊 Dashboard Tab
- **Financial metrics**: Total revenue, outstanding, overdue amounts
- **Charts**: Revenue timeline, status distribution, top customers
- **Recent invoices table**: Quick overview of latest transactions

### 📄 Invoices Tab
- **List all invoices** with filtering by status
- **Search** by invoice number or contact name
- **Create new invoices** (modal interface)
- **View invoice details** with line items

### 👥 Contacts Tab
- **List customers and suppliers**
- **Search** by name or email
- **Create new contacts**
- **View contact details** and history

### 💰 Payments Tab
- **Track all payments** across invoices
- **Filter by invoice**
- **View payment status** and dates

### 📚 Chart of Accounts Tab
- **Browse** all account codes
- **Search** by code or name
- **View account types** and tax settings

### 📈 Reports Tab
- Financial reports (coming soon)

## Backend API Endpoints

All endpoints require `business_id` query parameter (1, 2, or 3):

### Dashboard
```
GET /api/xero/dashboard?business_id=1
```
Returns metrics, charts data, and stats.

### Invoices
```
GET  /api/xero/invoices?business_id=1&status=AUTHORISED
POST /api/xero/invoices
GET  /api/xero/invoices/<invoice_id>?business_id=1
```

### Contacts
```
GET  /api/xero/contacts?business_id=1&search=ABC
POST /api/xero/contacts
```

### Payments
```
GET /api/xero/payments?business_id=1&invoice_id=xyz
```

### Accounts
```
GET /api/xero/accounts?business_id=1
```

### Bank Transactions
```
GET /api/xero/bank-transactions?business_id=1&from_date=2025-01-01
```

## AI Agent Tools

7 tools registered with the AI agent via tool registry:

1. **xero_get_invoices** - Get invoices with filtering
2. **xero_get_invoice_by_id** - Get specific invoice
3. **xero_get_contacts** - Get contacts list
4. **xero_create_invoice** - Create new invoice
5. **xero_get_accounts** - Get chart of accounts
6. **xero_get_bank_transactions** - Get bank transactions
7. **xero_get_payments** - Get payment records

### Usage via CHAT:
```powershell
CHAT "Show me all invoices from InHouse Print"
CHAT "Get contacts for InHouse Publishing"
CHAT "What's the outstanding balance?"
CHAT "Create an invoice for customer ABC"
```

## Configuration

### Environment Variables (.env.master)

```bash
# InHouse Print
XERO_PRINT_CLIENT_ID=your_print_client_id
XERO_PRINT_CLIENT_SECRET=your_print_client_secret

# InHouse Publishing
XERO_PUB_CLIENT_ID=your_pub_client_id
XERO_PUB_CLIENT_SECRET=your_pub_client_secret

# InHouse Signs
XERO_SIGNS_CLIENT_ID=your_signs_client_id
XERO_SIGNS_CLIENT_SECRET=your_signs_client_secret
```

### OAuth2 Flow
- Uses **Client Credentials** grant type
- Automatic token caching with expiry handling
- Scopes: `accounting.transactions accounting.contacts accounting.settings`

## Installation

1. **Credentials are already in `.env.master`** ✅
2. **Install Python package**:
   ```powershell
   pip install requests python-dotenv
   ```

3. **Restart Flask server**:
   ```powershell
   BISTART
   ```

4. **Access UI**:
   - Open AI_agents platform
   - Click "Xero Accounting" module
   - Select business from dropdown
   - Navigate tabs

## Architecture

### Frontend → Backend → Xero API

```
┌─────────────────┐
│   xero.js (UI)  │ ← User interaction
└────────┬────────┘
         │ AJAX
         ↓
┌─────────────────┐
│ xero_routes.py  │ ← Flask endpoints
└────────┬────────┘
         │ OAuth2
         ↓
┌─────────────────┐
│   Xero API      │ ← Official Xero REST API
└─────────────────┘
```

### Key Components

**XeroAPIClient** (in xero_routes.py):
- Handles OAuth2 token management
- Makes authenticated requests
- Caches tokens to reduce API calls
- Error handling and retry logic

**XeroModule** (in xero.js):
- Extends BaseModule
- Tab-based navigation
- Plotly charts integration
- Tabulator tables
- Dark mode support

## Module Registration

Automatically registered in:
- **UI manifest**: `UI/external/modules/manifest.json`
- **Flask app**: `AI_infrastructure/flask_app.py`
- **Tool registry**: `tools/schemas/xero_tools.json`

## Development

### Adding New Features

1. **Add UI tab** in `manifest.json`
2. **Create render method** in `xero.js`
3. **Add backend endpoint** in `xero_routes.py`
4. **Update tool schema** in `tools/schemas/xero_tools.json` (if needed)

### Testing

```powershell
# Test backend endpoint
curl http://localhost:5001/api/xero/dashboard?business_id=1

# Test via AI
CHAT "Show Xero invoices"

# Test UI
# Open browser → Xero Accounting module
```

## Troubleshooting

**Module not loading?**
- Check Flask logs for errors
- Verify xero_routes.py is found
- Ensure .env.master has credentials

**API errors?**
- Check Xero credentials are valid
- Verify OAuth scopes are correct
- Check token expiry (auto-refreshes)

**UI issues?**
- Check browser console for errors
- Verify manifest.json is valid JSON
- Check module registration in manifest

## Future Enhancements

- [ ] Financial reports tab implementation
- [ ] Invoice PDF generation
- [ ] Bulk operations (batch invoice creation)
- [ ] Advanced filtering and date ranges
- [ ] Export to Excel/CSV
- [ ] Email invoice directly from UI
- [ ] Payment reconciliation automation
- [ ] Multi-currency support
- [ ] Custom report builder

## Credits

Created: January 28, 2025  
Author: InHouse Print Development Team  
Version: 1.0.0  
Status: Production Ready ✅
