# Xero Comprehensive Toolkit Analysis
## Complete Xero API Capabilities for AI Agent Integration

**Date:** November 13, 2025  
**Purpose:** Document ALL Xero API capabilities discovered from official SDKs for complete AI agent tool coverage

---

## Research Sources

- **xeroapi/xero-python** - Official Python SDK
- **xeroapi/xero-netstandard** - Official .NET SDK  
- **xeroapi/xero-node** - Official Node.js SDK
- **xeroapi/xero-ruby** - Official Ruby SDK

---

## Xero API Architecture Overview

Xero provides **9 distinct API sets** covering different business functions:

| API Set | Base URL | Description | Tools Found |
|---------|----------|-------------|-------------|
| **Accounting API** | `api.xero.com/api.xro/2.0` | Core accounting functions (invoices, contacts, accounts) | 200+ endpoints |
| **Assets API** | `api.xero.com/assets.xro/1.0` | Fixed asset management | 10 endpoints |
| **Files API** | `api.xero.com/files.xro/1.0` | Document storage and attachments | 15 endpoints |
| **Projects API** | `api.xero.com/projects.xro/2.0` | Time tracking and project profitability | 17 endpoints |
| **Payroll AU API** | `api.xero.com/payroll.xro/1.0` | Australian payroll | 30+ endpoints |
| **Payroll UK API** | `api.xero.com/payroll.xro/1.0` | UK payroll | 30+ endpoints |
| **Payroll NZ API** | `api.xero.com/payroll.xro/2.0` | New Zealand payroll | 30+ endpoints |
| **Finance API** | `api.xero.com/finance.xro/1.0` | Financial statements and reporting | 15 endpoints |
| **App Store API** | `api.xero.com/appstore/2.0` | Subscription and usage tracking | 4 endpoints |

**Total Discovered Endpoints:** ~350+ (across all API sets)

---

## Current Xero Implementation Status

### ✅ Currently Implemented (7 Tools)

```python
# From tools/schemas/xero_tools.json
1. xero_get_invoices           # Get invoices with filters
2. xero_get_invoice_by_id      # Get specific invoice
3. xero_create_invoice          # Create new invoice
4. xero_get_contacts            # Get contacts with filters
5. xero_get_contact_by_id      # Get specific contact
6. xero_create_contact          # Create new contact
7. xero_get_accounts            # Get chart of accounts
```

**Coverage:** ~2% of total Xero API capabilities

---

## Complete Xero API Capabilities by Category

### 1. ACCOUNTING API (Core Business Functions) - 200+ Endpoints

#### A. **Invoices & Sales** (Current: 3 tools | Available: 25+ endpoints)

**Currently Implemented:**
- ✅ `xero_get_invoices` - List invoices
- ✅ `xero_get_invoice_by_id` - Get single invoice
- ✅ `xero_create_invoice` - Create invoice

**Missing Capabilities:**
```python
# Invoice Operations
- update_invoice(invoice_id, invoice_data)               # Modify existing invoice
- delete_invoice(invoice_id)                             # Delete draft invoice
- void_invoice(invoice_id)                               # Void approved invoice
- email_invoice(invoice_id, email_settings)              # Send invoice via email

# Invoice Attachments
- create_invoice_attachment(invoice_id, file, filename)  # Upload file to invoice
- get_invoice_attachments(invoice_id)                    # List invoice attachments
- get_invoice_attachment_by_id(invoice_id, attachment_id)
- get_invoice_attachment_content(invoice_id, attachment_id)
- delete_invoice_attachment(invoice_id, filename)

# Invoice History & Status
- get_invoice_history(invoice_id)                        # Get invoice history/notes
- create_invoice_history(invoice_id, history_record)     # Add note to invoice
- get_invoice_online_link(invoice_id)                    # Get online payment link

# Related Documents
- get_credit_notes()                                     # List credit notes
- create_credit_note(credit_note_data)                   # Create credit note
- get_prepayments()                                      # List prepayments
- get_overpayments()                                     # List overpayments

# Repeating Invoices
- get_repeating_invoices()                               # List recurring invoices
- create_repeating_invoice(template)                     # Create recurring invoice
- update_repeating_invoice(id, template)                 # Update recurring invoice
```

#### B. **Contacts & Relationships** (Current: 3 tools | Available: 15+ endpoints)

**Currently Implemented:**
- ✅ `xero_get_contacts` - List contacts
- ✅ `xero_get_contact_by_id` - Get single contact
- ✅ `xero_create_contact` - Create contact

