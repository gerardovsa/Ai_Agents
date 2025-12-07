# Xero & InHousePrint Universal Search Integration
**Date:** December 7, 2025  
**Status:** ✅ COMPLETE - Ready for Testing  
**Integration Type:** Multi-Business Accounting + Print Production Database Search

---

## 🎯 Overview

Added **Xero Accounting** and **InHousePrint SQL Server Database** as searchable sources in the Universal Search system. Users can now search across:

### Xero (3 Businesses)
- **InHouse Print** - Invoice, contact, payment data
- **InHouse Publishing** - Invoice, contact, payment data  
- **InHouse Signs** - Invoice, contact, payment data

### InHousePrint Database
- **Publishing Projects** - Project names, descriptions, deadlines
- **Clients** - Company names, contacts, emails
- **Products** - (schema supports, not yet searched)

---

## 📁 Files Modified

### 1. Backend: `AI_infrastructure/routes/universal_search_routes.py`

**Lines Changed:**
- **Line 167-169:** Added `include_xero` and `include_inhouseprint` parameters
- **Lines 560-717:** Added Sections 6 & 7 for Xero and InHousePrint search

**Section 6: SEARCH XERO (Accounting Data)**
```python
if include_xero:
    # Import Xero client
    from UI.modules_external.xero.xero_routes import XeroAPIClient
    
    # Search across 3 businesses
    for business_id in [1, 2, 3]:
        xero_client = XeroAPIClient(business_id=business_id, user_id=user_id)
        
        # Search invoices
        invoices = xero_client.make_request('GET', 'Invoices', 
            params={'where': f'Contact.Name.Contains("{query}") OR InvoiceNumber.Contains("{query}")'})
        
        # Search contacts
        contacts = xero_client.make_request('GET', 'Contacts',
            params={'where': f'Name.Contains("{query}") OR EmailAddress.Contains("{query}")'})
```

**Section 7: SEARCH INHOUSEPRINT (SQL Server)**
```python
if include_inhouseprint:
    # Connect to SQL Server
    inhouse_conn = pymssql.connect(
        server='3.25.76.138', port=1433,
        user='sa', password='Jack2011',
        database='InHousePrint', timeout=10
    )
    
    # Search PublishingProject table
    SELECT TOP 20 ... FROM PublishingProject p
    LEFT JOIN Clients c ON p.ClientID = c.ID
    WHERE p.ProjectName LIKE %query% OR c.CompanyName LIKE %query%
    
    # Search Clients table  
    SELECT TOP 20 ... FROM Clients
    WHERE CompanyName LIKE %query% OR ContactName LIKE %query%
```

### 2. Frontend: `UI/modules_internal/universal-search/universal-search.js`

**Lines Changed:**
- **Line 349-350:** Added Xero and InHousePrint checkboxes
- **Lines 606-607:** Added icon mappings (`fa-file-invoice`, `fa-print`)
- **Lines 616-617:** Added label mappings

**Checkbox Addition:**
```javascript
{ id: 'xero', label: 'Xero Accounting', icon: 'fa-file-invoice' },
{ id: 'inhouseprint', label: 'InHousePrint Projects', icon: 'fa-print' }
```

**Icon & Label Mappings:**
```javascript
getSourceIcon(source) {
    const icons = {
        xero: 'fas fa-file-invoice',
        inhouseprint: 'fas fa-print'
    };
}

getSourceLabel(source) {
    const labels = {
        xero: 'Xero Accounting',
        inhouseprint: 'InHousePrint Projects'
    };
}
```

---

## 🔌 Integration Details

### Xero Integration

**Existing Backend:** `UI/modules_external/xero/xero_routes.py`
- OAuth2 Client Credentials flow
- 3 business configurations (Print, Publishing, Signs)
- Full API client with `XeroAPIClient` class

**Search Capabilities:**
1. **Invoices**
   - Search by contact name or invoice number
   - Returns: invoice_number, contact, total, date, status, due_date
   - Top 5 results per business (15 total max)

2. **Contacts**
   - Search by name or email
   - Returns: name, email, phone, is_customer, is_supplier
   - Top 5 results per business (15 total max)

**API Endpoints Used:**
- `GET /api.xro/2.0/Invoices?where=Contact.Name.Contains("query")`
- `GET /api.xro/2.0/Contacts?where=Name.Contains("query")`

### InHousePrint Integration

