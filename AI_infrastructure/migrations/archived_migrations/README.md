# Archived Migrations

Historical migration files that have been applied and are no longer needed for active development.

## Files

- **run_009_migration.py** - Added 'unassigned' and 'prime-loaded' location values (Dec 2025)
- **run_010_migration.py** - Removed 'prime-loaded' location value (Dec 2025)
- **verify_010.py** - Verification script for migration 010

## Why Archived?

These migrations were part of the "prime-loaded" location cleanup. The functionality has been:
1. Applied to the production database
2. Fixed in all JavaScript frontend code
3. Simplified to use only 'prime' location

These files are kept for historical reference but are no longer needed for active development.

## Current Location Values

- `unassigned` - Thread not assigned to any location
- `prime` - AI Prime sidebar
- `agent-1` through `agent-26` - Command Center agent columns
- `synergy` - Synergy workspace
