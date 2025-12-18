# Auto Database Entry Guide
**Computer Use Integration for Professional Verification**

Last Updated: December 18, 2025

---

## Overview

The Auto Database Entry system uses **Anthropic Computer Use API** to automatically enter verified professional data into databases, CRMs, and web forms. Claude acts as a virtual assistant that can:

- Navigate websites in a browser
- Fill form fields with verification data
- Submit forms and verify success
- Capture screenshots for audit trail
- Process batches of records automatically

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Platform                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Professional Verification Module                            │
│  ├── Advanced Analysis (analyze_content_with_ai, etc.)      │
│  ├── Web Scraping (scrape_website_content, etc.)           │
│  └── Auto Database Entry  ← NEW                             │
│      ├── auto_enter_verification_results()                  │
│      ├── auto_enter_to_postgres()                          │
│      └── batch_enter_verifications()                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Computer Use Executor (SINGLETON)               │
│         AI_infrastructure/core/computer_use_executor.py     │
│                                                               │
│  ├── get_browser_container() - Start Docker browser         │
│  ├── take_screenshot() - Capture display                    │
│  ├── move_mouse() - Control cursor                          │
│  ├── click_mouse() - Click elements                         │
│  ├── type_text() - Enter text                               │
│  └── press_key() - Keyboard control                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container                          │
│              (Ubuntu + Chrome + VNC Display)                 │
│                                                               │
│  ├── X11 Virtual Display (1920x1080)                        │
│  ├── Google Chrome Browser                                   │
│  ├── VNC Server (port 5900)                                 │
│  └── Python 3.11 + Anthropic SDK                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Anthropic Computer Use API                      │
│          (Claude Sonnet 4.5 with computer_20241022)         │
│                                                               │
│  Claude receives:                                            │
│  ├── Task instruction ("Fill this form with data...")       │
│  ├── Screenshot of current display                          │
│  └── Available actions (mouse, keyboard, screenshot)        │
│                                                               │
│  Claude responds with:                                       │
│  ├── Next action to take                                     │
│  ├── Coordinates for mouse movements                        │
│  ├── Text to type                                            │
│  └── Status updates                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Docker Desktop
Computer Use requires Docker to run browser containers:

```powershell
# Check Docker is running
docker ps

# If not installed, download from:
# https://www.docker.com/products/docker-desktop
```

### 2. Anthropic API Key
Get your API key from: https://console.anthropic.com/

```powershell
# Set environment variable
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Or add to .env file
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Computer Use Docker Image
Build the browser container image:

```bash
cd AI_infrastructure/docker/computer-use
docker build -t computer-use:latest .
```

---

## Usage Examples

### Example 1: Enter Single Verification Result

```python
from auto_database_entry import auto_enter_verification_results

result = await auto_enter_verification_results(
    verification_data={
        'name': 'Gregory Dutton',
        'company': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'legitimacy_score': 42.3,
        'status': 'UNCERTAIN',
        'notes': 'Requires manual verification - 27 historical snapshots but low traffic'
    },
    target_system='crm',
    target_url='https://your-crm.com/contacts/new',
    form_fields={
        'contact_name': 'name',
        'company_name': 'company',
        'email_address': 'email',
        'risk_rating': 'legitimacy_score',
        'verification_status': 'status',
        'additional_notes': 'notes'
    }
)

print(f"Success: {result['success']}")
print(f"Records created: {result['records_created']}")
print(f"Time taken: {result['execution_time']}s")
print(f"Actions: {result['actions_taken']}")
```

**What happens:**
1. Docker browser container starts
2. Claude navigates to `https://your-crm.com/contacts/new`
3. Claude takes screenshot to see the page
4. Claude locates form field with name/id/label matching `contact_name`
5. Claude fills it with "Gregory Dutton"
6. Repeat for all fields
7. Claude clicks Submit button
8. Claude verifies success message
9. Final screenshot captured
10. Container cleaned up

### Example 2: Direct PostgreSQL Insert

```python
from auto_database_entry import auto_enter_to_postgres

result = await auto_enter_to_postgres(
    verification_data={
        'full_name': 'Gregory Dutton',
        'company_name': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'domain': 'isb.eco',
        'legitimacy_score': 42.3,
        'verification_status': 'UNCERTAIN',
        'domain_authority': 27,
        'web_archive_snapshots': 27,
        'ssl_certificates': 27,
        'requires_manual_review': True,
        'verification_date': '2025-12-18'
    },
    table_name='verified_professionals',
    schema_name='verification'
)

print(f"Success: {result['success']}")
print(f"Insert ID: {result['insert_id']}")
print(f"Table: {result['table']}")
```

