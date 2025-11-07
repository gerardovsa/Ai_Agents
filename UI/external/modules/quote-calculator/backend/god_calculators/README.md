# GOD Calculators - CLI Tools

**Location:** `G_Folder/Quote_Calculator/god_calculators/`  
**Status:**  Production Ready  
**Last Updated:** October 12, 2025

## Overview

GOD (Database-Driven) calculators with command-line interfaces for automated quoting. All calculators use the same database tables as the VB.NET production system.

## Available Calculators

| Calculator | File | CLI Tool | Status |
|------------|------|----------|--------|
| Perfect Bound Books | `GOD_perfect_bound_books_calculator.py` | `pbb_cli.py` |  Complete |
| Flyers | `GOD_flyer_calculator.py` | `flyers_cli.py` |  Complete |
| Letterheads | `GOD_letterhead_calculator.py` | `letterheads_cli.py` |  Complete |
| Corflute Signs | `corflute_calculator.py` | *(pending)* | ⏳ Planned |

## Quick Start

### Perfect Bound Books
```bash
# Single quote
python pbb_cli.py --qty 100 --width 148 --height 210 --pages 200 --gsm 80 --cover-gsm 300

# Compare multiple quantities
python pbb_cli.py --qty 100 250 500 1000 --width 148 --height 210 --pages 200 --gsm 80 --cover-gsm 300 --compare

# JSON output
python pbb_cli.py --qty 100 --width 148 --height 210 --pages 200 --gsm 80 --cover-gsm 300 --json
```

### Flyers
```bash
# Basic A4 flyer
python flyers_cli.py --qty 1000 --width 210 --height 297 --gsm 150 --sides both

# With folding and cellophane
python flyers_cli.py --qty 1000 --width 210 --height 420 --gsm 170 --sides both --folding 1 --cello gloss-both

# Compare quantities
python flyers_cli.py --qty 500 1000 2500 5000 --width 210 --height 297 --gsm 150 --sides both --compare
```

### Letterheads
```bash
# Standard A4 letterhead
python letterheads_cli.py --qty 500 --width 210 --height 297 --gsm 100 --sides front

# Double-sided
python letterheads_cli.py --qty 1000 --width 210 --height 297 --gsm 100 --sides both

# Compare quantities
python letterheads_cli.py --qty 250 500 1000 2500 --width 210 --height 297 --gsm 100 --sides front --compare
```

## Common Arguments

### Required (vary by calculator)
- `--qty` - Quantity (can specify multiple: `--qty 100 500 1000`)
- `--width` - Width in mm
- `--height` - Height in mm
- `--gsm` - Paper weight

### Optional
- `--json` - Output as JSON for API integration
- `--compare` - Show comparison table (automatic with multiple quantities)

## Output Modes

### 1. Single Quote (default)
Detailed breakdown with specifications, costs, and pricing.

### 2. Comparison Table (`--compare`)
Side-by-side comparison of multiple quantities with key metrics.

### 3. JSON Output (`--json`)
Structured data for API integration and automation.

## Database Tables Used

All calculators use these SQL Server tables:

- **Quote_DigitalStocks** - Paper stock pricing and sizes (7 columns)
- **Quote_DigitalClicks** - Printing costs per A4 (3 columns)
- **Quote_ProfitMargins** - Tiered profit margins (4 columns)
- **Quote_GenericSetting** - Configuration values (3 columns)
- **Quote_PBBPerBookBindCost** - Perfect bound binding costs (4 columns, PBB only)
- **Quote_PBBExtraBookScale** - Extra books allowance (4 columns, PBB only)

## Python Import Usage

### Using CLI Programmatically
```python
import sys
sys.argv = ['pbb_cli.py', '--qty', '100', '--width', '148', '--height', '210', 
            '--pages', '200', '--gsm', '80', '--cover-gsm', '300', '--json']
from god_calculators.pbb_cli import main
exit_code = main()
```

