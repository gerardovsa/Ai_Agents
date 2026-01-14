# Google Apps Script Integration Guide

**Status**: ✅ Production Ready  
**Tools**: 14 tools (Tier 1: 3, Tier 2: 6, Tier 3: 5 Smart Tools)  
**Authentication**: OAuth 2.0 (NOT service accounts)  
**Rate Limit**: 60 requests/minute  
**API Version**: v1

---

## 🎯 Overview

Google Apps Script is Google's cloud-based JavaScript platform for extending Google Workspace. This integration enables AI agents to:

- **Read script source code** - Diagnose bugs by viewing actual implementation
- **Execute functions remotely** - Test fixes and trigger automation
- **Debug failing scripts** - Comprehensive error analysis and diagnostics
- **Auto-fix common issues** - Automatic repair of OAuth scopes, deprecated APIs
- **Manage deployments** - Deploy as API executables or web apps
- **Version control** - Create snapshots, rollback to previous versions
- **Backup & restore** - Full project export and disaster recovery

---

## 🚀 Quick Start

### 1. Authentication Setup

**CRITICAL**: Apps Script API does NOT work with service accounts. Must use OAuth 2.0.

**🚨 IMPORTANT**: If you see `access_token required` errors, your OAuth app needs Apps Script scopes!

📖 **Complete Setup Guide**: See [`GOOGLE_APPS_SCRIPT_OAUTH_SETUP.md`](./GOOGLE_APPS_SCRIPT_OAUTH_SETUP.md) for detailed instructions.

**Quick Steps**:

1. **Enable Apps Script API**:
   - Go to https://console.cloud.google.com/
   - APIs & Services → Library → Search "Google Apps Script API" → Enable

2. **Add Required Scopes** to OAuth Consent Screen:
   ```
   https://www.googleapis.com/auth/script.projects       ← Read/write scripts
   https://www.googleapis.com/auth/script.processes      ← View execution logs
   https://www.googleapis.com/auth/script.deployments    ← Manage deployments
   ```

3. **Re-authenticate** to get new token with Apps Script scopes:
   ```
   http://localhost:5001/api/auth/google/login
   ```

4. **Verify** token includes Apps Script scopes:
   ```sql
   SELECT scopes FROM oauth_tokens WHERE platform = 'google';
   -- Should include "script.projects"
   ```

### 2. Usage Example

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Step 1: Find your script (need script ID)
# Note: Apps Script API doesn't have "list all" - use Drive API or provide ID
script_id = "1a2b3c4d5e6f7g8h9i0j"  # From script URL

# Step 2: Read script code
result = registry.execute_tool(
    tool_name="google_apps_script_get_content",
    script_id=script_id,
    _user_id=1,
    _injected_credentials=True
)

print(f"Files: {len(result['files'])}")
print(f"OAuth Scopes: {result['manifest']['oauthScopes']}")

# Step 3: Check execution history for errors
processes = registry.execute_tool(
    tool_name="google_apps_script_list_processes",
    script_id=script_id,
    page_size=20,
    _user_id=1,
    _injected_credentials=True
)

# Step 4: Run comprehensive debugging
debug_result = registry.execute_tool(
    tool_name="google_apps_script_debug_script",
    script_id=script_id,
    _user_id=1,
    _injected_credentials=True
)

print(debug_result['diagnosticReport'])
print("Recommended actions:", debug_result['recommendedActions'])
```

---

## 📋 Tool Tiers

### **Tier 1: Basic Operations (3 tools)**

#### `google_apps_script_list_projects`
**Purpose**: Discover available scripts  
**Use Case**: Find script by name before debugging  
**Note**: API limitation - no native "list all" endpoint. Use Drive API to search or provide known script IDs.

**Example**:
```python
# Current implementation returns structure for manual script discovery
result = registry.execute_tool("google_apps_script_list_projects", _user_id=1)
```

#### `google_apps_script_get_content`
**Purpose**: Read all source code files  
**Use Case**: Essential for debugging - see what script actually does  
**Returns**: .gs files, .html files, appsscript.json manifest

**Example**:
```python
content = registry.execute_tool(
    "google_apps_script_get_content",
    script_id="abc123...",
    _user_id=1
)

