# Quote Calculator Documentation Index

**Last Updated:** October 12, 2025  
**Status:** Cleaned and Consolidated

## 📂 Directory Structure

```
Quote_Calculator/
├── DOCUMENTATION_INDEX.md (this file - ⭐ START HERE)
├── god_calculators/              # GOD (Database-Driven) Calculators
│   ├── README.md                 # ⭐ CLI Tools Guide
│   ├── GOD_perfect_bound_books_calculator.py (932 lines)
│   ├── GOD_flyer_calculator.py (809 lines)
│   ├── GOD_letterhead_calculator.py (554 lines)
│   ├── corflute_calculator.py (562 lines)
│   ├── pbb_cli.py 
│   ├── flyers_cli.py 
│   └── letterheads_cli.py 
├── shopify_calculators/          # Shopify Website Calculators (hardcoded)
├── AI_Quote_Agent/               # AI Agent System
├── stocks/                       # Stock Management CLI
├── ui_components/                # Streamlit UI Components
└── ARCHIVE/                      # Historical files (Oct 12, 2025 cleanup)
    ├── docs_oct12_2025/          # 50+ analysis documents
    └── test_scripts/             # 30+ test scripts
```

## 🎯 Quick Start Guides

### For Calculator Usage
1. **GOD Calculators CLI** → `god_calculators/README.md` ⭐ **START HERE**
2. **Architecture Overview** → `CALCULATOR_ARCHITECTURE.md`
3. **Database Rules** → `DATABASE_AND_BUSINESS_RULES.md`
4. **Formulas** → `CALCULATION_ALGORITHMS.md`

### For Development
1. **AI Agent Integration** → `AI_USAGE_EXAMPLES.md`
2. **CLI Tools** → `CLI_TOOLS_REFERENCE.md`
3. **Stock Management** → `STOCK_USAGE_ANALYTICS_TOOLS.md`

## 📚 Core Documentation (Active Files)

### Calculator System (Essential)
- **`god_calculators/README.md`** ⭐ - Complete CLI tools guide
- **`CALCULATOR_ARCHITECTURE.md`** (10KB) - GOD vs Shopify explained
- **`CALCULATION_ALGORITHMS.md`** (91KB) - All formulas documented
- **`DATABASE_AND_BUSINESS_RULES.md`** (15KB) - Business logic

### Implementation Files (Production Code)
- **`complete_calculator_implementation.py`** (331KB) - Main system
- **`comprehensive_quote_system.py`** (171KB) - Quote generator
- **`god_calculators/*.py`** - Database-driven calculators 
- **`shopify_calculators/*.py`** - Website price matchers

### AI Agent System
- **`AI_USAGE_EXAMPLES.md`** (11KB) - How to use AI agent
- **`AI_SPECIFICATIONS_USED.md`** (6KB) - AI configuration
- **`AI_INFORMATION_FLOW_AND_TIMING.md`** (34KB) - Workflow details
- **`SHOW_ACTUAL_AI_PROMPT_AND_TOOLS.py`** (23KB) - Debug tool

### Stock & Pricing Logic
- **`STOCK_IMPOSITION_MAPPING_DESIGN.md`** (17KB) - Stock selection
- **`STOCKIMPOSITIONMAPPING_EXPLAINED.md`** (13KB) - Imposition
- **`UPS_IMPOSITION_SOLUTION.md`** (12KB) - UPS calculations
- **`STOCK_LIST_WITH_CONFIDENCE.md`** (11KB) - Stock reference

### Tools & Utilities
- **`CLI_TOOLS_REFERENCE.md`** (10KB) - CLI commands
- **`STOCK_USAGE_ANALYTICS_TOOLS.md`** (12KB) - Analytics
- **`calculator_pricing_dashboard.py`** (21KB) - Dashboard
- **`inventory_tracker.py`** (28KB) - Inventory tracking

## 🗑️ Archived Files (Oct 12, 2025 Cleanup)