### Using Calculator Directly
```python
import sys
import os
sys.path.insert(0, 'c:/Users/gpoli/GIT/In_House_SQL/G_Folder/tools')
from db_connector import InHousePrintDB
from god_calculators.GOD_perfect_bound_books_calculator import PerfectBoundBooksCalculator

config_path = 'c:/Users/gpoli/GIT/In_House_SQL/G_Folder/config/database-config.json'

# PBB uses context manager
with PerfectBoundBooksCalculator(config_path) as calc:
    result = calc.calculate(
        quantity=100,
        width=148,
        height=210,
        pages=200,
        internal_gsm=80,
        cover_gsm=300
    )
    print(f"Price: ${result.total_cost_inc_gst:.2f}")

# Flyers and Letterheads need db_connector
db = InHousePrintDB(config_path)
from god_calculators.GOD_flyer_calculator import FlyerCalculatorGOD
calc = FlyerCalculatorGOD(db)
result = calc.calculate(quantity=1000, width=210, height=297, gsm=150, print_side1=1, print_side2=1)
print(f"Price: ${result.total_cost_inc_gst:.2f}")
db.close()
```

## Calculator Accuracy

All GOD calculators have been validated against:
- VB.NET source code formulas
- Production database tables
- Actual production job data

**Perfect Bound Books**: ±2% accuracy (validated Oct 12, 2025)

## Common Paper Sizes

| Size | Width (mm) | Height (mm) | Use Case |
|------|------------|-------------|----------|
| A4 | 210 | 297 | Standard documents |
| A5 | 148 | 210 | Half A4, booklets |
| A6 | 105 | 148 | Postcards |
| DL | 99 | 210 | 1/3 A4, mailers |
| A3 | 297 | 420 | Large flyers |

## Common GSM Values

| GSM Range | Type | Use Case |
|-----------|------|----------|
| 80-100 | Text | Internal pages, letterheads |
| 115-150 | Light card | Flyers, certificates |
| 170-250 | Medium card | Business cards, covers |
| 300-400 | Heavy card | Premium cards, covers |

## Error Handling

All CLI tools return:
- **Exit code 0**: Success
- **Exit code 1**: Error (with detailed traceback)

Database connections are automatically cleaned up on both success and error.

## File Structure

```
god_calculators/
├── README.md                              # This file
├── GOD_perfect_bound_books_calculator.py  # PBB calculator (932 lines)
├── GOD_flyer_calculator.py                # Flyers calculator (809 lines)
├── GOD_letterhead_calculator.py           # Letterheads calculator (554 lines)
├── corflute_calculator.py                 # Corflute calculator (562 lines)
├── pbb_cli.py                             # PBB CLI tool (342 lines)
├── flyers_cli.py                          # Flyers CLI tool (324 lines)
├── letterheads_cli.py                     # Letterheads CLI tool (285 lines)
└── __init__.py                            # Module initialization
```

## Development Notes

### Initialization Patterns

**Perfect Bound Books** - Context Manager:
```python
with PerfectBoundBooksCalculator(config_path) as calc:
    result = calc.calculate(...)
```

**Flyers & Letterheads** - Manual DB Connection:
```python
db = InHousePrintDB(config_path)
calc = FlyerCalculatorGOD(db)
result = calc.calculate(...)
db.close()
```

**Corflute** - Standalone (no database):
```python
calc = CorflutePricingCalculator()
result = calc.calculate_base_quote(...)
```

## Related Documentation

- **Main Calculator Docs**: `G_Folder/Quote_Calculator/CALCULATOR_ARCHITECTURE.md`
- **Database Reference**: `G_Folder/tools/docs/business/DATABASE_BUSINESS_ATLAS.md`
- **Schema Tools**: `G_Folder/tools/docs/business/SCHEMA_TOOLS_REFERENCE.md`

## Support

For calculator issues or questions:
1. Check calculator test functions (at bottom of each .py file)
2. Review VB.NET source in `InHousePrint/Classes/`
3. Verify database table schemas with `stock_database_cli.py`

## Changelog

**October 12, 2025**
-  Created CLI tools for PBB, Flyers, Letterheads
-  Consolidated documentation into single README
-  Validated all calculators against production data
-  Added JSON output mode to all CLI tools
-  Implemented comparison mode for multi-quantity quotes