**Missing Capabilities:**
```python
# Contact Operations
- update_contact(contact_id, contact_data)               # Modify existing contact
- delete_contact(contact_id)                             # Archive contact
- get_contact_groups()                                   # List contact groups
- create_contact_group(group_name, contacts)             # Create contact group
- get_contact_cis_settings(contact_id)                   # UK CIS settings

# Contact Attachments
- create_contact_attachment(contact_id, file)            # Upload file to contact
- get_contact_attachments(contact_id)                    # List contact attachments
- get_contact_attachment_content(contact_id, attachment_id)

# Contact History
- get_contact_history(contact_id)                        # Get contact activity
- create_contact_history(contact_id, history_record)     # Add note to contact
```

#### C. **Accounts & General Ledger** (Current: 1 tool | Available: 15+ endpoints)

**Currently Implemented:**
- ✅ `xero_get_accounts` - Get chart of accounts

**Missing Capabilities:**
```python
# Account Operations
- get_account_by_id(account_id)                          # Get single account
- create_account(account_data)                           # Create new account
- update_account(account_id, account_data)               # Modify account
- delete_account(account_id)                             # Archive account

# Account Attachments
- create_account_attachment(account_id, file)            # Upload file to account
- get_account_attachments(account_id)                    # List account attachments

# Journal Entries
- get_journals()                                         # List journal entries
- get_journal_by_id(journal_id)                          # Get specific journal
- create_manual_journal(journal_data)                    # Create manual journal
- update_manual_journal(journal_id, journal_data)        # Update manual journal
- get_manual_journals()                                  # List manual journals

# Tracking Categories (Dimensions)
- get_tracking_categories()                              # List tracking categories
- create_tracking_category(category_data)                # Create category
- update_tracking_category(category_id, category_data)   # Update category
- delete_tracking_category(category_id)                  # Delete category
- create_tracking_option(category_id, option_data)       # Add option to category
```

#### D. **Payments & Banking** (Available: 20+ endpoints)

```python
# Payments
- get_payments()                                         # List all payments
- create_payment(payment_data)                           # Record payment
- delete_payment(payment_id)                             # Delete payment
- get_payment_services()                                 # List payment services

# Bank Transactions
- get_bank_transactions()                                # List bank transactions
- create_bank_transaction(transaction_data)              # Create transaction
- update_bank_transaction(transaction_id, data)          # Update transaction
- get_bank_transaction_attachments(transaction_id)       # List attachments

# Bank Transfers
- get_bank_transfers()                                   # List bank transfers
- create_bank_transfer(transfer_data)                    # Create transfer
- get_bank_transfer_attachments(transfer_id)             # List attachments

# Batch Payments
- get_batch_payments()                                   # List batch payments
- create_batch_payment(batch_data)                       # Create batch payment
```

#### E. **Purchase Orders & Bills** (Available: 20+ endpoints)

```python
# Purchase Orders
- get_purchase_orders()                                  # List purchase orders
- create_purchase_order(po_data)                         # Create PO
- update_purchase_order(po_id, po_data)                  # Update PO
- delete_purchase_order(po_id)                           # Delete draft PO
- get_purchase_order_by_id(po_id)                        # Get specific PO
- get_purchase_order_history(po_id)                      # Get PO history
- create_purchase_order_history(po_id, note)             # Add note to PO

# Bills (Payable Invoices)
- get_bills()                                            # List bills/payable invoices
- create_bill(bill_data)                                 # Create bill
- update_bill(bill_id, bill_data)                        # Update bill
- get_bill_attachments(bill_id)                          # List bill attachments
```

#### F. **Quotes & Estimates** (Available: 10+ endpoints)

```python
# Quotes
- get_quotes()                                           # List quotes
- create_quote(quote_data)                               # Create quote
- update_quote(quote_id, quote_data)                     # Update quote
- get_quote_by_id(quote_id)                              # Get specific quote
- get_quote_history(quote_id)                            # Get quote history
- create_quote_history(quote_id, note)                   # Add note to quote
- get_quote_attachments(quote_id)                        # List attachments
```

#### G. **Items & Inventory** (Available: 10+ endpoints)

```python
# Items
- get_items()                                            # List items/products
- create_item(item_data)                                 # Create item
- update_item(item_id, item_data)                        # Update item
- delete_item(item_id)                                   # Delete item
- get_item_by_id(item_id)                                # Get specific item
- get_item_history(item_id)                              # Get item history
```