**Existing Backend:** `AI_infrastructure/routes/inhouse_kanban_routes.py`
- SQL Server connection (pymssql)
- Database: InHousePrint at 3.25.76.138:1433

**Search Capabilities:**
1. **Publishing Projects**
   - Search by project name, description, client name
   - Returns: project_name, description, client, contact, email, start_date, deadline, status
   - Top 20 results

2. **Clients**
   - Search by company name, contact name, email
   - Returns: company, contact, email, phone, address
   - Top 20 results

**Database Schema:**
```sql
PublishingProject (ID, ProjectName, Description, StartDate, DeadlineDate, Status, ClientID)
Clients (ID, CompanyName, ContactName, Email, Phone, Address, Customer_XEROID)
```

**Note:** `Customer_XEROID` links to Xero contacts for cross-referencing.

---

## 🎨 User Interface

### Source Selection Panel
```
☐ Documents
☐ Vector Database (AI Search)
☐ Threads
☐ Messages
☐ Synergy Sessions
☐ Automations
☐ Gmail
☐ Slack
☑ Xero Accounting          ← NEW
☑ InHousePrint Projects    ← NEW
```

### Search Result Display

**Xero Invoice Result:**
```
📄 Invoice INV-2025-001
   Business: InHouse Print
   Contact: Microsoft Corporation
   Total: $15,450.00
   Status: PAID
   Due Date: 2025-01-15
```

**Xero Contact Result:**
```
👤 Microsoft Corporation
   Business: InHouse Publishing
   Email: accounts@microsoft.com
   Phone: +61 2 1234 5678
   Type: Customer
```

**InHousePrint Project Result:**
```
📋 Annual Report 2025 - Microsoft
   Client: Microsoft Corporation
   Contact: John Smith (john.smith@microsoft.com)
   Start Date: 2025-01-01
   Deadline: 2025-03-31
   Status: In Progress
```

**InHousePrint Client Result:**
```
🏢 Microsoft Corporation
   Contact: John Smith
   Email: john.smith@microsoft.com
   Phone: +61 2 1234 5678
   Address: 123 Tech Street, Sydney NSW 2000
```

---

## 🚀 How to Use

### 1. Enable Sources
In Universal Search module, check:
- ☑ Xero Accounting
- ☑ InHousePrint Projects

### 2. Search Queries

**Find invoice:**
```
Query: "invoice Microsoft"
Results:
  ✅ Xero: 3 invoices across 3 businesses
  ✅ InHousePrint: Project for Microsoft client
```

**Find client:**
```
Query: "john smith"
Results:
  ✅ Xero: Contact details in all businesses
  ✅ InHousePrint: Client record with projects
```

**Find project:**
```
Query: "annual report"
Results:
  ✅ InHousePrint: All publishing projects matching "annual report"
```

### 3. Filter Results
- Click source badges to filter
- Sort by date, relevance, or business
- Group by source type

---

## 🔐 Authentication & Credentials

### Xero Credentials
**Stored in:** `ai_infrastructure.user_platform_credentials`

**Platform names:**
- `xero_print` - InHouse Print credentials
- `xero_pub` - InHouse Publishing credentials
- `xero_signs` - InHouse Signs credentials

**Credential format:**
```json
{
  "client_id": "YOUR_XERO_CLIENT_ID",
  "client_secret": "YOUR_XERO_CLIENT_SECRET"
}
```

**Fallback:** Environment variables
- `XERO_PRINT_CLIENT_ID` / `XERO_PRINT_CLIENT_SECRET`
- `XERO_PUB_CLIENT_ID` / `XERO_PUB_CLIENT_SECRET`
- `XERO_SIGNS_CLIENT_ID` / `XERO_SIGNS_CLIENT_SECRET`

### InHousePrint Credentials
**Connection:** Hardcoded in `universal_search_routes.py`

```python
server='3.25.76.138'
port=1433
user='sa'
password='Jack2011'
database='InHousePrint'
```

**Security Note:** Consider moving to credential store for production.

---

## ✅ Testing Checklist

### Backend Tests
- [ ] Xero search returns invoices across 3 businesses
- [ ] Xero search returns contacts across 3 businesses
- [ ] InHousePrint search returns projects
- [ ] InHousePrint search returns clients
- [ ] Error handling for missing Xero credentials
- [ ] Error handling for InHousePrint connection failure
- [ ] Results limited to 5 per business (Xero) and 20 total (InHousePrint)

