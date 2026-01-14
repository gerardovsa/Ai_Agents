# AI Agent Quick Reference - Database Structure with Examples

## 📋 How to Use the Enhanced Database Report

### File Location
```
c:\Users\gpoli\GIT\AI_agents\data\database_analysis_report.txt
```

### When to Use This Report

Use this report when you need to:
1. ✅ Write SQL queries
2. ✅ Validate data before insertion
3. ✅ Understand foreign key relationships
4. ✅ Build API responses
5. ✅ Debug data issues
6. ✅ Design new features
7. ✅ Understand data patterns

## 🔍 Reading the Report

### Column Information Format
```
column_name                    DATA_TYPE       [CONSTRAINTS]
  Examples: value1, value2, value3
```

### Example Entry
```
platform                       TEXT            [NOT NULL]
  Examples: "google", "microsoft"
```

**What this tells you:**
- Column name: `platform`
- Data type: `TEXT` (string)
- Constraint: `[NOT NULL]` (required)
- Valid values: Only "google" or "microsoft" (lowercase, no variations)

## 📊 Understanding Different Example Types

### 1. Normal Examples (Most Common)
```
email                          TEXT           
  Examples: "user@domain.com", "admin@company.org"
```
**Meaning:** Column has data, showing 1-3 real examples

### 2. Empty Table
```
id                             INTEGER         [PK]
  Examples: (table empty)
```
**Meaning:** Table exists but has no rows yet

### 3. NULL-Only Column
```
revoked_at                     TIMESTAMP      
  Examples: (all NULL)
```
**Meaning:** Column exists but all values are NULL (never used yet)

### 4. Truncated Long Values
```
raw_json                       TEXT           
  Examples: "{"id": 6261741781187, "admin_graphql_api_id": ..."
```
**Meaning:** Value is longer than 50 chars (truncated with "...")

## 🎯 Common Use Cases

### Use Case 1: Building WHERE Clauses

**Task:** Query for active Microsoft tokens

**Look up:**
```
TABLE: oauth_tokens
  platform                       TEXT            [NOT NULL]
    Examples: "google", "microsoft"
  is_active                      BOOLEAN        
    Examples: 1
```

**Result:**
```sql
SELECT * FROM oauth_tokens 
WHERE platform = 'microsoft'  -- ✅ lowercase
AND is_active = 1;            -- ✅ integer 1, not boolean true
```

### Use Case 2: Data Validation

**Task:** Validate session status before insert

**Look up:**
```
TABLE: synergy_sessions
  status                         TEXT           
    Examples: "active", "paused", "in_progress"
```

**Result:**
```python
VALID_STATUSES = ['active', 'paused', 'in_progress']
if status not in VALID_STATUSES:
    raise ValueError(f"Invalid status: {status}")
```

### Use Case 3: Understanding Date Formats

**Task:** Parse timestamp from database

**Look up:**
```
created_at                     TIMESTAMP      
  Examples: "2025-10-29 13:19:36", "2025-10-30 09:49:23"
```

**Result:**
```python
from datetime import datetime
dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
```

### Use Case 4: JSON Structure

**Task:** Parse metadata field

**Look up:**
```
metadata                       TEXT           
  Examples: "{"google_id": "106194727360309483287", "picture...", "{"microsoft_id": "c7e77a9f-f08c-49fb-addc-05689..."
```

**Result:**
```python
import json
meta = json.loads(metadata)
google_id = meta.get('google_id')      # For Google tokens
microsoft_id = meta.get('microsoft_id') # For Microsoft tokens
```

### Use Case 5: Foreign Key Joins

**Look up:**
```
TABLE: oauth_tokens
  user_id                        INTEGER         [NOT NULL]
    Examples: 3, 5, 12

Foreign Keys:
  user_id -> users.id
```

**Result:**
```sql
SELECT 
    u.username,
    o.platform,
    o.email
FROM oauth_tokens o
JOIN users u ON o.user_id = u.id  -- ✅ Integer join
WHERE u.id = 3;
```

## 💡 Pro Tips

### Tip 1: Check Row Count First
```
TABLE: account_link_requests - 0 rows
```
**If row count is 0, don't query this table!** It's empty.

### Tip 2: Look at ALL Examples
```
Examples: "active", "paused", "in_progress"
```
These are likely **ALL** the valid values (not just samples). Use for validation!

### Tip 3: Boolean Values
```
is_active                      BOOLEAN        
  Examples: 1
```
SQLite uses **integers for booleans**: `1` = true, `0` = false (not `true`/`false`)

