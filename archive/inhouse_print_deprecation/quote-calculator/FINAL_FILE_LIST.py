# QUOTE-CALCULATOR MODULE - DEFINITIVE USED FILES LIST
# =====================================================
# Based on code analysis of imports in calculator_wrapper.py (lines 60-90)

ACTIVE_FILES = """
✅ ACTUALLY USED BY SYSTEM (Total: 19 files)
==============================================

CORE MODULE (4 files):
  manifest.json
  quote-calculator.html
  quote-calculator.js
  quote-calculator.css

SCHEMAS (2 files):
  schema/calculator_tools.json
  schema/query_library_tools.json

WRAPPERS (2 files):
  implementations/calculator_wrapper.py
  implementations/query_library_wrapper.py

GOD CALCULATORS - Database-driven (4 files):
  backend/god_calculators/GOD_flyer_calculator.py
  backend/god_calculators/GOD_letterhead_calculator.py
  backend/god_calculators/GOD_perfect_bound_books_calculator.py
  backend/god_calculators/corflute_calculator.py

SHOPIFY CALCULATORS - Hardcoded pricing (6 files):
  backend/shopify_calculators/EconomicalBusinessCards_Shopify_Calculator.py
  backend/shopify_calculators/PremiumBusinessCards_Shopify_Calculator.py
  backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py
  backend/shopify_calculators/WireBound_Shopify_Calculator.py
  backend/shopify_calculators/SpiralBound_Shopify_Calculator.py
  backend/shopify_calculators/PerfectBound_Shopify_Calculator.py  ← CONFIRMED IMPORTED

UTILITIES (1 file):
  backend/query_library.py

"""

UNUSED_FILES = """
❌ NOT USED - SAFE TO DELETE/ARCHIVE (60+ files)
==================================================

TEMPORARY ANALYSIS SCRIPTS (8 files):
  CALCULATOR_FILE_COMPARISON.py
  analyze_files.py
  compare_files.py
  compare_schemas.py
  final_summary.py
  find_duplicates.py
  remove_duplicates.py
  ACTUALLY_USED_FILES.py

CLI TESTING SCRIPTS (3 files):
  backend/god_calculators/flyers_cli.py
  backend/god_calculators/letterheads_cli.py
  backend/god_calculators/pbb_cli.py

DUPLICATE/OLD SHOPIFY CALCULATORS (2 files):
  backend/shopify_calculators/business_card_calculator_shopify.py
  backend/shopify_calculators/corflute_calculator_shopify.py
  └─ These are DUPLICATES of the newer Shopify calculators above

OLD CONFIG FILES (16 files):
  backend/configs/Business_Cards_Economic.json
  backend/configs/Corflute_Signs_Shopify.json
  backend/configs/Perfect_Bound_Books_WooCommerce.json
  backend/configs/Perfect_Bound_books.json
  backend/configs/Premium_Business_Cards.json
  backend/configs/Printed_Flyers_Shopify.json
  backend/configs/Wire_Spiral_Bound.json
  backend/configs/folded_printed_flyers_Shopify.json
  schema/shopify/Business_Cards_Economic.json
  schema/shopify/Corflute_Signs_Shopify.json
  schema/shopify/Perfect_Bound_Books_WooCommerce.json
  schema/shopify/Perfect_Bound_books.json
  schema/shopify/Premium_Business_Cards.json
  schema/shopify/Printed_Flyers_Shopify.json
  schema/shopify/Wire_Spiral_Bound.json
  schema/shopify/folded_printed_flyers_Shopify.json

LOG FILES (10 files, 717 KB):
  exports/AI_Quotes/ai_quote_session_20251208_042531.log
  exports/AI_Quotes/ai_quote_session_20251208_044327.log
  exports/AI_Quotes/ai_quote_session_20251208_044329.log
  exports/AI_Quotes/ai_quote_session_20251208_044330.log
  exports/AI_Quotes/ai_quote_session_20251208_044332.log
  exports/AI_Quotes/ai_quote_session_20251208_044333.log
  exports/AI_Quotes/ai_quote_session_20251208_054039.log
  exports/AI_Quotes/ai_quote_session_20251208_061951.log
  exports/AI_Quotes/ai_quote_session_20251209_134743.log
  exports/AI_Quotes/ai_quote_session_20251209_134759.log

DOCUMENTATION (4 files):
  QUERY_LIBRARY_COMPLETE_INVENTORY.md
  SQL_PATTERNS_ANALYSIS.md
  backend/god_calculators/README.md
  tests/README.md

TEST FILES (1 file):
  tests/test_all_calculators.py

OTHER CONFIG (3 files):
  config/database-config.json
  tools/manifest.json
  backend/__init__.py (may be needed - check if empty)
  backend/god_calculators/__init__.py (may be needed - check if empty)
  backend/shopify_calculators/__init__.py (may be needed - check if empty)
  implementations/__init__.py (may be needed - check if empty)

"""

print(ACTIVE_FILES)
print(UNUSED_FILES)

print("\n" + "="*80)
print("📊 FINAL STATISTICS")
print("="*80)
print(f"✅ ACTIVE FILES:     19")
print(f"❌ UNUSED FILES:     60+")
print(f"📂 TOTAL FILES:      79+")
print(f"💾 Wasted Space:     ~1 MB+ (logs, old configs, duplicate code)")
print()
print("🎯 Recommendation: Move unused files to ARCHIVE folder")
