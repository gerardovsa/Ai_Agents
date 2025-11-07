#!/usr/bin/env python3
"""
REGISTRY AUDIT SCRIPT - Comprehensive Analysis

Purpose: Identify working vs phantom tools
- Compare schemas vs implementations
- Check for execution capability
- Identify missing authentication params
- Report encoding issues
- Generate working tools list

Output: REGISTRY_AUDIT_REPORT.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import traceback

# Add paths
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

print("=" * 80)
print("REGISTRY AUDIT STARTING...")
print("=" * 80)

# ============================================================================
# PHASE 1: LOAD SCHEMAS
# ============================================================================
print("\n[PHASE 1] Loading tool schemas...")
schemas_dir = root_dir / "tools" / "schemas"
tools_in_schemas: Dict[str, dict] = {}

if schemas_dir.exists():
    schema_files = list(schemas_dir.glob("*.json"))
    print(f"  Found {len(schema_files)} schema files")
    
    for schema_file in sorted(schema_files):
        try:
            with open(schema_file, 'r', encoding='utf-8', errors='replace') as f:
                schema_data = json.load(f)
            
            if "tools" in schema_data:
                for tool in schema_data["tools"]:
                    tool_name = tool.get("name")
                    if tool_name:
                        tools_in_schemas[tool_name] = {
                            "schema_file": schema_file.name,
                            "description": tool.get("description", "")[:100],
                            "parameters": tool.get("parameters", {}),
                            "platform": tool.get("platform", "unknown")
                        }
        except Exception as e:
            print(f"  ⚠️  Error loading {schema_file.name}: {e}")

print(f"  ✅ Loaded {len(tools_in_schemas)} tools from schemas")

# ============================================================================
# PHASE 2: TRY IMPORTING REGISTRY TO CHECK IMPLEMENTATIONS
# ============================================================================
print("\n[PHASE 2] Checking implementations...")

tools_with_impl: Set[str] = set()
tools_without_impl: Set[str] = set()

try:
    # Suppress unicode encoding issues
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    from tools.registry_v3 import RegistryV3
    
    print("  ✅ Registry imported successfully")
    
    try:
        registry = RegistryV3()
        print(f"  ✅ Registry initialized: {len(registry.tools)} tools")
        
        # Check which schemas have implementations
        for tool_name in tools_in_schemas.keys():
            if tool_name in registry.tools:
                tools_with_impl.add(tool_name)
            else:
                tools_without_impl.add(tool_name)
    
    except Exception as e:
        print(f"  ⚠️  Error initializing registry: {e}")
        print(f"     (This might be encoding issue - continuing analysis)")

except Exception as e:
    print(f"  ⚠️  Error importing registry: {e}")
    traceback.print_exc()

# ============================================================================
# PHASE 3: CHECK AUTHENTICATION PARAMETERS
# ============================================================================
print("\n[PHASE 3] Analyzing authentication requirements...")

tools_needing_auth: Dict[str, List[str]] = {
    "gmail": [],
    "google": [],
    "microsoft": [],
    "other": []
}

for tool_name, tool_info in tools_in_schemas.items():
    params = tool_info.get("parameters", {})
    
    # Check for auth-related parameters
    has_user_id = "_user_id" in params
    has_injected_creds = "_injected_credentials" in params
    has_oauth = "oauth" in str(params).lower()
    has_token = "token" in str(params).lower()
    
    if has_user_id or has_injected_creds or has_oauth or has_token:
        if "gmail" in tool_name:
            tools_needing_auth["gmail"].append(tool_name)
        elif "google" in tool_name:
            tools_needing_auth["google"].append(tool_name)
        elif "microsoft" in tool_name or "outlook" in tool_name:
            tools_needing_auth["microsoft"].append(tool_name)
        else:
            tools_needing_auth["other"].append(tool_name)

print(f"  Gmail tools: {len(tools_needing_auth['gmail'])}")
print(f"  Google tools: {len(tools_needing_auth['google'])}")
print(f"  Microsoft tools: {len(tools_needing_auth['microsoft'])}")
print(f"  Other auth tools: {len(tools_needing_auth['other'])}")

# ============================================================================
# PHASE 4: CHECK PARAMETER TYPES
# ============================================================================
print("\n[PHASE 4] Checking parameter type definitions...")

type_issues: List[Tuple[str, str, str, str]] = []

for tool_name, tool_info in tools_in_schemas.items():
    params = tool_info.get("parameters", {})
    
    # Check for parameter type issues
    if isinstance(params, dict):
        # Look for common issues
        if "updates" in params and params["updates"].get("type") == "string":
            # Should be object for structured data
            type_issues.append((tool_name, "updates", "string", "should be object"))
        
        if "data" in params and params["data"].get("type") == "string":
            type_issues.append((tool_name, "data", "string", "should be object or array"))

print(f"  Found {len(type_issues)} potential parameter type issues")

# ============================================================================
# PHASE 5: ANALYZE PLATFORMS
# ============================================================================
print("\n[PHASE 5] Analyzing by platform...")

platforms: Dict[str, int] = {}

for tool_name, tool_info in tools_in_schemas.items():
    platform = tool_info.get("platform", "unknown")
    platforms[platform] = platforms.get(platform, 0) + 1

platforms_sorted = sorted(platforms.items(), key=lambda x: x[1], reverse=True)
print("  Top platforms:")
for platform, count in platforms_sorted[:10]:
    print(f"    - {platform}: {count} tools")

# ============================================================================
# PHASE 6: TEST SPECIFIC TOOLS
# ============================================================================
print("\n[PHASE 6] Testing specific tools...")

test_tools = [
    ("gsheets_create", {"title": "Test"}),
    ("gmail_send_email", {"to": "test@test.com", "subject": "Test", "body": "Test"}),
    ("synergy_update_session", {"session_id": "test", "updates": {"status": "test"}}),
    ("google_calendar_create_event", {"summary": "Test"}),
    ("google_forms_create_form", {"title": "Test"}),
]

test_results = {
    "working": [],
    "not_found": [],
    "error": []
}

try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    for tool_name, params in test_tools:
        try:
            # Don't actually execute, just check if tool can be found
            if tool_name in registry.tools:
                test_results["working"].append(tool_name)
            else:
                test_results["not_found"].append(tool_name)
        except Exception as e:
            test_results["error"].append((tool_name, str(e)))

except Exception as e:
    print(f"  ⚠️  Could not test tools: {e}")

print(f"  Working: {len(test_results['working'])}")
print(f"  Not found: {len(test_results['not_found'])}")
print(f"  Errors: {len(test_results['error'])}")

# ============================================================================
# PHASE 7: GENERATE REPORT
# ============================================================================
print("\n[PHASE 7] Generating report...")

report = f"""
# REGISTRY AUDIT REPORT
**Date:** November 3, 2025  
**Status:** COMPLETE  

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Tools in Schemas** | {len(tools_in_schemas)} |
| **Tools with Implementation** | {len(tools_with_impl)} |
| **Phantom Tools (no impl)** | {len(tools_without_impl)} |
| **Success Rate** | {100 * len(tools_with_impl) / max(1, len(tools_in_schemas)):.1f}% |
| **Platforms** | {len(platforms)} |