for file in content['files']:
    print(f"{file['name']}.{file['type']}: {len(file['source'])} chars")
```

#### `google_apps_script_update_content`
**Purpose**: Modify script code (fix bugs!)  
**Use Case**: Apply fixes after diagnosis  
**Critical**: Must include ALL files, not just changed ones

**Example**:
```python
# Get current content first
content = registry.execute_tool("google_apps_script_get_content", script_id="abc123", _user_id=1)

# Modify specific file
files = content['files']
for file in files:
    if file['name'] == 'Code':
        file['source'] = file['source'].replace('old_code', 'fixed_code')

# Update with ALL files
result = registry.execute_tool(
    "google_apps_script_update_content",
    script_id="abc123",
    files=files,
    _user_id=1
)
```

### **Tier 2: Advanced (6 tools)**

#### `google_apps_script_run_function`
**Purpose**: Execute script functions remotely  
**Use Case**: Test fixes, trigger automation  
**Requirement**: Script must be deployed as API executable

**Example**:
```python
result = registry.execute_tool(
    "google_apps_script_run_function",
    script_id="abc123",
    function_name="processData",
    parameters=["testInput", 123],
    dev_mode=True,  # Use latest saved code (owner only)
    _user_id=1
)

print(f"Result: {result['result']}")
print(f"Execution time: {result['execution_time_ms']}ms")
```

#### `google_apps_script_list_processes`
**Purpose**: View execution history and errors  
**Use Case**: See what failed and when

**Example**:
```python
processes = registry.execute_tool(
    "google_apps_script_list_processes",
    script_id="abc123",
    page_size=50,
    _user_id=1
)

failed = [p for p in processes['processes'] if p['processStatus'] == 'FAILED']
print(f"Failures: {len(failed)} out of {len(processes['processes'])}")
```

#### `google_apps_script_create_deployment`
**Purpose**: Deploy as API executable or web app  
**Use Case**: Required for run_function to work

**Example**:
```python
deployment = registry.execute_tool(
    "google_apps_script_create_deployment",
    script_id="abc123",
    description="Production deployment v2.0",
    _user_id=1
)

print(f"Deployment ID: {deployment['deploymentId']}")
```

#### `google_apps_script_create_version`
**Purpose**: Create immutable snapshot  
**Use Case**: Before production deployment

**Example**:
```python
version = registry.execute_tool(
    "google_apps_script_create_version",
    script_id="abc123",
    description="Fixed permission error",
    _user_id=1
)

print(f"Created version {version['versionNumber']}")
```

#### `google_apps_script_list_versions`
**Purpose**: View version history  
**Use Case**: Find version to rollback to

#### `google_apps_script_get_metrics`
**Purpose**: Usage statistics  
**Use Case**: Monitor script health

### **Tier 3: Smart Multi-Step Tools (5 tools)**

These tools combine multiple operations for complex workflows.

#### `google_apps_script_analyze_errors` 🧠
**What it does**: Parses error messages, groups by type, suggests fixes  
**Combines**: Error parsing + pattern detection + fix recommendations

**Example**:
```python
# Get processes first
processes = registry.execute_tool("google_apps_script_list_processes", script_id="abc123", _user_id=1)

# Analyze errors
analysis = registry.execute_tool(
    "google_apps_script_analyze_errors",
    processes=processes['processes'],
    _user_id=1
)

