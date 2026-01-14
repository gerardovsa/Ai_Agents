# Xero Contact Data Structure - Complete Field Reference

**Generated:** January 4, 2026  
**Source:** Xero API v2.0 (api.xero.com/api.xro/2.0)

---

## 📊 Summary

Accessed Xero API for 3 businesses:
- **InHouse Print** - 100 contacts
- **InHouse Publishing** - 100 contacts  
- **InHouse Signs** - 100 contacts

---

## 🔑 Core Contact Fields

### Primary Identifiers
```json
{
  "ContactID": "996dfeab-0754-4d5c-881b-00740d6d12a2",  // UUID
  "ContactNumber": null,                                 // Optional customer number
  "Name": "CJ King Printing",                           // Display name (REQUIRED)
  "ContactStatus": "ACTIVE"                             // ACTIVE, ARCHIVED, GDPRREQUEST
}
```

### Personal Information
```json
{
  "FirstName": null,         // First name (for person contacts)
  "LastName": null,          // Last name (for person contacts)
  "EmailAddress": "",        // Primary email
  "TaxNumber": null,         // ABN/ACN/Tax ID
  "BankAccountDetails": ""   // Bank account info
}
```

### Contact Classification
```json
{
  "IsCustomer": false,       // Customer flag
  "IsSupplier": false,       // Supplier flag
  "DefaultCurrency": null    // e.g., "AUD", "USD"
}
```

### Tax Configuration
```json
{
  "AccountsReceivableTaxType": null,  // Tax rate for sales
  "AccountsPayableTaxType": null      // Tax rate for purchases
}
```

---

## 📞 Phone Numbers Array

Xero supports **4 phone types** per contact:

```json
"Phones": [
  {
    "PhoneType": "DDI",              // Direct Dial In
    "PhoneNumber": "",
    "PhoneAreaCode": "",
    "PhoneCountryCode": ""
  },
  {
    "PhoneType": "DEFAULT",          // Main phone
    "PhoneNumber": "",
    "PhoneAreaCode": "",
    "PhoneCountryCode": ""
  },
  {
    "PhoneType": "FAX",              // Fax number
    "PhoneNumber": "",
    "PhoneAreaCode": "",
    "PhoneCountryCode": ""
  },
  {
    "PhoneType": "MOBILE",           // Mobile phone
    "PhoneNumber": "",
    "PhoneAreaCode": "",
    "PhoneCountryCode": ""
  }
]
```

**Available Phone Types:**
- `DEFAULT` - Primary phone
- `DDI` - Direct Dial In
- `MOBILE` - Mobile/cell phone
- `FAX` - Fax machine

---

## 🏠 Addresses Array

Xero supports **3 address types** per contact:

```json
"Addresses": [
  {
    "AddressType": "POBOX",          // PO Box address
    "AddressLine1": null,            // First line
    "AddressLine2": null,            // Second line (optional)
    "City": "",
    "Region": "",                    // State/Province
    "PostalCode": "",
    "Country": ""
  },
  {
    "AddressType": "STREET",         // Physical street address
    "AddressLine1": null,
    "AddressLine2": null,
    "City": "",
    "Region": "",
    "PostalCode": "",
    "Country": ""
  },
  {
    "AddressType": "DELIVERY",       // Delivery address (if different)
    "AddressLine1": null,
    "AddressLine2": null,
    "City": "",
    "Region": "",
    "PostalCode": "",
    "Country": ""
  }
]
```

**Available Address Types:**
- `POBOX` - PO Box address
- `STREET` - Physical street address
- `DELIVERY` - Separate delivery address

---

## 👥 Contact Persons Array

Multiple contact persons can be associated with a company contact:

```json
"ContactPersons": [
  {
    "FirstName": "John",
    "LastName": "Smith",
    "EmailAddress": "john@company.com",
    "IncludeInEmails": true,
    "PhoneNumbers": [
      {
        "PhoneType": "DEFAULT",
        "PhoneNumber": "0412345678"
      }
    ]
  }
]
```

---

## 📋 Additional Metadata

```json
{
  "UpdatedDateUTC": "/Date(1487615896353+0000)/",  // Last update timestamp
  "ContactGroups": [],                              // Contact group assignments
  "HasAttachments": false,                          // Files attached to contact
  "HasValidationErrors": false                      // Validation status
}
```

---

## 🔍 Sample Contact Examples

### Example 1: InHouse Print Contact
```json
{
  "ContactID": "996dfeab-0754-4d5c-881b-00740d6d12a2",
  "Name": "CJ King Printing",
  "ContactStatus": "ACTIVE",
  "EmailAddress": "",
  "IsCustomer": false,
  "IsSupplier": false,
  "Phones": [4 phone type slots - all empty],
  "Addresses": [2 address slots - POBOX + STREET - all empty],
  "ContactPersons": [],
  "UpdatedDateUTC": "/Date(1487615896353+0000)/"
}
```