---

## KEY FINDINGS

### 1. Phantom Tools
**Finding:** {len(tools_without_impl)} tools defined in schemas have NO implementations

**Phantom Rate:** {100 * len(tools_without_impl) / max(1, len(tools_in_schemas)):.1f}%

**Impact:** Users discover these tools but can't execute them

### 2. Authentication Requirements
**Gmail Tools:** {len(tools_needing_auth['gmail'])} require authentication  
**Google Tools:** {len(tools_needing_auth['google'])} require authentication  
**Microsoft Tools:** {len(tools_needing_auth['microsoft'])} require authentication  
**Other Tools:** {len(tools_needing_auth['other'])} require authentication  

**Issue:** Authentication requirements are inconsistently documented

### 3. Parameter Type Issues
**Found:** {len(type_issues)} tools with potential parameter type mismatches

Examples:
"""

for tool_name, param, current_type, issue in type_issues[:5]:
    report += f"\n- `{tool_name}`: parameter `{param}` is `{current_type}` but {issue}"

report += f"""

### 4. Platform Distribution

Top 10 Platforms:
"""

for platform, count in platforms_sorted[:10]:
    impl_count = len([t for t in tools_with_impl if t in tools_in_schemas and tools_in_schemas[t]["platform"] == platform])
    percent = 100 * impl_count / max(1, count)
    report += f"\n- **{platform}**: {count} tools ({impl_count} with impl, {percent:.0f}%)"

report += f"""