**What happens:**
1. Builds INSERT query from data dictionary
2. Uses platform's PostgreSQL connection
3. Executes INSERT with RETURNING id
4. Returns new record ID
5. No Computer Use needed (direct SQL)

### Example 3: Batch Processing

```python
from auto_database_entry import batch_enter_verifications

verification_list = [
    {
        'name': 'Gregory Dutton',
        'company': 'ISB',
        'email': 'gregory.dutton@isb.eco',
        'score': 42.3,
        'status': 'UNCERTAIN'
    },
    {
        'name': 'Test Person',
        'company': 'SCA Technology',
        'email': 'test@scatechnology.ai',
        'score': 0.0,
        'status': 'SUSPICIOUS'
    },
    {
        'name': 'John Smith',
        'company': 'Legitimate Corp',
        'email': 'john@legitimate.com',
        'score': 95.8,
        'status': 'VERIFIED'
    }
]

result = await batch_enter_verifications(
    verification_list=verification_list,
    target_system='crm',
    target_url='https://your-crm.com/contacts/new',
    form_fields={
        'full_name': 'name',
        'company': 'company',
        'email': 'email',
        'legitimacy': 'score',
        'status': 'status'
    }
)

print(f"Total: {result['total_records']}")
print(f"Created: {result['records_created']}")
print(f"Failed: {result['records_failed']}")
print(f"Time: {result['execution_time']}s")
```

**What happens:**
1. Processes each record sequentially
2. 2-second delay between entries (avoid rate limiting)
3. Each entry follows same process as Example 1
4. Returns detailed results for each record
5. Continues even if some records fail

---

## Integration with AI Agent

### Using from Chat

```
User: "I've verified Gregory Dutton from ISB. His legitimacy score is 42.3/100. 
       Can you add him to our CRM?"

Agent: I'll use the auto_enter_verification_results tool to add Gregory to the CRM.

[Calls tool with verification data]

Agent: ✅ Successfully added Gregory Dutton to CRM. Record created in 8.3 seconds.
       Status: UNCERTAIN - flagged for manual review due to low legitimacy score.
       Screenshots captured for audit trail.
```

### Using in Workflows

```python
# In a verification workflow tool
from advanced_analysis_core import analyze_content_with_ai
from auto_database_entry import auto_enter_to_postgres

async def verify_and_store(domain, company_name):
    # Step 1: Verify
    verification = await analyze_content_with_ai(
        content=scrape_result['full_text'],
        domain=domain
    )
    
    # Step 2: Calculate legitimacy
    legitimacy_score = calculate_legitimacy_score(verification)
    
    # Step 3: Auto-store in database
    db_result = await auto_enter_to_postgres(
        verification_data={
            'company_name': company_name,
            'domain': domain,
            'legitimacy_score': legitimacy_score,
            'verification_status': 'UNCERTAIN' if legitimacy_score < 50 else 'VERIFIED',
            'requires_manual_review': legitimacy_score < 50,
            'verification_date': datetime.now().isoformat()
        },
        table_name='verified_professionals',
        schema_name='verification'
    )
    
    return {
        'verification': verification,
        'legitimacy_score': legitimacy_score,
        'database_record_id': db_result.get('insert_id'),
        'stored': db_result['success']
    }
```

---

## Security Considerations

### 1. Credential Handling
**NEVER** hardcode credentials in form data:

```python
# ❌ BAD - Exposes password
verification_data = {
    'username': 'admin',
    'password': 'supersecret123'  # NEVER DO THIS
}

# ✅ GOOD - Use credential injection
# Platform injects credentials securely via _injected_credentials
```

### 2. URL Validation
Always validate target URLs:

```python
# Check URL is from allowed domain
allowed_domains = ['your-crm.com', 'your-company.net']
url_domain = urlparse(target_url).netloc

if url_domain not in allowed_domains:
    return {'success': False, 'error': 'URL not in allowed domains'}
```

### 3. Data Sanitization
Sanitize data before entry:

```python
import bleach

verification_data = {
    'name': bleach.clean(raw_name),  # Remove HTML/JS
    'email': validate_email(raw_email),  # Verify format
    'notes': bleach.clean(raw_notes)[:500]  # Limit length
}
```

### 4. Screenshot Storage
Screenshots contain sensitive data:

```python
# Store screenshots securely
screenshot_path = f"verification_screenshots/{user_id}/{timestamp}.png"

# Encrypt before storage
encrypted = encrypt_screenshot(result['screenshot_after'])
save_secure(screenshot_path, encrypted)

# Auto-delete after 30 days
schedule_deletion(screenshot_path, days=30)
```

---

## Target System Examples

### Salesforce CRM