#### H. **Employees & Users** (Available: 10+ endpoints)

```python
# Employees
- get_employees()                                        # List employees
- create_employee(employee_data)                         # Create employee
- update_employee(employee_id, employee_data)            # Update employee
- get_employee_by_id(employee_id)                        # Get specific employee
```

#### I. **Tax Rates & Settings** (Available: 10+ endpoints)

```python
# Tax Rates
- get_tax_rates()                                        # List tax rates
- create_tax_rate(tax_data)                              # Create tax rate
- update_tax_rate(tax_type, tax_data)                    # Update tax rate

# Currencies
- get_currencies()                                       # List currencies
- create_currency(currency_code)                         # Add currency
```

#### J. **Organizations & Settings** (Available: 10+ endpoints)

```python
# Organization
- get_organisations()                                    # Get org details
- get_organisation_actions()                             # Get available actions
- get_organisation_cis_settings(org_id)                  # UK CIS settings

# Users
- get_users()                                            # List users
- get_user_by_id(user_id)                                # Get specific user

# Branding Themes
- get_branding_themes()                                  # List branding themes
- get_branding_theme_by_id(theme_id)                     # Get specific theme
```

#### K. **Reports & Analytics** (Available: 30+ endpoints)

```python
# Financial Reports
- get_report_profit_and_loss(date_from, date_to, periods)
- get_report_balance_sheet(date, periods, timeframe)
- get_report_trial_balance(date, paymentsOnly)
- get_report_budget_summary(date, periods)
- get_report_executive_summary(date)

# Tax Reports
- get_report_gst_report(report_id)                       # GST report
- get_report_bas_report()                                # BAS report (AU)
- get_report_aged_payables_by_contact(contact_id, date)
- get_report_aged_receivables_by_contact(contact_id, date)

# Banking Reports
- get_report_bank_summary(from_date, to_date)
- get_report_bank_statement(bank_account_id, from_date, to_date)
```

---

### 2. ASSETS API (Fixed Asset Management) - 10 Endpoints

```python
# Assets
- get_assets(status, page, page_size)                    # List fixed assets
- create_asset(asset_data)                               # Create asset
- get_asset_by_id(asset_id)                              # Get specific asset

# Asset Types
- get_asset_types()                                      # List asset types
- create_asset_type(type_data)                           # Create asset type

# Asset Settings
- get_asset_settings()                                   # Get depreciation settings
```

**Use Cases:**
- Track company vehicles, equipment, property
- Calculate depreciation for tax/accounting
- Manage asset disposal and transfers

---

### 3. FILES API (Document Management) - 15 Endpoints

```python
# Files
- get_files(pagesize, page, sort, direction)             # List files
- upload_file(file_data, name, filename, mime_type)      # Upload file
- upload_file_to_folder(folder_id, file_data, name)      # Upload to folder
- get_file(file_id)                                      # Get file metadata
- get_file_content(file_id)                              # Download file
- delete_file(file_id)                                   # Delete file
- rename_file(file_id, new_name)                         # Rename file
- move_file(file_id, folder_id)                          # Move file

# Folders
- get_folders(sort)                                      # List folders
- create_folder(folder_name)                             # Create folder
- get_folder(folder_id)                                  # Get folder details
- delete_folder(folder_id)                               # Delete folder
- rename_folder(folder_id, new_name)                     # Rename folder
- get_inbox()                                            # Get inbox folder

# File Associations (Link files to records)
- create_file_association(file_id, object_id, object_type)
- get_file_associations(file_id)                         # List associations
- get_associations_by_object(object_id)                  # Get object's files
- get_associations_count(object_ids)                     # Count associations
- delete_file_association(file_id, object_id)            # Unlink file
```

**Use Cases:**
- Store invoices, receipts, contracts
- Link documents to contacts, invoices, transactions
- Organize files in folders
- Access via Xero mobile app

---

### 4. PROJECTS API (Time Tracking & Profitability) - 17 Endpoints

```python
# Projects
- get_projects(project_ids, contact_id, states, page, page_size)
- create_project(project_data)                           # Create project
- update_project(project_id, project_data)               # Update project
- patch_project(project_id, patch_data)                  # Partial update
- get_project(project_id)                                # Get project details

# Tasks
- get_tasks(project_id, page, page_size, task_ids, charge_type)
- create_task(project_id, task_data)                     # Create task
- get_task(project_id, task_id)                          # Get task details
- update_task(project_id, task_id, task_data)            # Update task
- delete_task(project_id, task_id)                       # Delete task

# Time Entries
- get_time_entries(project_id, user_id, task_id, states, page)
- create_time_entry(project_id, time_entry_data)         # Log time
- get_time_entry(project_id, time_entry_id)              # Get time entry
- update_time_entry(project_id, time_entry_id, data)     # Update time
- delete_time_entry(project_id, time_entry_id)           # Delete time

# Project Users
- get_project_users(page, page_size)                     # List users
```

