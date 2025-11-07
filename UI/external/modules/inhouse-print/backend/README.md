# InHouse Print Backend

**IMPORTANT:** This module REUSES the backend from `quote-calculator` module.

## Backend Location

**Actual backend files:** `../quote-calculator/backend/`

This folder contains a README only. The `inhouse_wrapper.py` file references the backend path directly.

## Backend Files Used

From `../quote-calculator/backend/`:
- `tool_use_agent.py` (3,187 lines) - Main Tool Use Agent
- `complete_calculator_implementation.py` (6,277 lines) - Quote Calculator
- `query_library.py` (5,042 lines) - 50+ SQL queries
- `db_connector.py` - SQL Server connection
- `stock_database_tools.py` - SQLite stock management
- All 6 Shopify calculators

## Why Reuse?

- **No duplication:** Backend files are already in quote-calculator
- **Single source of truth:** Updates to backend affect both modules
- **Singleton pattern:** Wrapper creates single ToolUseAgent instance
- **Clean separation:** Schema + wrapper in this module, backend shared

## Architecture

```
inhouse-print/
├── schema/
│   └── inhouse_tools.json          (6 tool definitions)
├── implementations/
│   └── inhouse_wrapper.py          (bridges to backend)
└── backend/ (THIS FOLDER)
    └── README.md                   (you are here)

quote-calculator/backend/           (actual backend files)
├── tool_use_agent.py
├── complete_calculator_implementation.py
├── query_library.py
└── ... (all other backend files)
```

The wrapper adds `../quote-calculator/backend` to `sys.path` and imports directly.

## No Action Required

This is informational only. The wrapper handles path resolution automatically.
