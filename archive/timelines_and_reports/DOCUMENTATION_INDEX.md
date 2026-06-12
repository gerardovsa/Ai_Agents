# Documentation Index - AI Agents Project

**Last Updated:** December 12, 2025  
**Project:** AI Agents Infrastructure V10  
**Status:** Production

---

## 📚 Core Documentation

### Calculator System
**Location:** [`CALCULATOR_SYSTEM_DOCUMENTATION.md`](./CALCULATOR_SYSTEM_DOCUMENTATION.md)  
**Status:** ✅ Production - 35/35 Calculators Working (100%)  
**Contents:**
- Complete system architecture
- All 35 calculator specifications
- Testing & verification guide
- Deployment procedures
- Dashboard usage
- Troubleshooting
- API reference

**Quick Links:**
- Calculator Dashboard: `file:///C:/Users/gpoli/GIT/AI_agents/calculator_test_dashboard.html`
- Test Suite: `UI/modules_external/quote-calculator/tests/test_all_calculators.py`
- Schema: `tools/schemas/calculator_tools.json`

---

## 🗂️ Archived Documentation

### Historical Calculator Documentation
**Location:** [`archive/calculator_history/`](./archive/calculator_history/)  
**Contents:**
- `CALCULATOR_100_PERCENT_SUCCESS_DEC11.md` - Final testing results achieving 100% success
- `CALCULATOR_DASHBOARD_GUIDE.md` - Original dashboard usage guide
- `CALCULATOR_SHORT_DESCRIPTIONS_GUIDE.md` - Guide for semantic search optimization
- `VINYL_STICKERS_CALCULATOR_SPECIFICATION.md` - Detailed vinyl sticker calculator spec

**Purpose:** Historical reference for major milestones and detailed specifications

### Original Work Quote Documentation
**Location:** [`archive/documentation/`](./archive/documentation/)  
**Contents:**
- Historical work quote analysis and implementations
- Xero quote automation tools
- Early calculator specifications

---

## 🧪 Testing Documentation

### Current Test Suite
**Location:** `UI/modules_external/quote-calculator/tests/test_all_calculators.py`  
**Status:** All tests passing (35/35)  
**Last Run:** December 11, 2025  
**Coverage:** 100% of production calculators

### Test Dashboard
**Location:** `calculator_test_dashboard.html` (root) or `UI/calculator_test_dashboard.html` (production)  
**Features:**
- Real-time test execution
- Visual pass/fail indicators
- Server status monitoring
- Category-based testing

---

## 🏗️ Architecture Documentation

### Calculator Architecture
**Primary Doc:** See `CALCULATOR_SYSTEM_DOCUMENTATION.md` → Architecture section  
**Implementation Pattern:** Registry V3 (direct module imports)  
**Key Components:**
- `tools/schemas/calculator_tools.json` - Registry schema (35 tools)
- `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py` - All calculator implementations
- `AI_infrastructure/routes/calculator_test_routes.py` - Flask API endpoints

### File Structure
```
AI_agents/
├── CALCULATOR_SYSTEM_DOCUMENTATION.md    ← MAIN CALCULATOR DOC
├── DOCUMENTATION_INDEX.md                ← THIS FILE
├── calculator_test_dashboard.html        ← Test dashboard (root)
├── UI/
│   ├── calculator_test_dashboard.html    ← Test dashboard (production)
│   └── modules_external/
│       └── quote-calculator/
│           ├── implementations/
│           │   └── calculator_wrapper.py
│           ├── schema/
│           │   ├── calculator_tools.json
│           │   └── shopify/
│           ├── tests/
│           │   └── test_all_calculators.py
│           └── exports/AI_Quotes/
├── AI_infrastructure/
│   └── routes/
│       └── calculator_test_routes.py
├── tools/
│   ├── schemas/
│   │   └── calculator_tools.json
│   └── implementations/
│       └── registry_v3.py
└── archive/
    ├── calculator_history/
    └── documentation/
```

---

## 🔧 Development Guides

### Adding a New Calculator
See: `CALCULATOR_SYSTEM_DOCUMENTATION.md` → Maintenance & Updates → Adding a New Calculator

**Quick Steps:**
1. Add function to `calculator_wrapper.py`
2. Add schema to `calculator_tools.json`
3. Add test to `test_all_calculators.py`
4. Run full test suite
5. Update documentation