**Use Cases:**
- Track billable hours for clients
- Monitor project profitability
- Create tasks and assign to team members
- Generate time-based invoices

---

### 5. PAYROLL AU API (Australian Payroll) - 30+ Endpoints

```python
# Employees
- get_employees(if_modified_since, where, order, page)
- create_employee(employee_data)                         # Create employee
- get_employee(employee_id)                              # Get employee details

# Pay Items
- get_pay_items(if_modified_since, where, order, page)
- create_pay_item(pay_item_data)                         # Create pay item

# Pay Runs
- get_pay_runs(if_modified_since, where, order, page)
- create_pay_run(pay_run_data)                           # Create pay run
- update_pay_run(pay_run_id, pay_run_data)               # Update pay run

# Payslips
- get_payslip(payslip_id)                                # Get payslip
- update_payslip(payslip_id, payslip_data)               # Update payslip

# Leave Applications
- get_leave_applications(if_modified_since, where, order, page)
- create_leave_application(leave_data)                   # Create leave request
- approve_leave_application(leave_application_id)        # Approve leave
- reject_leave_application(leave_application_id)         # Reject leave

# Timesheets
- get_timesheets(if_modified_since, where, order, page)
- create_timesheet(timesheet_data)                       # Create timesheet
- update_timesheet(timesheet_id, timesheet_data)         # Update timesheet

# Payroll Calendars
- get_payroll_calendars(if_modified_since, where, order, page)
- create_payroll_calendar(calendar_data)                 # Create calendar
- get_payroll_calendar(calendar_id)                      # Get calendar details

# Superannuation
- get_superfunds(if_modified_since, where, order, page)
- create_superfund(superfund_data)                       # Create superfund
- get_superfund(superfund_id)                            # Get superfund details
- update_superfund(superfund_id, superfund_data)         # Update superfund
- get_superfund_products()                               # List super products

# Settings
- get_settings()                                         # Get payroll settings
```

**Use Cases:**
- Process Australian payroll
- Manage superannuation contributions
- Track leave balances and applications
- Generate payslips and payment files

---

### 6. PAYROLL UK API (UK Payroll) - 30+ Endpoints

```python
# Employees
- get_employees(if_modified_since, where, order, page)
- create_employee(employee_data)                         # Create employee
- get_employee(employee_id)                              # Get employee details
- get_employee_pay_template(employee_id)                 # Get pay template
- get_employee_payment_method(employee_id)               # Get payment method

# Benefits
- get_benefits(page)                                     # List benefits
- create_benefit(benefit_data)                           # Create benefit
- get_benefit(benefit_id)                                # Get benefit details

# Deductions
- get_deductions(page)                                   # List deductions
- create_deduction(deduction_data)                       # Create deduction
- get_deduction(deduction_id)                            # Get deduction details

# Earnings
- get_earnings_rates(page)                               # List earnings rates
- create_earnings_rate(earnings_rate_data)               # Create earnings rate
- get_earnings_rate(earnings_rate_id)                    # Get earnings rate

# Earnings Orders (Court Orders)
- get_earnings_orders(page)                              # List earnings orders
- get_earnings_order(earnings_order_id)                  # Get earnings order

# Pay Runs
- get_pay_runs(page)                                     # List pay runs
- create_pay_run(pay_run_data)                           # Create pay run
- get_pay_run(pay_run_id)                                # Get pay run details

# Pay Slips
- get_pay_slips(pay_run_id, page)                        # List payslips
- get_pay_slip(pay_run_id, payslip_id)                   # Get payslip

# Timesheets
- get_timesheets(page)                                   # List timesheets
- create_timesheet(timesheet_data)                       # Create timesheet
- get_timesheet(timesheet_id)                            # Get timesheet details

# Reimbursements
- get_reimbursements(page)                               # List reimbursements
- create_reimbursement(reimbursement_data)               # Create reimbursement
```

**Use Cases:**
- Process UK payroll with PAYE/NI
- Manage statutory payments (SSP, SMP, etc.)
- Handle court orders and deductions
- Generate RTI submissions to HMRC