print("Error patterns:", analysis['errorPatterns'])
print("Root causes:", analysis['rootCauses'])
print("Suggested fixes:", analysis['suggestedFixes'])
```

**Output Example**:
```json
{
  "errorPatterns": [
    {"type": "permission", "count": 12, "sample_message": "DriveApp.getFileById permission denied"}
  ],
  "rootCauses": ["Missing Drive API scope in manifest (12 occurrences)"],
  "suggestedFixes": [
    "Add https://www.googleapis.com/auth/drive to oauthScopes",
    "Enable Drive API in Google Cloud Console"
  ],
  "affectedFunctions": ["extractFiles", "processFolder"]
}
```

#### `google_apps_script_debug_script` 🧠
**What it does**: Complete debugging workflow  
**Combines**: get_content + list_processes + analyze_errors + code review

**Example**:
```python
# One-call comprehensive debugging
debug = registry.execute_tool(
    "google_apps_script_debug_script",
    script_id="abc123",
    include_code_review=True,
    _user_id=1
)

print(debug['diagnosticReport'])
# === Diagnostic Report for Script abc123 ===
# Files: 3
# Recent Executions: 45
# Failures: 12 (45 total)
# Root Causes:
#   - Missing Drive API scope in manifest (12 occurrences)
# Code Quality Issues:
#   - Missing error handling (no try-catch blocks)

print("Actions:", debug['recommendedActions'])
# ["Add drive.readonly scope to manifest", "Add try-catch error handling"]
```

#### `google_apps_script_fix_common_issues` 🧠
**What it does**: Auto-detect and fix common problems  
**Combines**: Code analysis + automatic fixes + change tracking

**Fixes**:
- Missing OAuth scopes (detects API usage, adds required scopes)
- Deprecated API calls (identifies old methods)
- Missing error handling (detects lack of try-catch)
- Hardcoded credentials (warns about security issues)

**Example**:
```python
fixes = registry.execute_tool(
    "google_apps_script_fix_common_issues",
    script_id="abc123",
    fix_types=["oauth_scopes", "deprecated_apis"],
    auto_apply=False,  # Review before applying
    _user_id=1
)

print(f"Fixes found: {fixes['fixesApplied']}")
print(f"Manual review needed: {fixes['requiresManualReview']}")

# If satisfied, apply:
fixes = registry.execute_tool(
    "google_apps_script_fix_common_issues",
    script_id="abc123",
    auto_apply=True,
    _user_id=1
)
```

#### `google_apps_script_backup_project` 🧠
**What it does**: Full project export  
**Combines**: get_content + list_versions + list_processes

**Example**:
```python
backup = registry.execute_tool(
    "google_apps_script_backup_project",
    script_id="abc123",
    include_versions=True,
    include_executions=True,
    _user_id=1
)

# Save backup
import json
with open(f"backup_{backup['exportTimestamp']}.json", 'w') as f:
    json.dump(backup['backupData'], f, indent=2)

print(f"Backed up {backup['metadata']['files']} files, {backup['metadata']['versions']} versions")
```

#### `google_apps_script_restore_version` 🧠
**What it does**: Rollback to previous version  
**Combines**: backup_project + get_content(version) + update_content + create_deployment

**Example**:
```python
restore = registry.execute_tool(
    "google_apps_script_restore_version",
    script_id="abc123",
    version_number=3,  # Rollback to version 3
    create_backup=True,  # Backup current state first
    redeploy=True,  # Deploy after restoring
    _user_id=1
)

print(f"Restored to version {restore['restoredVersion']}")
print(f"Backup created: {restore['backupCreated']}")
print(f"Deployment: {restore['deploymentStatus']}")
```

---

## 💡 Common Workflows

### Workflow 1: Debug Failing Script

```python
# User: "My Northecote File Extractor script is failing"

# Step 1: Comprehensive debugging
debug = registry.execute_tool(
    "google_apps_script_debug_script",
    script_id="1a2b3c4d5e6f",
    _user_id=1
)

# Step 2: Review diagnostic report
print(debug['diagnosticReport'])
# Identifies: Missing Drive API scope

# Step 3: Auto-fix
fixes = registry.execute_tool(
    "google_apps_script_fix_common_issues",
    script_id="1a2b3c4d5e6f",
    fix_types=["oauth_scopes"],
    auto_apply=True,
    _user_id=1
)