### Example 2: InHouse Publishing Contact
```json
{
  "ContactID": "008507cc-7c17-4365-9996-02409bbaaa2c",
  "Name": "Justeen Angelic",
  "ContactStatus": "ACTIVE",
  "EmailAddress": "publishing@inhouseprint.com.au",
  "IsCustomer": false,
  "IsSupplier": false,
  "Phones": [4 phone type slots - all empty],
  "Addresses": [2 address slots - all empty]
}
```

---

## 📊 Data Quality Observations

### Current State Analysis:

**InHouse Print (100 contacts):**
- ✅ All contacts have `Name` field
- ⚠️ Most contacts missing:
  - Email addresses (empty strings)
  - Phone numbers (empty arrays)
  - Physical addresses (empty fields)
  - Customer/Supplier flags (false)

**InHouse Publishing (100 contacts):**
- ✅ All contacts have `Name` field
- ⚠️ Similar data quality issues
- ✅ Some contacts have email (e.g., publishing@inhouseprint.com.au)

**InHouse Signs (100 contacts):**
- ✅ All contacts have `Name` field
- ⚠️ Data quality similar to other businesses

### Missing Fields (Common Issues):
1. **Email addresses** - Most are empty strings
2. **Phone numbers** - Phone arrays exist but numbers are empty
3. **Addresses** - Address structures exist but fields are empty
4. **Contact classification** - Most contacts not marked as Customer/Supplier
5. **FirstName/LastName** - Not populated (only Name field used)

---

## 🛠️ API Capabilities

### Read Operations:
- **GET /Contacts** - List all contacts
- **GET /Contacts/{ContactID}** - Get single contact
- **Filtering:** Support for `where` clause
  - `Name.Contains("search")`
  - `UpdatedDateUTC>=DateTime(2025,1,1)`
  - `IsCustomer==true`

### Write Operations:
- **POST /Contacts** - Create new contact
- **PUT /Contacts/{ContactID}** - Update existing contact
- **DELETE /Contacts/{ContactID}** - Archive contact

### Required Fields for Creation:
- ✅ `Name` - **REQUIRED** (minimum requirement)
- All other fields are **optional**

---

## 💡 Recommendations for Customer Intelligence

### Data Enrichment Opportunities:

1. **Email Collection**
   - Most contacts missing email addresses
   - Critical for automated marketing campaigns
   - **Action:** Add email capture workflow in quote/invoice process

2. **Phone Number Completion**
   - Phone structures exist but data missing
   - Important for urgent customer contact
   - **Action:** Prompt for phone during customer creation

3. **Address Validation**
   - Empty address fields limit delivery tracking
   - Required for accurate shipping
   - **Action:** Validate addresses during order placement

4. **Customer Classification**
   - `IsCustomer`/`IsSupplier` flags mostly false
   - Limits customer-specific reporting
   - **Action:** Auto-flag on first invoice/order

5. **Contact Persons**
   - No contact persons defined
   - Limits personalized communication
   - **Action:** Allow multiple contacts per company

---

## 🔗 Integration with Customer Intelligence Tab

### Current Usage in Customer Intelligence Pipeline:

The Customer Intelligence tab (`xero_routes.py` lines 2646-3237) currently uses:

**From Xero Contacts:**
- ✅ `ContactID` - Unique identifier
- ✅ `Name` - Display name

**From Xero Invoices (Primary Data Source):**
- Invoice dates (first/last/all)
- Invoice amounts (lifetime revenue)
- Payment status (on-time/late)
- Outstanding balances

**Calculated Fields:**
- RFM segmentation
- ML churn probability
- Risk scores
- Behavior trends
- Recommended actions

### Enhancement Opportunities:

**If email data was complete:**
- Enable email campaign tracking
- Measure email engagement (opens/clicks)
- Segment by email domain (corporate vs personal)

**If phone data was complete:**
- Enable SMS campaigns
- Track call outcomes
- Prioritize high-value customers for phone contact

**If address data was complete:**
- Geographic segmentation
- Delivery optimization
- Regional campaign targeting

---

## 📝 Next Steps

### Immediate Actions:
1. ✅ Document Xero contact structure (COMPLETED)
2. 🔄 Identify data quality gaps (COMPLETED)
3. 📋 Plan data enrichment strategy

### Future Enhancements:
1. **Data Collection Workflow**
   - Add prompts in quote/invoice creation
   - Pre-fill from previous orders
   - Validate against external databases

2. **Contact Segmentation**
   - Use `ContactGroups` for custom segments
   - Sync segments with Customer Intelligence classifications

3. **Enhanced Reporting**
   - Cross-reference contact data with invoice data
   - Show data completeness metrics in dashboard
   - Alert on missing critical fields (email, phone)

---

**Generated by:** Xero API Test Script  
**Location:** `test_xero_contact_data.py`  
**API Version:** Xero API v2.0