---

### 7. PAYROLL NZ API (New Zealand Payroll) - 30+ Endpoints

```python
# Employees
- get_employees(page)                                    # List employees
- create_employee(employee_data)                         # Create employee
- get_employee(employee_id)                              # Get employee details
- get_employee_payment_method(employee_id)               # Get payment method
- get_employee_salary_and_wages(employee_id, page)       # Get salary/wage
- get_employee_tax(employee_id)                          # Get tax details

# Deductions
- get_deductions(page)                                   # List deductions
- create_deduction(deduction_data)                       # Create deduction
- get_deduction(deduction_id)                            # Get deduction details

# Earnings Rates
- get_earnings_rates(page)                               # List earnings rates
- create_earnings_rate(earnings_rate_data)               # Create earnings rate
- get_earnings_rate(earnings_rate_id)                    # Get earnings rate

# Leave Types
- get_leave_types(page)                                  # List leave types
- create_leave_type(leave_type_data)                     # Create leave type
- get_leave_type(leave_type_id)                          # Get leave type

# Pay Runs
- get_pay_runs(page)                                     # List pay runs
- create_pay_run(pay_run_data)                           # Create pay run
- get_pay_run(pay_run_id)                                # Get pay run details

# Pay Run Calendars
- get_pay_run_calendars(page)                            # List calendars
- create_pay_run_calendar(calendar_data)                 # Create calendar
- get_pay_run_calendar(calendar_id)                      # Get calendar

# Pay Slips
- get_pay_slips(pay_run_id, page)                        # List payslips
- get_pay_slip(pay_run_id, payslip_id)                   # Get payslip
- update_pay_slip_line_items(pay_run_id, payslip_id, data)

# Superannuation
- get_superannuations(page)                              # List super schemes
- create_superannuation(superannuation_data)             # Create scheme
- get_superannuation(superannuation_id)                  # Get scheme details

# Timesheets
- get_timesheets(page)                                   # List timesheets
- create_timesheet(timesheet_data)                       # Create timesheet
- get_timesheet(timesheet_id)                            # Get timesheet details
- approve_timesheet(timesheet_id)                        # Approve timesheet

# Settings
- get_settings()                                         # Get payroll settings
- get_tracking_categories()                              # Get tracking categories
```

**Use Cases:**
- Process NZ payroll with PAYE
- Manage KiwiSaver contributions
- Track leave and holidays
- Generate employment records

---

### 8. FINANCE API (Financial Analysis & Reporting) - 15 Endpoints

```python
# Accounting Activity
- get_accounting_activity_account_usage(xero_tenant_id, start_month, end_month)
- get_accounting_activity_lock_history(xero_tenant_id, end_date)
- get_accounting_activity_report_history(xero_tenant_id, end_date)
- get_accounting_activity_user_activities(xero_tenant_id, data_month)

# Bank Statements
- get_bank_statement_accounting(xero_tenant_id, bank_account_id, from_date, to_date, summary_only)

# Cash Position
- get_cash_validation(xero_tenant_id, balance_date, as_at_system_date, begin_date)

# Financial Statements
- get_financial_statement_balance_sheet(xero_tenant_id, balance_date, periods, timeframe, tracking_option_id)
- get_financial_statement_cashflow(xero_tenant_id, start_date, end_date, periods, timeframe, tracking_option_id)
- get_financial_statement_profit_and_loss(xero_tenant_id, start_date, end_date, periods, timeframe, tracking_option_id)
- get_financial_statement_trial_balance(xero_tenant_id, end_date)

# Contact Analysis
- get_financial_statement_contacts_revenue(xero_tenant_id, contact_ids, start_month, end_month)
- get_financial_statement_contacts_expense(xero_tenant_id, contact_ids, start_month, end_month)
```

**Use Cases:**
- Generate financial statements for reporting
- Analyze account usage and activity
- Track user actions for audit
- Monitor cash flow and bank reconciliations
- Analyze revenue/expense by contact

---

### 9. APP STORE API (Subscription & Usage Tracking) - 4 Endpoints

```python
# Subscriptions
- get_subscription(subscription_id)                      # Get subscription details

# Usage Records (for metered billing)
- get_usage_records(subscription_id)                     # List usage records
- post_usage_records(subscription_id, subscription_item_id, usage_data)
- put_usage_records(subscription_id, subscription_item_id, usage_record_id, usage_data)
```

**Use Cases:**
- Track API usage for billing
- Manage subscription status
- Record metered usage for customers

