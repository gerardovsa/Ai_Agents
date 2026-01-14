# 🔍 Module Analyzer - Quick Start Guide

**Version:** 1.0.0  
**Last Updated:** November 29, 2025  
**Status:** Production Ready

---

## What is Module Analyzer?

A comprehensive CLI tool that analyzes modules for V3.0 compliance, architecture patterns, integrations, and best practices. AI agents and developers use it to validate modules before deployment.

---

## Quick Usage

```powershell
# Analyze any module
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}

# Examples
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/inhouse-kanban
python UI/modules_internal/docs/module_analyzer.py UI/modules_internal/settings
```

---

## What It Checks (9 Areas)

1. ✅ **File Structure** - manifest, JS, CSS, HTML, docs, backups
2. ✅ **Manifest V3.0 Compliance** - schema validation, required fields
3. ✅ **Architecture Pattern** - Architecture 1 vs 2 detection
4. ✅ **Sidebar Integration** - SidebarManager vs custom
5. ✅ **API Endpoints** - fetch() calls, backend URLs
6. ✅ **UI Rendering** - initialize(), render(), containers
7. ✅ **Connections** - databases, external APIs, WebSockets
8. ✅ **Documentation** - README, guides, coverage
9. ✅ **Best Practices** - error handling, async/await, logging

---

## Compliance Score

**0-100 Score with Status:**
- **80-100:** ✅ EXCELLENT - Production ready
- **60-79:** ⚠️ GOOD - Minor improvements
- **40-59:** ⚠️ NEEDS IMPROVEMENT - Fix issues
- **0-39:** ❌ POOR - Major refactoring required

---

## Output Sections

### 🔴 Critical Issues
**Must fix** for V3.0 compatibility:
- Missing manifest fields (`type`, `category`)
- Invalid JSON syntax
- Broken initialization
- Missing required methods

### ⚠️ Warnings
**Should address** for best practices:
- Old manifest version (2.x)
- Custom sidebar implementation
- Multiple backup files
- Excessive logging

### 💡 Recommendations
**Nice to have** improvements:
- Documentation consolidation
- Architecture optimization
- Performance tweaks
- Code organization

---

## When to Use

### Before Starting Work
```powershell
# Understand current state
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}

# Review issues to plan work
```

### During Development
```powershell
# After each major change
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}

# Verify score increases
```

### Before Deployment
```powershell
# Final validation
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}

# Target: 80+ score, 0 critical issues
```

### For Troubleshooting
```powershell
# When module fails to load
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}

# Check critical issues section
```

---

## AI Agent Prompt Template

```
Analyze the module at UI/modules_external/{module-id}

Run: python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}

Review results and create action plan:
1. Fix critical issues (🔴)
2. Address warnings (⚠️)
3. Implement recommendations (💡)

Target: 80+ compliance score
```

---

## Example Output

```
================================================================================
V3.0 COMPLIANCE SCORE: 75/100 - ⚠️ GOOD
================================================================================

🔴 CRITICAL ISSUES (2):
   - V3.0 missing required fields: type, category
   - capabilities structure needs V3.0 update

⚠️ WARNINGS (2):
   - Manifest is 2.x, should be V3.0
   - Sidebar uses custom implementation

💡 RECOMMENDATIONS (3):
   - Upgrade manifest to V3.0 schema
   - Migrate to SidebarManager framework
   - Consolidate 14 documentation files

================================================================================
SUMMARY
================================================================================
Manifest Version: 2.x
Architecture: Architecture 2 (Inline HTML-in-JS)
API Endpoints: 8
Sidebar: CUSTOM
Documentation: 14 files
================================================================================

Results saved to: analysis_results.json
```

---

## Results File

Analyzer saves detailed results to `analysis_results.json` in the module folder:

```json
{
  "module_name": "inhouse-kanban",
  "timestamp": "2025-11-29T14:30:45",
  "compliance_score": 75,
  "checks": {
    "file_structure": { "status": "PASS" },
    "manifest_compliance": { "status": "FAIL", "version": "2.x" },
    "architecture_pattern": { "architecture": "Architecture 2", "confidence": 90 },
    "sidebar_integration": { "status": "CUSTOM" },
    "api_endpoints": { "total_endpoints": 8 },
    "ui_rendering": { "status": "PASS" },
    "connections": { "databases": ["Supabase"] },
    "documentation": { "total_docs": 14 },
    "best_practices": { "good_practices": 4, "issues": 2 }
  },
  "issues": ["V3.0 missing required fields: type, category"],
  "warnings": ["Manifest is 2.x", "Custom sidebar implementation"],
  "recommendations": ["Upgrade to V3.0", "Use SidebarManager"]
}
```

---

## Exit Codes (for CI/CD)

- **0:** Score ≥70 (Success)
- **1:** Score 40-69 (Warning)
- **2:** Score <40 (Error)

```powershell
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/{module-id}
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Module passed"
} else {
    Write-Host "❌ Module failed"
}
```

---

## Integration with Workflows

### Module Creation
```powershell
# Step 1: Create module files
# Step 2: Run analyzer
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/new-module

# Step 3: Fix issues based on report
# Step 4: Re-run analyzer until score 80+
```

### Module Migration (V2 → V3)
```powershell
# Step 1: Analyze current state
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/old-module

# Step 2: Update manifest to V3.0
# Step 3: Re-run analyzer
# Step 4: Migrate sidebar to SidebarManager
# Step 5: Final analyzer run (target: 80+)
```

### Module Troubleshooting
```powershell
# Step 1: Module not loading? Run analyzer
python UI/modules_internal/docs/module_analyzer.py UI/modules_external/broken-module

# Step 2: Check critical issues
# Step 3: Fix issues one by one
# Step 4: Re-run after each fix
```

---

## Related Documentation

- **MODULE_SYSTEM_ARCHITECTURE_V3.md** - Complete V3.0 architecture guide
- **MODULE_MANIFEST_SCHEMA_V3.md** - Manifest schema reference
- **SIDEBAR_FRAMEWORK_GUIDE.md** - SidebarManager implementation
- **Module Architect.prompt.md** - AI agent module creation guide

---

## Tips for Best Results

1. **Run Early, Run Often** - Catch issues before they compound
2. **Target 80+ Score** - Minimum for production deployment
3. **Fix Critical Issues First** - Highest impact on functionality
4. **Address Warnings** - Improve code quality and maintainability
5. **Consider Recommendations** - Optional but valuable improvements
6. **Save Results** - Commit `analysis_results.json` to Git
7. **Track Progress** - Compare scores over time

---

**Tool Location:** `UI/modules_internal/docs/module_analyzer.py`  
**Maintained By:** AI Agents Platform Team  
**Last Updated:** November 29, 2025