### Frontend Tests
- [ ] Xero checkbox appears in source panel
- [ ] InHousePrint checkbox appears in source panel
- [ ] Icons display correctly (fa-file-invoice, fa-print)
- [ ] Results grouped by source
- [ ] Result cards show all fields correctly
- [ ] Click on result opens details

### Integration Tests
- [ ] Search "microsoft" returns both Xero and InHousePrint results
- [ ] Cross-reference works (Customer_XEROID links Xero contacts)
- [ ] Performance acceptable with all sources enabled
- [ ] No duplicate results between sources

---

## 🐛 Known Issues & Limitations

### Xero
1. **OAuth Scope:** Uses Client Credentials flow, not user OAuth
   - All users see same business data
   - No user-specific filtering

2. **Rate Limits:** Xero API has rate limits (60 calls/minute)
   - Consider caching search results
   - Implement request throttling

3. **Tenant Selection:** Uses first tenant only
   - Multi-tenant organizations may have issues

### InHousePrint
1. **Hardcoded Credentials:** Database credentials in code
   - Move to credential store for security
   - Use environment variables or Azure Key Vault

2. **SQL Server Dependency:** Requires pymssql package
   - Ensure `pymssql` installed in production

3. **Limited Search Fields:** Only searches text fields
   - Doesn't search numeric IDs, dates, or status codes
   - Consider full-text indexing for better search

4. **Customer_XEROID Linkage:** Not yet used for cross-referencing
   - Future: Link InHousePrint clients to Xero contacts automatically

---

## 🔄 Future Enhancements

### Short Term
1. **Add more Xero endpoints:**
   - Payments (`/Payments`)
   - Bank Transactions (`/BankTransactions`)
   - Accounts (`/Accounts`)
   - Reports (`/Reports/*`)

2. **Add InHousePrint Products:**
   - Search Products table
   - Link products to projects

3. **Cross-reference results:**
   - Use `Customer_XEROID` to link Xero contacts to InHousePrint clients
   - Show combined view: "Client X has 3 invoices and 5 projects"

### Long Term
1. **Real-time sync:**
   - Webhook integration for Xero updates
   - Database triggers for InHousePrint changes

2. **Advanced search:**
   - Date range filtering
   - Amount range filtering (invoices)
   - Status filtering (projects)

3. **Analytics:**
   - Revenue by client (Xero)
   - Project completion rates (InHousePrint)
   - Client engagement metrics

4. **Export:**
   - Export search results to CSV/Excel
   - Generate reports from search results

---

## 📚 Related Documentation

- **Universal Search Architecture:** `UNIVERSAL_SEARCH_ARCHITECTURE_ANALYSIS.md`
- **Xero API Documentation:** `UI/modules_external/xero/xero_routes.py`
- **InHousePrint Kanban:** `AI_infrastructure/routes/inhouse_kanban_routes.py`
- **Xero Developer Portal:** https://developer.xero.com/documentation/api/api-overview
- **Xero API Reference:** https://developer.xero.com/documentation/api/accounting/overview

---

## 🎯 Success Criteria

✅ **Integration Complete** when:
1. Xero search returns results from all 3 businesses
2. InHousePrint search returns projects and clients
3. UI displays both sources with correct icons/labels
4. Results grouped and formatted correctly
5. Error handling works for missing credentials
6. Performance acceptable (<2 seconds for combined search)

---

## 📞 Support & Troubleshooting

### Xero Not Returning Results
1. Check credentials in database: `SELECT * FROM ai_infrastructure.user_platform_credentials WHERE platform IN ('xero_print', 'xero_pub', 'xero_signs')`
2. Check environment variables: `echo $XERO_PRINT_CLIENT_ID`
3. Test Xero API directly: `/api/xero/dashboard`
4. Check Xero Developer Portal for API status

### InHousePrint Connection Failed
1. Test SQL Server connection: `telnet 3.25.76.138 1433`
2. Check pymssql installed: `pip list | grep pymssql`
3. Check database credentials: `sa` / `Jack2011`
4. Check firewall rules for port 1433

### Search Too Slow
1. Enable caching for Xero results
2. Add database indexes for InHousePrint full-text search
3. Limit concurrent searches (search in sequence, not parallel)
4. Reduce result limits (currently 5 per business for Xero, 20 for InHousePrint)

---

**END OF DOCUMENTATION**