### Updating Calculator Parameters
See: `CALCULATOR_SYSTEM_DOCUMENTATION.md` → Maintenance & Updates → Updating Calculator Parameters

**Quick Steps:**
1. Modify function signature
2. Update schema
3. Update tests if needed
4. Run test suite
5. Document changes

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (35/35)
- [ ] Dashboard accessible and functional
- [ ] Flask server running without errors
- [ ] Schema valid JSON
- [ ] No console errors in dashboard

### Deployment Steps
See: `CALCULATOR_SYSTEM_DOCUMENTATION.md` → Deployment Guide

1. Verify calculator schema
2. Test calculator wrapper
3. Run test suite
4. Start Flask server
5. Verify API endpoints

### Post-Deployment Verification
- [ ] Server status check (dashboard)
- [ ] Run all tests via dashboard
- [ ] Verify API endpoints respond
- [ ] Check pricing accuracy

---

## 📊 Current Status

### Calculator System
- **Total Calculators:** 35
- **Working:** 35/35 (100%)
- **Last Tested:** December 11, 2025
- **Registry Version:** V3
- **Status:** ✅ Production Ready

### Documentation Status
- **Core Docs:** Complete ✅
- **Archived Docs:** Organized ✅
- **Old Logs:** Cleaned ✅ (1,451 files removed)
- **Redundant Docs:** Deleted ✅ (51 files removed)

---

## 🗃️ Removed Documentation

### Deleted Files (December 12, 2025 Cleanup)
The following documentation files were removed as redundant, outdated, or superseded by `CALCULATOR_SYSTEM_DOCUMENTATION.md`:

**Status/Fix Documentation (24 files):**
- CALCULATOR_ALL_6_FIXED_DEC11.md
- CALCULATOR_CHAOS_ANALYSIS_DEC11.md
- CALCULATOR_COMPLETION_SUMMARY_DEC11.md
- CALCULATOR_DASHBOARD_BUTTON_ADDED.md
- CALCULATOR_DASHBOARD_FIXED.md
- CALCULATOR_DIRECT_IMPORT_SUCCESS_DEC11.md
- CALCULATOR_FINAL_STATUS_DEC11.md
- CALCULATOR_FIX_COMPLETE_DEC10.md
- CALCULATOR_FIX_COMPLETE_DEC11.md
- CALCULATOR_FIX_PROGRESS.md
- CALCULATOR_FIX_SUMMARY_DEC11.md
- CALCULATOR_FIXES_COMPLETE_DEC11.md
- CALCULATOR_PROGRESS_DEC11_PHASE2.md
- CALCULATOR_REGISTRY_TEST_SUCCESS_DEC11.md
- CALCULATOR_SCHEMA_FIX_COMPLETE_DEC11.md
- CALCULATOR_STATUS_REALITY_CHECK_DEC11.md
- CALCULATOR_STATUS_REPORT.md
- CALCULATOR_TEST_RESULTS.md
- CLEANUP_CALCULATOR_LAYERS_DEC11.md
- INHOUSE_CALCULATOR_FIX_SUMMARY.md
- INHOUSE_CALCULATOR_FIXES.md
- QUICK_FIX_INHOUSE_CALCULATOR.md
- QUOTE_CALCULATOR_ASSESSMENT_DEC11.md
- QUOTE_CALCULATOR_CONFIG_FIX_DEC9_2025.md

**Implementation/Migration Documentation (15 files):**
- BOOKLET_CALCULATOR_FIX_DEC10_2025.md
- COMPLETE_CALCULATOR_FIX_ANALYSIS_DEC10.md
- COMPLETE_SHOPIFY_CALCULATOR_IMPLEMENTATION_PLAN.md
- DEPLOYMENT_COMPLETE_BOOKLET_CALCULATOR_DEC10.md
- SHOPIFY_CALCULATOR_BUG_FIX_COMPLETE.md
- SHOPIFY_CALCULATOR_NAMING_RESTORATION_DEC10.md
- SHOPIFY_CALCULATOR_PREVIOUS_IMPLEMENTATION_ANALYSIS.md
- SHOPIFY_CALCULATOR_TEST_REPORT_DEC10.md
- SHOPIFY_CALCULATOR_WRAPPER_IMPLEMENTATION_DEC10.md
- SHOPIFY_CALCULATORS_FIX_COMPLETE_DEC10.md
- V9_SHOPIFY_CALCULATOR_ANALYSIS_DEC10.md
- CALCULATOR_IMPLEMENTATION_COMPLETE_DEC10.md
- CALCULATOR_IMPLEMENTATION_ROADMAP_DEC10.md
- COMPLETE_23_CALCULATORS_TO_ADD.md
- CALCULATOR_TOOL_DISCOVERY_IMPROVEMENT_PLAN.md