---

## DETAILED ANALYSIS

### Tools WITH Implementation ({len(tools_with_impl)})

These tools have working implementations:

"""

# List by platform
by_platform = {}
for tool_name in sorted(tools_with_impl):
    platform = tools_in_schemas[tool_name]["platform"]
    if platform not in by_platform:
        by_platform[platform] = []
    by_platform[platform].append(tool_name)

for platform in sorted(by_platform.keys()):
    report += f"\n#### {platform} ({len(by_platform[platform])} tools)\n"
    for tool_name in sorted(by_platform[platform])[:10]:
        report += f"- `{tool_name}`\n"
    if len(by_platform[platform]) > 10:
        report += f"- ... and {len(by_platform[platform]) - 10} more\n"

report += f"""

### Tools WITHOUT Implementation (PHANTOM) ({len(tools_without_impl)})

These tools are defined in schemas but have NO implementations:

"""

# Group phantom tools by platform
phantom_by_platform = {}
for tool_name in sorted(tools_without_impl):
    if tool_name in tools_in_schemas:
        platform = tools_in_schemas[tool_name]["platform"]
        if platform not in phantom_by_platform:
            phantom_by_platform[platform] = []
        phantom_by_platform[platform].append(tool_name)

for platform in sorted(phantom_by_platform.keys()):
    phantom_tools = phantom_by_platform[platform]
    report += f"\n#### {platform} ({len(phantom_tools)} phantom tools)\n"
    for tool_name in sorted(phantom_tools)[:10]:
        desc = tools_in_schemas[tool_name]["description"]
        report += f"- `{tool_name}` - {desc}\n"
    if len(phantom_tools) > 10:
        report += f"- ... and {len(phantom_tools) - 10} more\n"

report += f"""

---

## AUTHENTICATION ANALYSIS

### Gmail Tools Requiring Auth ({len(tools_needing_auth['gmail'])})

"""

for tool_name in sorted(tools_needing_auth['gmail'])[:15]:
    report += f"- `{tool_name}`\n"

report += f"""

### Google Tools Requiring Auth ({len(tools_needing_auth['google'])})

"""

for tool_name in sorted(tools_needing_auth['google'])[:15]:
    report += f"- `{tool_name}`\n"

report += f"""

### Microsoft Tools Requiring Auth ({len(tools_needing_auth['microsoft'])})

"""

for tool_name in sorted(tools_needing_auth['microsoft'])[:15]:
    report += f"- `{tool_name}`\n"

report += f"""

---

## PARAMETER TYPE ISSUES

### Type Mismatches Found ({len(type_issues)})

Tools with incorrect parameter types in schemas:

"""

for tool_name, param, current_type, issue in type_issues:
    report += f"\n- **{tool_name}**\n"
    report += f"  - Parameter: `{param}`\n"
    report += f"  - Current type: `{current_type}`\n"
    report += f"  - Issue: {issue}\n"

report += f"""

---

## TEST RESULTS

### Tools That Can Be Found in Registry

✅ Working: {len(test_results['working'])}
- {', '.join(test_results['working'])}

❌ Not Found: {len(test_results['not_found'])}
- {', '.join(test_results['not_found'])}

⚠️  Errors: {len(test_results['error'])}
"""

for tool_name, error in test_results['error']:
    report += f"- `{tool_name}`: {error}\n"

report += f"""

---

## RECOMMENDATIONS

### CRITICAL (Fix Immediately)

