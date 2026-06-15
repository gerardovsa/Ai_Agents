# Archived Documentation - Historical Reference Only

**Date Archived:** December 14, 2025  
**Status:** Historical Reference - Do Not Use for Current Implementation

---

## ⚠️ Important Notice

These files are **ARCHIVED** and represent historical documentation from the original calculator implementation and migration process. They are kept for reference purposes only.

**For current documentation, see:** `../README.md`

---

## 📚 Archived Files (12 documents)

### Architecture & Design (3 files)

1. **ARCHITECTURE_DIAGRAM.md**
   - Visual system architecture from original integration
   - Data flow diagrams
   - Component relationships
   - **Superseded by:** README.md "Architecture" section

2. **CALCULATOR_ARCHITECTURE.md**
   - GOD vs Shopify architecture comparison
   - Original calculator organization
   - **Superseded by:** README.md "Calculator Types" section

3. **CONVERSION_PLAN.md**
   - Original implementation roadmap
   - Migration strategy notes
   - **Status:** Migration complete (Oct 2025)

### Implementation & Integration (4 files)

4. **INTEGRATION_GUIDE.md**
   - Step-by-step integration instructions
   - Wrapper pattern implementation
   - **Superseded by:** README.md "Usage Guide" section

5. **README_INTEGRATION.md**
   - Files copied from In_House_SQL
   - Transfer summary
   - **Status:** Transfer complete (Oct 30, 2025)

6. **MODULE_REORGANIZATION_COMPLETE.md**
   - File reorganization summary
   - **Status:** Reorganization complete

7. **COPY_COMPLETE_SUMMARY.md**
   - Original copy operation summary
   - **Status:** Historical record

### File Management (3 files)

8. **FILE_LOCATIONS.md**
   - Original file organization
   - Path mappings
   - **Superseded by:** README.md "Module Structure" section

9. **FILE_MAPPING.md**
   - Complete file inventory from migration
   - Source → destination mappings
   - **Status:** Historical record

10. **DOCUMENTATION_INDEX.md**
    - Original documentation index
    - Navigation guide for old structure
    - **Superseded by:** README.md (single comprehensive doc)

### Technical Reference (2 files)

11. **CALCULATION_ALGORITHMS.md** (2,374 lines)
    - VB.NET to Python algorithm conversions
    - Detailed calculation formulas
    - Database schema details
    - **Partially superseded by:** README.md "Database Configuration" section
    - **Keep for:** Deep-dive algorithm reference

12. **DATABASE_AND_BUSINESS_RULES.md**
    - SQL table structures
    - Business logic reference
    - Configuration values
    - **Partially superseded by:** README.md "Database Configuration" section
    - **Keep for:** Detailed database schema reference

---

## 🔄 Migration Timeline

- **Oct 9, 2025** - Initial calculator architecture defined
- **Oct 12, 2025** - Documentation index created, 50+ docs archived
- **Oct 30, 2025** - Files copied from In_House_SQL to AI_agents
- **Nov-Dec 2025** - Module reorganization and self-containment
- **Dec 14, 2025** - Final consolidation into single README.md

---

## 📖 What Changed?

### Old Structure (Pre-Dec 14, 2025)
```
quote-calculator/
├── ARCHIVE/ORIGINAL/          # 5 markdown files
├── ARCHIVE_DOCS/              # 7 markdown files
├── DOCUMENTATION/             # 3 reference files
└── [No consolidated README]
```

**Issues:**
- Documentation scattered across 3 folders
- 12 separate files to search through
- Outdated references to old file paths
- Redundant information across multiple files

### New Structure (Dec 14, 2025)
```
quote-calculator/
├── README.md                  # ✅ Single comprehensive doc (400+ lines)
├── DOCUMENTATION/             # Reference docs (SQL queries, etc.)
└── ARCHIVE_CONSOLIDATED/      # Historical docs (this folder)
```

**Benefits:**
- ✅ Single source of truth (README.md)
- ✅ Up-to-date with current structure
- ✅ Includes test results and troubleshooting
- ✅ Clear module organization
- ✅ Historical docs preserved but separated

---

## 🔍 When to Reference These Files

### Use README.md for:
- Current architecture and structure
- Usage examples and API reference
- Testing and troubleshooting
- Quick start guides
- Module statistics

### Use CALCULATION_ALGORITHMS.md for:
- Deep-dive algorithm details
- VB.NET conversion notes
- Mathematical formulas
- Complex calculation logic

### Use DATABASE_AND_BUSINESS_RULES.md for:
- Detailed table schemas
- Business rule specifics
- Configuration value lists
- Database query patterns

### Other Archived Files:
- Historical reference only
- Migration process documentation
- Old file organization patterns

---

## ✅ Verification

**Current Module Status (Dec 14, 2025):**
- 31 calculators operational
- 97.5% test pass rate (39/40)
- Self-contained module structure
- No external dependencies except inhouse-print/db_connector
- All imports fixed (23 files updated)
- Comprehensive documentation in single README.md

---

**For Questions or Issues:**
- See current documentation: `../README.md`
- Run tests: `python tests/test_comprehensive.py`
- Check module structure: `ls -R backend/`