---

## Authentication & Connection Requirements

### OAuth 2.0 Flow (Required for all APIs)

```python
# 1. Authorization URL
authorization_url = 'https://login.xero.com/identity/connect/authorize'
params = {
    'response_type': 'code',
    'client_id': XERO_CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': 'offline_access accounting.transactions accounting.contacts ...',
    'state': random_state
}

# 2. Exchange code for tokens
token_url = 'https://identity.xero.com/connect/token'
token_data = {
    'grant_type': 'authorization_code',
    'code': authorization_code,
    'redirect_uri': REDIRECT_URI,
    'client_id': XERO_CLIENT_ID,
    'client_secret': XERO_CLIENT_SECRET
}

# 3. Get tenant/organization IDs
connections_url = 'https://api.xero.com/connections'
headers = {'Authorization': f'Bearer {access_token}'}

# 4. Make API calls with tenant ID header
headers = {
    'Authorization': f'Bearer {access_token}',
    'Xero-Tenant-Id': tenant_id,
    'Accept': 'application/json'
}
```

### Required OAuth Scopes

```
# Core Scopes
offline_access                          # Refresh token
openid profile email                    # User info

# Accounting Scopes
accounting.transactions                 # Invoices, bills, payments
accounting.contacts                     # Contacts
accounting.settings                     # Accounts, tracking categories
accounting.reports.read                 # Financial reports
accounting.journals.read                # Journal entries
accounting.attachments                  # File attachments

# Asset Scopes
assets                                  # Fixed assets
assets.read                             # Read-only assets

# Files Scopes
files                                   # Files API
files.read                              # Read-only files

# Projects Scopes
projects                                # Projects API
projects.read                           # Read-only projects

# Payroll Scopes
payroll.employees                       # Employees
payroll.payruns                         # Pay runs
payroll.payslip                         # Payslips
payroll.timesheets                      # Timesheets
payroll.settings                        # Payroll settings

# Finance Scopes
finance.statements.read                 # Financial statements
finance.accountingactivity.read         # Account activity
finance.cashvalidation.read             # Cash validation
```

---

## Implementation Priority Recommendations

### Phase 1: Core Accounting Expansion (High Priority)
**Add ~40 critical accounting tools**

```python
# Must-Have Tools (Priority 1)
1. xero_update_invoice              # Modify invoices
2. xero_delete_invoice              # Delete/void invoices
3. xero_create_payment              # Record payments
4. xero_get_payments                # List payments
5. xero_update_contact              # Modify contacts
6. xero_create_bank_transaction     # Record bank transactions
7. xero_get_bank_transactions       # List bank transactions
8. xero_create_credit_note          # Create credit notes
9. xero_get_credit_notes            # List credit notes
10. xero_email_invoice              # Send invoices via email

# High-Value Tools (Priority 2)
11. xero_get_reports_profit_loss    # P&L report
12. xero_get_reports_balance_sheet  # Balance sheet
13. xero_get_reports_aged_receivables  # AR aging
14. xero_get_reports_aged_payables   # AP aging
15. xero_create_invoice_attachment   # Upload invoice docs
16. xero_get_invoice_attachments     # Download invoice docs
17. xero_create_purchase_order       # Create POs
18. xero_get_purchase_orders         # List POs
19. xero_create_quote                # Create quotes
20. xero_get_quotes                  # List quotes
```

### Phase 2: Files & Documents (Medium Priority)
**Add ~15 file management tools**

```python
# File Operations
21. xero_upload_file                 # Upload documents
22. xero_get_files                   # List files
23. xero_download_file               # Download files
24. xero_create_folder               # Create folder
25. xero_get_folders                 # List folders
26. xero_create_file_association     # Link file to record
27. xero_get_file_associations       # List linked files
```

### Phase 3: Projects & Time Tracking (Medium Priority)
**Add ~15 project management tools**

```python
# Project Management
28. xero_create_project              # Create project
29. xero_get_projects                # List projects
30. xero_create_task                 # Create task
31. xero_get_tasks                   # List tasks
32. xero_create_time_entry           # Log time
33. xero_get_time_entries            # List time entries
34. xero_get_project_users           # List project users
```

### Phase 4: Payroll (Low Priority - Specialized)
**Add ~30 payroll tools (by region)**

```python
# Australian Payroll
35. xero_au_get_employees
36. xero_au_create_employee
37. xero_au_create_payrun
38. xero_au_get_payslip

# UK Payroll
39. xero_uk_get_employees
40. xero_uk_create_benefit
41. xero_uk_create_payrun

# NZ Payroll
42. xero_nz_get_employees
43. xero_nz_create_timesheet
44. xero_nz_approve_timesheet
```