### Tip 4: ID Patterns
```
id                             INTEGER         [PK]
  Examples: 15, 8, 99

shopify_order_id               TEXT            [NOT NULL]
  Examples: "6153174220995", "6156133433539"
```
- Integer IDs → Auto-increment
- Text IDs → External system identifiers (strings)

### Tip 5: Timestamp Formats
```
created_at                     TIMESTAMP      
  Examples: "2025-10-29 13:19:36"

created_at                     TEXT
  Examples: "2025-11-01T23:53:52.348379"
```
Two formats used:
- `TIMESTAMP` → SQL format: `YYYY-MM-DD HH:MM:SS`
- `TEXT` → ISO format: `YYYY-MM-DDTHH:MM:SS.ffffff`

### Tip 6: Array/JSON Fields
```
tags                           TEXT           
  Examples: "["enterprise", "integration", "ecommerce"..."
```
If examples start with `[` or `{`, field contains JSON (parse it!)

## 🚫 Common Mistakes to Avoid

### Mistake 1: Case Sensitivity
❌ **Wrong:**
```sql
WHERE platform = 'Google'  -- WRONG! Examples show lowercase
```

✅ **Correct:**
```sql
WHERE platform = 'google'  -- ✅ Match the example exactly
```

### Mistake 2: Boolean Comparison
❌ **Wrong:**
```sql
WHERE is_active = true  -- WRONG! SQLite uses integers
```

✅ **Correct:**
```sql
WHERE is_active = 1  -- ✅ Integer comparison
```

### Mistake 3: Assuming Values
❌ **Wrong:**
```python
# Assuming values without checking examples
VALID_STATUSES = ['active', 'inactive', 'pending']  # WRONG!
```

✅ **Correct:**
```python
# Check examples first, then validate
VALID_STATUSES = ['active', 'paused', 'in_progress']  # ✅ From examples
```

### Mistake 4: Wrong Date Format
❌ **Wrong:**
```python
dt = datetime.fromtimestamp(int(created_at))  # WRONG! Not Unix timestamp
```

✅ **Correct:**
```python
dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')  # ✅ SQL format
```

### Mistake 5: Ignoring NULL Examples
❌ **Wrong:**
```python
# Assuming field always has value
last_error = row['last_refresh_error'].strip()  # WRONG! Could be NULL
```

✅ **Correct:**
```python
# Check examples: (all NULL) → Optional field
last_error = row['last_refresh_error']
if last_error:  # ✅ Handle NULL case
    process_error(last_error)
```

## 📚 Quick Lookup Guide

### Find Database
```
Ctrl+F: "DATABASE: database_name"
```

### Find Table
```
Ctrl+F: "TABLE: table_name"
```

### Find Column
```
Ctrl+F: "column_name"
```

### Check Foreign Keys
Look for "Foreign Keys:" section after column list

### Check Table Size
Look at row count: `TABLE: name - X rows`

## 🎓 Learning Exercise

**Try this:** Pick any table and answer these questions just from the report:

1. How many rows does the table have?
2. What is the primary key column?
3. What are the required (NOT NULL) columns?
4. What are the valid values for any TEXT columns?
5. What is the format of any TIMESTAMP columns?
6. Are there any foreign keys?
7. Which columns are always NULL (unused)?
8. Which columns contain JSON data?

**Example:**
```
TABLE: oauth_tokens - 5 rows

1. Row count: 5 rows
2. Primary key: id (INTEGER [PK])
3. Required: user_id, platform, access_token
4. Valid values:
   - platform: "google", "microsoft"
   - token_type: "Bearer"
5. Timestamp format: "2025-10-29 13:19:36" (SQL format)
6. Foreign keys: user_id -> users.id
7. Unused columns: last_refresh_error (all NULL), revoked_at (all NULL)
8. JSON columns: metadata (starts with "{")
```

## 🔄 Report Refresh

**When to re-run the analyzer:**
- After adding new tables
- After major data migrations
- Monthly (to see new data patterns)
- When examples seem outdated

**How to re-run:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents\data
python show_database_structure.py
```

## 📞 Help

**If examples don't match your query results:**
1. Check if you're using the correct database
2. Re-run the analyzer to refresh examples
3. Verify table and column names (case-sensitive)
4. Check for recent data changes

**If you need more examples:**
- Current limit: 3 examples per column
- To see all distinct values, query directly:
  ```sql
  SELECT DISTINCT column_name FROM table_name;
  ```

---

**Last Updated:** November 11, 2025  
**Report Version:** 2.0 (with examples)  
**Status:** Production Ready ✅