**Customer Quotes & Workflows (9 files):**
- CUSTOMER_QUOTE_PVC_FOAMBOARD_DEC10.md
- WORLDWIDE_A4_LANDSCAPE_BOOKLET_QUOTE_DEC10.md
- WORLDWIDE_BOOKLET_QUOTE_DEC10.md
- COMPLETE_WORK_QUOTE.md
- WORKFLOW_QUOTE_WITH_TEMPLATE_AND_EMAIL.md
- XERO_CONTACT_QUOTES_COMPLETE.md
- XERO_QUOTE_TOOLS_MIGRATION_COMPLETE.md
- CALCULATOR_WORKFLOW_ANALYSIS.md
- CALCULATOR_TEST_DASHBOARD_README.md

**Test Documentation (3 files):**
- tests/CALCULATOR_PARAMETER_REQUIREMENTS.md
- tests/CALCULATOR_TEST_RESULTS_FINAL.md
- tests/SHOPIFY_CALCULATOR_VERIFICATION.md

**Archive Docs (2 files):**
- docs/archive/QUOTE_CALCULATOR_MANIFEST_FIX.md
- docs/archive/QUOTE_CALCULATOR_MODULE_FIX.md

**Total Removed:** 53 files

### Log Files Cleaned (December 12, 2025)
- **Location:** `UI/modules_external/quote-calculator/exports/AI_Quotes/`
- **Removed:** 1,451 log files older than 7 days
- **Retained:** Recent logs (last 7 days)

---

## 📝 Documentation Standards

### File Naming Convention
- Use UPPERCASE for major documentation files
- Include dates in format: `_DEC12_2025` or `_20251212`
- Use underscores for word separation
- Keep names descriptive but concise

### Content Standards
- Include "Last Updated" date at top
- Provide clear table of contents for long documents
- Use code blocks with syntax highlighting
- Include working examples
- Link to related documentation

### Maintenance Schedule
- Review quarterly (March, June, September, December)
- Update after major system changes
- Archive old versions when superseded
- Clean up logs monthly

---

## 🔍 Quick Search Guide

### Finding Calculator Information
1. **General Info:** Check `CALCULATOR_SYSTEM_DOCUMENTATION.md`
2. **Specific Calculator:** Search calculator name in main doc
3. **Testing:** See Testing Documentation section
4. **Historical:** Check `archive/calculator_history/`

### Finding API Information
1. **API Reference:** `CALCULATOR_SYSTEM_DOCUMENTATION.md` → API Reference
2. **Endpoints:** `/api/calculator/list` and `/api/calculator/test`
3. **Implementation:** `AI_infrastructure/routes/calculator_test_routes.py`

### Finding Schema Information
1. **Main Schema:** `tools/schemas/calculator_tools.json`
2. **Module Schema:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`
3. **Shopify Configs:** `UI/modules_external/quote-calculator/schema/shopify/`

---

## 📞 Support Resources

### Internal Resources
- Main Documentation: `CALCULATOR_SYSTEM_DOCUMENTATION.md`
- Test Dashboard: `calculator_test_dashboard.html`
- Test Suite: `UI/modules_external/quote-calculator/tests/test_all_calculators.py`

### External Resources
- Python Documentation: https://docs.python.org/3/
- Flask Documentation: https://flask.palletsprojects.com/
- JSON Schema: https://json-schema.org/

---

## 🎯 Next Steps

### Immediate Priorities
1. ✅ Consolidate documentation (COMPLETE)
2. ✅ Clean up redundant files (COMPLETE)
3. ✅ Archive historical docs (COMPLETE)
4. ✅ Create documentation index (COMPLETE)

### Future Enhancements
- [ ] Add video tutorials for dashboard usage
- [ ] Create API client examples in multiple languages
- [ ] Add performance benchmarking documentation
- [ ] Create calculator configuration wizard

---

**Last Reviewed:** December 12, 2025  
**Version:** 1.0  
**Status:** ✅ Complete and Current