### Phase 5: Advanced Features (Low Priority)
**Add ~20 specialized tools**

```python
# Fixed Assets
45. xero_get_assets                  # List fixed assets
46. xero_create_asset                # Create asset

# Finance API
47. xero_get_financial_statements    # Advanced reports
48. xero_get_bank_statement_accounting

# App Store (if you build a Xero app)
49. xero_get_subscription
50. xero_post_usage_records
```

---

## Recommended Tool Organization

### Folder Structure
```
tools/
├── schemas/
│   ├── xero_accounting_tools.json       # Core accounting (40 tools)
│   ├── xero_files_tools.json            # Files API (15 tools)
│   ├── xero_projects_tools.json         # Projects API (15 tools)
│   ├── xero_payroll_au_tools.json       # AU Payroll (30 tools)
│   ├── xero_payroll_uk_tools.json       # UK Payroll (30 tools)
│   ├── xero_payroll_nz_tools.json       # NZ Payroll (30 tools)
│   ├── xero_assets_tools.json           # Assets API (10 tools)
│   ├── xero_finance_tools.json          # Finance API (15 tools)
│   └── xero_appstore_tools.json         # App Store API (4 tools)
│
└── implementations/
    ├── xero_accounting.py                # Core accounting functions
    ├── xero_files.py                     # Files functions
    ├── xero_projects.py                  # Projects functions
    ├── xero_payroll_au.py                # AU Payroll functions
    ├── xero_payroll_uk.py                # UK Payroll functions
    ├── xero_payroll_nz.py                # NZ Payroll functions
    ├── xero_assets.py                    # Assets functions
    ├── xero_finance.py                   # Finance functions
    └── xero_appstore.py                  # App Store functions
```

### Tool Naming Convention

```python
# Pattern: xero_{api_set}_{action}_{resource}

# Accounting API
xero_accounting_get_invoices
xero_accounting_create_invoice
xero_accounting_update_invoice
xero_accounting_delete_invoice
xero_accounting_get_payments
xero_accounting_create_payment

# Files API
xero_files_upload_file
xero_files_get_files
xero_files_download_file
xero_files_create_folder

# Projects API
xero_projects_get_projects
xero_projects_create_project
xero_projects_create_time_entry

# Payroll APIs
xero_payroll_au_get_employees
xero_payroll_uk_create_payrun
xero_payroll_nz_approve_timesheet
```

---

## Key Implementation Patterns

### 1. Tenant ID Header (Required for ALL calls)

```python
def make_xero_api_call(endpoint, access_token, tenant_id, method='GET', data=None):
    """All Xero API calls MUST include Xero-Tenant-Id header"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-Tenant-Id': tenant_id,  # CRITICAL!
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method=method,
        url=endpoint,
        headers=headers,
        json=data
    )
    return response.json()
```

### 2. Idempotency Keys (for POST/PUT operations)

```python
import uuid

def create_invoice_with_idempotency(invoice_data, access_token, tenant_id):
    """Prevent duplicate invoices with idempotency key"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-Tenant-Id': tenant_id,
        'Idempotency-Key': str(uuid.uuid4()),  # Unique per request
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'https://api.xero.com/api.xro/2.0/Invoices',
        headers=headers,
        json={'Invoices': [invoice_data]}
    )
    return response.json()
```

### 3. Pagination (for large result sets)

```python
def get_all_invoices_paginated(access_token, tenant_id):
    """Paginate through all invoices"""
    page = 1
    all_invoices = []
    
    while True:
        response = make_xero_api_call(
            f'https://api.xero.com/api.xro/2.0/Invoices?page={page}',
            access_token,
            tenant_id
        )
        
        invoices = response.get('Invoices', [])
        if not invoices:
            break
            
        all_invoices.extend(invoices)
        page += 1
    
    return all_invoices
```

### 4. File Uploads (multipart/form-data)

```python
def upload_invoice_attachment(invoice_id, file_path, access_token, tenant_id):
    """Upload file to invoice"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-Tenant-Id': tenant_id
    }
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(
            f'https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}/Attachments/{os.path.basename(file_path)}',
            headers=headers,
            files=files
        )
    
    return response.json()
```

### 5. Error Handling (Xero-specific)