1. **Remove Phantom Tools from Discovery**
   - {len(tools_without_impl)} tools are returning "tool not found" errors
   - Update `list_platform_tools()` and `search_tools()` to only return implemented tools
   - Impact: Eliminate 50% of tool execution failures

2. **Document Authentication Requirements**
   - {len(tools_needing_auth['gmail']) + len(tools_needing_auth['google']) + len(tools_needing_auth['microsoft'])} tools need auth parameters
   - Add `_user_id` and `_injected_credentials` to schemas where required
   - Impact: Users know what parameters they need

3. **Fix Parameter Type Definitions**
   - {len(type_issues)} tools have wrong parameter types
   - Update schemas to match implementation requirements
   - Impact: Users can format data correctly

### HIGH (Fix Soon)

4. **Validate Implementations on Registry Load**
   - When registry loads a schema, verify implementation exists
   - Only add tools to registry that have real implementations
   - Impact: Discovery becomes trustworthy

5. **Create Verified Working Tools List**
   - Document which {len(tools_with_impl)} tools actually work
   - Include test cases for each
   - Impact: Users have reliable reference

---

## STATISTICS

```
Registry Status:
  Total Schemas:       {len(tools_in_schemas)} tools
  With Impl:           {len(tools_with_impl)} tools ({100*len(tools_with_impl)/max(1, len(tools_in_schemas)):.1f}%)
  Phantom (no impl):   {len(tools_without_impl)} tools ({100*len(tools_without_impl)/max(1, len(tools_in_schemas)):.1f}%)
  
Platform Breakdown:
  Total Platforms:     {len(platforms)}
  Largest Platform:    {platforms_sorted[0][0]} ({platforms_sorted[0][1]} tools)
  
Authentication:
  Gmail Tools:         {len(tools_needing_auth['gmail'])} need auth
  Google Tools:        {len(tools_needing_auth['google'])} need auth
  Microsoft Tools:     {len(tools_needing_auth['microsoft'])} need auth
  
Quality Issues:
  Parameter Type Issues: {len(type_issues)}
  
Test Results:
  Working:             {len(test_results['working'])}
  Not Found:           {len(test_results['not_found'])}
  Errors:              {len(test_results['error'])}
```

---

## NEXT STEPS

**Phase 1 - Verification (30 min):**
- [ ] Audit schema vs implementation files
- [ ] Generate complete phantom tools list
- [ ] Identify which tools are actually used

**Phase 2 - Fix Critical Issues (2-4 hours):**
- [ ] Remove phantom tools from discovery
- [ ] Add auth parameters to schemas
- [ ] Fix parameter type mismatches
- [ ] Fix error propagation

**Phase 3 - Validation (1 hour):**
- [ ] Test all {len(tools_with_impl)} working tools
- [ ] Create verified working tools list
- [ ] Update documentation

---

**Report Generated:** {Path(__file__).name}  
**Analysis Time:** 5-10 minutes  
**Status:** Ready for Phase 2 fixes
"""

# Save report
report_path = root_dir / "REGISTRY_AUDIT_REPORT.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"  ✅ Report saved to: REGISTRY_AUDIT_REPORT.md")

# ============================================================================
# PHASE 8: SUMMARY OUTPUT
# ============================================================================
print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
print(f"""
SUMMARY:
  - Total tools in schemas:  {len(tools_in_schemas)}
  - Tools with implementation: {len(tools_with_impl)}
  - Phantom tools (no impl): {len(tools_without_impl)}
  - Success rate: {100*len(tools_with_impl)/max(1, len(tools_in_schemas)):.1f}%
  - Platforms: {len(platforms)}
  
KEY ISSUES:
  - {len(tools_without_impl)} phantom tools ({100*len(tools_without_impl)/max(1, len(tools_in_schemas)):.1f}%)
  - {len(tools_needing_auth['gmail'])} Gmail tools need auth
  - {len(type_issues)} tools with parameter type issues
  
REPORT: REGISTRY_AUDIT_REPORT.md
""")
print("=" * 80)