# Step 4: Test fix
test = registry.execute_tool(
    "google_apps_script_run_function",
    script_id="1a2b3c4d5e6f",
    function_name="extractFiles",
    dev_mode=True,
    _user_id=1
)

print("✅ Script fixed and tested successfully!")
```

### Workflow 2: Update Script Code

```python
# Step 1: Read current code
content = registry.execute_tool(
    "google_apps_script_get_content",
    script_id="abc123",
    _user_id=1
)

# Step 2: Modify code
files = content['files']
for file in files:
    if file['name'] == 'Code' and file['type'] == 'SERVER_JS':
        # Add error handling
        file['source'] = file['source'].replace(
            'function processData() {',
            'function processData() {\n  try {'
        )
        file['source'] += '\n  } catch (e) {\n    Logger.log("Error: " + e);\n  }\n}'

# Step 3: Update
result = registry.execute_tool(
    "google_apps_script_update_content",
    script_id="abc123",
    files=files,
    _user_id=1
)

# Step 4: Create version
version = registry.execute_tool(
    "google_apps_script_create_version",
    script_id="abc123",
    description="Added error handling",
    _user_id=1
)

# Step 5: Deploy
deployment = registry.execute_tool(
    "google_apps_script_create_deployment",
    script_id="abc123",
    version_number=version['versionNumber'],
    _user_id=1
)

print(f"✅ Updated, versioned (v{version['versionNumber']}), and deployed")
```

### Workflow 3: Backup Before Major Changes

```python
# Step 1: Create backup
backup = registry.execute_tool(
    "google_apps_script_backup_project",
    script_id="abc123",
    _user_id=1
)

# Save backup file
import json
with open(f"backup_before_refactor.json", 'w') as f:
    json.dump(backup['backupData'], f, indent=2)

# Step 2: Make changes
# ... (update code) ...

# Step 3: If something breaks, restore
restore = registry.execute_tool(
    "google_apps_script_restore_version",
    script_id="abc123",
    version_number=5,  # Previous working version
    _user_id=1
)
```

---

## 🔍 Error Handling

### Common Errors

**401 Unauthorized**
- **Cause**: OAuth token expired or invalid
- **Solution**: Re-authenticate user, refresh access token

**403 Forbidden**
- **Cause**: Missing required OAuth scope
- **Solution**: Add scope to OAuth consent screen, re-authorize

**404 Not Found**
- **Cause**: Invalid script_id or script deleted
- **Solution**: Verify script_id, check script still exists in Drive

**429 Rate Limit**
- **Cause**: Exceeded 60 requests/minute
- **Solution**: Automatic retry with backoff (handled by implementation)

**Execution Timeout**
- **Cause**: Function exceeded 6-minute limit
- **Solution**: Optimize code, break into smaller operations

### Debugging Tips

1. **Always read code first**: `get_content` before making changes
2. **Check manifest for scopes**: Permission errors often = missing scope
3. **Use debug_script for comprehensive analysis**: One-call diagnostics
4. **Test in dev_mode first**: Safer than deploying untested code
5. **Create versions before deploying**: Easy rollback if needed

---

## 📊 Rate Limits

- **Requests**: 60 per minute
- **Execution time**: 6 minutes max per function
- **Automatic retry**: Implemented with exponential backoff

---

## 🔒 Security Notes

- **OAuth 2.0 only**: Service accounts NOT supported
- **User consent required**: Scripts need user authorization
- **Scope validation**: Ensure minimal necessary scopes
- **Credential storage**: Never hardcode keys - use PropertiesService
- **Audit trail**: All operations logged with user_id

---

## 📚 Additional Resources

- **Official API Docs**: https://developers.google.com/apps-script/api
- **OAuth Setup Guide**: https://developers.google.com/apps-script/guides/cloud-platform-projects
- **API Reference**: https://developers.google.com/apps-script/api/reference/rest
- **Quotas**: https://developers.google.com/apps-script/guides/services/quotas

---

**Last Updated**: November 29, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready with Smart Tools