```python
result = await auto_enter_verification_results(
    verification_data={
        'first_name': 'Gregory',
        'last_name': 'Dutton',
        'account': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'legitimacy_score': '42.3',
        'status': 'Uncertain - Requires Review'
    },
    target_system='crm',
    target_url='https://your-org.lightning.force.com/lightning/o/Contact/new',
    form_fields={
        'FirstName': 'first_name',
        'LastName': 'last_name',
        'Account': 'account',
        'Email': 'email',
        'Legitimacy_Score__c': 'legitimacy_score',
        'Verification_Status__c': 'status'
    }
)
```

### HubSpot

```python
result = await auto_enter_verification_results(
    verification_data={
        'firstname': 'Gregory',
        'lastname': 'Dutton',
        'company': 'ISB',
        'email': 'gregory.dutton@isb.eco',
        'legitimacy_rating': '42.3'
    },
    target_system='crm',
    target_url='https://app.hubspot.com/contacts/YOUR_HUB_ID/contact/create',
    form_fields={
        'firstname': 'firstname',
        'lastname': 'lastname',
        'company': 'company',
        'email': 'email',
        'legitimacy_rating': 'legitimacy_rating'
    }
)
```

### Google Forms

```python
# First, inspect the form to get field entry IDs
# Right-click on form field → Inspect → Find name="entry.123456789"

result = await auto_enter_verification_results(
    verification_data={
        'name': 'Gregory Dutton',
        'company': 'ISB',
        'email': 'gregory.dutton@isb.eco',
        'score': '42.3',
        'status': 'UNCERTAIN'
    },
    target_system='custom',
    target_url='https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform',
    form_fields={
        'entry.123456789': 'name',      # Replace with actual entry IDs
        'entry.987654321': 'company',
        'entry.111222333': 'email',
        'entry.444555666': 'score',
        'entry.777888999': 'status'
    }
)
```

### Airtable

```python
result = await auto_enter_verification_results(
    verification_data={
        'Name': 'Gregory Dutton',
        'Company': 'ISB',
        'Email': 'gregory.dutton@isb.eco',
        'Legitimacy Score': '42.3',
        'Status': 'UNCERTAIN'
    },
    target_system='database',
    target_url='https://airtable.com/YOUR_BASE_ID/YOUR_TABLE_ID',
    form_fields={
        'fldNameField': 'Name',
        'fldCompanyField': 'Company',
        'fldEmailField': 'Email',
        'fldScoreField': 'Legitimacy Score',
        'fldStatusField': 'Status'
    }
)
```

---

## Troubleshooting

### Issue: "Docker not available"

**Symptoms:**
```
Error: Docker not available: [Errno 2] No such file or directory: '/var/run/docker.sock'
```

**Solutions:**
1. Start Docker Desktop
2. Check Docker is running: `docker ps`
3. On Windows, enable "Expose daemon on tcp://localhost:2375"
4. Restart VS Code/terminal after starting Docker

### Issue: "Computer Use executor not available"

**Symptoms:**
```
Error: Computer Use executor not available. Install Docker and check AI_infrastructure.
```

**Solutions:**
1. Check `AI_infrastructure/core/computer_use_executor.py` exists
2. Verify Docker image built: `docker images | grep computer-use`
3. Build image: `cd AI_infrastructure/docker/computer-use && docker build -t computer-use:latest .`

### Issue: "Anthropic API key required"

**Symptoms:**
```
Error: Anthropic API key required for Computer Use
```

**Solutions:**
1. Set environment variable: `$env:ANTHROPIC_API_KEY = "sk-ant-..."`
2. Or add to `.env` file
3. Verify: `echo $env:ANTHROPIC_API_KEY`

### Issue: "Max iterations reached"

**Symptoms:**
```
Error: Max iterations (20) reached without completion
```

**Causes:**
- Form too complex for Claude to navigate
- Page requires login (credentials not provided)
- Form has CAPTCHA or bot detection
- Page JavaScript errors preventing submission

**Solutions:**
1. Check screenshot_after to see where Claude got stuck
2. Simplify form (remove unnecessary fields)
3. Provide login credentials if needed
4. Increase max_iterations parameter
5. Use direct PostgreSQL insert instead

### Issue: "Table does not exist"

**Symptoms:**
```
Error: relation "verification.verified_professionals" does not exist
```

**Solutions:**
Create the table first:

```sql
CREATE SCHEMA IF NOT EXISTS verification;

CREATE TABLE IF NOT EXISTS verification.verified_professionals (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    email VARCHAR(255),
    domain VARCHAR(255),
    legitimacy_score DECIMAL(5,2),
    verification_status VARCHAR(50),
    domain_authority INT,
    web_archive_snapshots INT,
    ssl_certificates INT,
    requires_manual_review BOOLEAN,
    verification_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Performance Metrics

### Computer Use Form Fill

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| Container startup | 3-5 seconds | First time only, reused after |
| Page load | 2-4 seconds | Depends on website |
| Field fill (per field) | 1-2 seconds | Claude locates + fills |
| Form submission | 1-3 seconds | Includes verification |
| Total time (5 fields) | 8-15 seconds | End-to-end |
| Screenshot size | 50-200 KB | Base64 encoded |
| API calls to Claude | 10-20 per form | Iterative process |
| Cost per form | $0.01-$0.05 | Anthropic API usage |

### Direct PostgreSQL Insert

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| INSERT query | 5-50 ms | Local database |
| Total time | <100 ms | Very fast |
| API calls | 0 | Direct SQL |
| Cost | $0 | No API usage |

### Batch Processing (10 records)

| Metric | Computer Use | PostgreSQL |
|--------|--------------|------------|
| Total time | 90-150 seconds | <1 second |
| Time per record | 9-15 seconds | <100 ms |
| Cost | $0.10-$0.50 | $0 |

**Recommendation:** Use PostgreSQL for bulk operations, Computer Use for web forms.

---

## Best Practices

### 1. Choose the Right Tool

```python
# ✅ PostgreSQL for bulk operations
if len(records) > 10:
    for record in records:
        await auto_enter_to_postgres(record, 'table_name')

# ✅ Computer Use for web forms
if target_is_web_form:
    await auto_enter_verification_results(data, 'crm', url, fields)
```

### 2. Error Handling

```python
try:
    result = await auto_enter_verification_results(...)
    
    if not result['success']:
        logger.error(f"Entry failed: {result['error']}")
        
        # Fallback to manual notification
        send_email_to_admin(
            subject="Manual entry required",
            data=verification_data,
            error=result['error']
        )
except Exception as e:
    logger.error(f"Critical error: {e}", exc_info=True)
    # Always have a backup plan
```

### 3. Audit Trail

```python
# Save screenshots for audit
if result['success']:
    save_screenshot(
        result['screenshot_before'],
        f"audit/{user_id}/before_{timestamp}.png"
    )
    save_screenshot(
        result['screenshot_after'],
        f"audit/{user_id}/after_{timestamp}.png"
    )
    
    # Log all actions
    log_verification_entry(
        user_id=user_id,
        verification_data=verification_data,
        actions=result['actions_taken'],
        timestamp=datetime.now()
    )
```

### 4. Rate Limiting

```python
# Add delays for bulk operations
for record in records:
    result = await auto_enter_verification_results(record, ...)
    
    # Respect target system rate limits
    await asyncio.sleep(2)  # 2 seconds between entries
```

---

## Cost Estimation

### Anthropic API Pricing (as of Dec 2025)

- Claude Sonnet 4.5: $3 per million input tokens, $15 per million output tokens
- Computer Use: Additional $0.001 per action
- Average form fill: 5,000 input + 1,000 output tokens + 15 actions

**Cost per form:** ~$0.03-$0.05

### Monthly Cost Estimates

| Usage | Forms/Month | Monthly Cost |
|-------|-------------|--------------|
| Light | 50 | $2-$3 |
| Medium | 500 | $15-$25 |
| Heavy | 5,000 | $150-$250 |
| Enterprise | 50,000 | $1,500-$2,500 |

**ROI Calculation:**
- Manual data entry: 5 minutes per form × $25/hour = $2.08 per form
- Automated entry: $0.03-$0.05 per form
- **Savings: $2.00+ per form (40x cheaper than manual)**

---

## Future Enhancements

### Planned Features

1. **Multi-page forms** - Handle forms spanning multiple pages
2. **CAPTCHA solving** - Integration with CAPTCHA solving services
3. **Authentication handling** - Automatic login to systems
4. **Field mapping AI** - Auto-detect form fields using Claude
5. **Validation checks** - Verify data before submission
6. **Retry logic** - Automatic retry on transient failures
7. **Parallel processing** - Process multiple forms simultaneously
8. **Custom workflows** - Build complex multi-step automation

---

## Support

### Documentation
- Main guide: This file
- API reference: `auto_database_entry.py` docstrings
- Tool definitions: `auto_database_entry_tools.json`
- Computer Use architecture: `AI_infrastructure/COMPUTER_USE_ARCHITECTURE.md`

### Testing
```bash
# Run test suite
cd UI/modules_external/professional-verification/TESTS
python test_auto_database_entry.py
```

### Questions
Contact platform support or file an issue in the repository.

---

**Last Updated:** December 18, 2025  
**Version:** 1.0.0  
**Status:** Production Ready 🚀