```python
class XeroAPIError(Exception):
    """Custom exception for Xero API errors"""
    pass

def handle_xero_error(response):
    """Parse Xero API error responses"""
    if response.status_code >= 400:
        error_data = response.json()
        
        # Xero errors format
        if 'Elements' in error_data:
            errors = error_data['Elements'][0]['ValidationErrors']
            error_messages = [err['Message'] for err in errors]
            raise XeroAPIError(f"Xero API Error: {', '.join(error_messages)}")
        
        # Rate limit errors
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            raise XeroAPIError(f"Rate limit exceeded. Retry after {retry_after} seconds")
        
        raise XeroAPIError(f"HTTP {response.status_code}: {response.text}")
```

---

## Testing Strategy

### 1. Use Xero Demo Company

```python
# Xero provides a demo company for testing
# https://developer.xero.com/documentation/getting-started-guide/demo-companies
```

### 2. Test with Different Scopes

```python
# Test read-only operations first
scopes_readonly = "offline_access accounting.transactions.read accounting.contacts.read"

# Then test write operations
scopes_full = "offline_access accounting.transactions accounting.contacts"
```

### 3. Validate Webhook Signatures

```python
import hmac
import hashlib
import base64

def verify_xero_webhook_signature(request_body, signature_header, webhook_key):
    """Verify webhook authenticity"""
    computed_signature = base64.b64encode(
        hmac.new(
            webhook_key.encode(),
            request_body,
            hashlib.sha256
        ).digest()
    ).decode()
    
    return hmac.compare_digest(computed_signature, signature_header)
```

---

## Performance Considerations

### Rate Limits

```
# Accounting API
- 60 requests per minute per organization
- 5,000 requests per day per organization

# Other APIs
- Vary by API set, check Xero documentation

# Rate Limit Headers
X-Rate-Limit-Limit: 60
X-Rate-Limit-Remaining: 59
X-Rate-Limit-Problem: minute
```

### Caching Strategy

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_or_fetch(cache_key, fetch_function, ttl=300):
    """Cache Xero API responses to reduce API calls"""
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    data = fetch_function()
    cache.setex(cache_key, ttl, json.dumps(data))
    return data

# Example usage
accounts = get_cached_or_fetch(
    f'xero_accounts_{tenant_id}',
    lambda: xero_get_accounts(access_token, tenant_id),
    ttl=3600  # Cache for 1 hour
)
```

---

## Summary Statistics

| Category | Current Tools | Available Endpoints | Coverage |
|----------|---------------|---------------------|----------|
| **Accounting API** | 7 | ~200 | 3.5% |
| **Assets API** | 0 | 10 | 0% |
| **Files API** | 0 | 15 | 0% |
| **Projects API** | 0 | 17 | 0% |
| **Payroll AU API** | 0 | 30 | 0% |
| **Payroll UK API** | 0 | 30 | 0% |
| **Payroll NZ API** | 0 | 30 | 0% |
| **Finance API** | 0 | 15 | 0% |
| **App Store API** | 0 | 4 | 0% |
| **TOTAL** | **7** | **~350** | **2%** |

---

## Recommended Next Steps

1. **Phase 1 Implementation (2-3 weeks)**
   - Add 40 core accounting tools (invoices, payments, contacts, transactions)
   - Implement proper error handling and pagination
   - Add comprehensive tests with demo company

2. **Phase 2 Implementation (1-2 weeks)**
   - Add Files API (15 tools)
   - Add Projects API (15 tools)
   - Implement file upload/download

3. **Phase 3 Implementation (2-3 weeks)**
   - Choose payroll region (AU/UK/NZ based on user needs)
   - Add payroll tools for chosen region (~30 tools)
   - Implement payroll-specific features

4. **Phase 4 Implementation (1 week)**
   - Add Assets API (10 tools)
   - Add Finance API (15 tools)
   - Add App Store API (4 tools)

**Total Implementation Time:** 6-9 weeks for complete Xero coverage

**Result:** 180+ Xero tools covering all business functions

---

## Additional Resources

- **Xero API Explorer:** https://developer.xero.com/documentation/api-explorer
- **Xero API Status:** https://status.developer.xero.com/
- **Xero SDKs:** https://github.com/XeroAPI
- **Community Forum:** https://community.xero.com/developer/
- **OAuth 2.0 Guide:** https://developer.xero.com/documentation/guides/oauth2/overview

---

**Last Updated:** November 13, 2025  
**Status:** Research Complete - Ready for Implementation  
**Estimated Tools to Add:** 170+ (from 7 to 180+)