### Moved to `ARCHIVE/test_scripts/` (30+ files)
- All `test_*.py` scripts
- All `debug_*.py`, `check_*.py` files  
- All `analyze_*.py` analysis scripts
- Old `calculator_cli.py` (replaced by individual CLI tools)
- Utility scripts: `extract_*.py`, `validate_*.py`, etc.

### Moved to `ARCHIVE/docs_oct12_2025/` (50+ docs)
- All comparison and analysis documents (`*COMPARISON*.md`)
- Extraction status reports (`*EXTRACTION*.md`, `*STATUS*.md`)
- Bug fix summaries (`*FIX*.md`, `*VERIFICATION*.md`)
- Assessment documents (`*ASSESSMENT*.md`, `*FINDINGS*.md`)
- Implementation docs (`*IMPLEMENTATION*.md`, `*INTEGRATION*.md`)
- WooCommerce/Shopify analysis docs

### Moved to `ARCHIVE/` (other)
- WooCommerce calculator copies
- `complete_calculator_implementation copy.py`
- Old JSON analysis files (`.json`)

##  Current Status (Oct 12, 2025)

### Completed
-  GOD Calculator CLI tools (PBB, Flyers, Letterheads)
-  All calculators validated against VB.NET
-  Documentation consolidated into single README
-  Folder cleaned and organized
-  80+ obsolete files archived

### In Progress
- ⏳ Corflute CLI tool (calculator exists, CLI pending)

### Planned
- 📋 Wire/Spiral Bound calculator extraction from VB.NET
- 📋 Pads/NCR calculator extraction from VB.NET

## 📖 Navigation Guide

### I want to...

| Goal | Go to |
|------|-------|
| **Run quotes via CLI** | `god_calculators/README.md` ⭐ |
| **Understand formulas** | `CALCULATION_ALGORITHMS.md` |
| **Use AI agent** | `AI_USAGE_EXAMPLES.md` |
| **Check pricing rules** | `DATABASE_AND_BUSINESS_RULES.md` |
| **See calculator types** | `CALCULATOR_ARCHITECTURE.md` |
| **Find old analysis** | `ARCHIVE/docs_oct12_2025/` |
| **Review test scripts** | `ARCHIVE/test_scripts/` |
| **Stock calculations** | `STOCK_IMPOSITION_MAPPING_DESIGN.md` |
| **CLI commands** | `CLI_TOOLS_REFERENCE.md` |

## 🎓 Learning Path

### New to the System?
1. Read `god_calculators/README.md` - Understand CLI tools
2. Read `CALCULATOR_ARCHITECTURE.md` - Learn system design
3. Read `DATABASE_AND_BUSINESS_RULES.md` - Understand business logic
4. Try CLI tools with sample quotes

### Want to Develop?
1. Review `CALCULATION_ALGORITHMS.md` - Master the formulas
2. Study calculator source code in `god_calculators/`
3. Check `AI_USAGE_EXAMPLES.md` - Learn AI integration
4. Review archived analysis in `ARCHIVE/` for context

### Debugging Issues?
1. Use `SHOW_ACTUAL_AI_PROMPT_AND_TOOLS.py` - Debug AI
2. Check `calculator_pricing_dashboard.py` - Visual pricing analysis
3. Review `ARCHIVE/test_scripts/` - Find relevant test cases
4. Check `ARCHIVE/docs_oct12_2025/` - Past bug fixes

## ⚠️ Important Notes

1. **GOD Calculators** = Database-driven, matches VB.NET production system
2. **Shopify Calculators** = Hardcoded for website price matching ONLY
3. **All CLI tools** = Use production database (read-only queries)
4. **ARCHIVE folder** = Historical reference, NOT production code
5. **Context managers** = PBB uses them, Flyers/Letterheads use manual db.close()

## 📊 File Count Summary

- **Active Documentation**: 20 files (core reference)
- **Active Code**: 10+ calculators + CLI tools
- **Archived Documentation**: 50+ files (historical)
- **Archived Scripts**: 30+ files (test/debug)
- **Total Cleanup**: ~80 files organized into ARCHIVE/

---

**Need Help?** Start with `god_calculators/README.md` for CLI usage or `CALCULATOR_ARCHITECTURE.md` for system overview.
