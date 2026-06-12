# Deprecation Notice: top-level `tests/` cleanup (row 42)

**Date archived at this location:** June 12, 2026
**Status:** EXTRACTED from top-level `tests/` (not deleted — preserved here for historical reference)

---

## What was extracted

2 files were moved from the top-level `tests/` directory. After this extraction, the top-level `tests/` directory contains **28 Python files + 1 JavaScript file + 1 subdir (`calculators/`)**, all load-bearing or recently-modified.

| File | Size | Reason for extraction |
|---|---:|---|
| `test_inhouse_calculator_fix.py` | 17.5M | **Not a Python file.** This is a test log (Python `print(WARNING)` output) that was accidentally committed with a `.py` extension. Verified by `grep -c "^(import\|from\|def\|class\|print)"` → **0** (zero Python code lines). 242 lines × ~72KB/line, with every line consisting of repeated `[WARN]` characters. The only "import" in the file is a self-referential docstring: `python test_inhouse_calculator_fix.py`. |
| `test_all_calculators_with_fred_db.py` | 9K | References **non-existent modules**: `from inhouse_modules.db_connector import InHousePrintDB` and `from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator`. Neither path exists in the live code — `inhouse_modules/` is the legacy "FRED" InHouse Print system, superseded by the Supabase + AI-agents platform per CLAUDE.md §1. |

## Why these were moved

Per `ARCHIVE_CLEANUP_TRACKER.md` row 42, the spec was: "Top-level `tests/` cleanup ... Trace each. Heuristic: not imported anywhere, not in `.vscode/tasks.json`, not in `.github/workflows/`, last modified >6 months."

The audit verified:

| Check | `test_inhouse_calculator_fix.py` | `test_all_calculators_with_fred_db.py` |
|---|---|---|
| `from tests.X` or `import tests.X` anywhere | 0 hits | 0 hits |
| Referenced in `.vscode/tasks.json` | 0 hits | 0 hits |
| Referenced in `.github/workflows/*.yml` | 0 hits | 0 hits |
| Referenced in `AI_infrastructure/docs/*`, `routes/*`, `threads/*`, `V4_BUILD_COMPLETE.md` | 0 hits | 0 hits |
| Self-references own filename | 1 hit (in own docstring) | 0 hits |
| Last modified | Jan 15, 2026 (5 months ago) | Jan 15, 2026 (5 months ago) |
| Python code lines (`import`/`from`/`def`/`class`/`print`) | **0** (log file) | many, but module imports fail |
| Module imports executable as-is | **no** (log file) | **no** (`inhouse_modules.*` not found) |

The hard rule from the per-feature cleanup prompt is **"never `rm`, always `git mv`"** — so both files were preserved in `git log` and on disk by moving them to this archive location.

## What's still in `tests/` at the top level (28 .py + 1 .js + 1 subdir)

After this extraction, the live top-level `tests/` directory contains only **load-bearing** or **recently-validated** scripts:

**Documented in CLAUDE.md §3 (5 runners — must stay):**
- `run_all_tests.py` — runs persistent semantic search test suite
- `run_group2_tests.py` — Group 2 calculator tests (books)
- `run_group3_tests.py` — Group 3 calculator tests (notepads)
- `run_group4_tests.py` — Group 4 calculator tests (signs)
- `run_group5_tests.py` — Group 5 calculator tests (promotional products)

**Called as subprocess by `run_all_tests.py` (4 files — must stay):**
- `test_persistent_semantic_smoke.py`
- `test_persistent_semantic_compile.py`
- `test_persistent_semantic_endpoint.py`
- `test_persistent_semantic_e2e.py`

**Referenced in `CALCULATOR_TEST_QUOTES_SUMMARY_JAN26_2026.md` and `CALCULATOR_VALIDATION_TESTING_REANALYSIS_JAN26_2026.md` (6 per-calculator regression tests):**
- `test_luxury_classic_pull_up_banners.py`
- `test_premium_pull_up_banners.py`
- `test_metal_face_a_frame.py`
- `test_strut_cards_a3.py`
- `test_strut_cards_a4.py`
- `test_strut_cards_a5.py`

**Standalone calculator tests (kept — useful but not part of any runner):**
- `test_all_calculators.py` (comprehensive, dated Dec 8, 2025)
- `test_calculator_with_db.py`
- `test_calculator_fix_simple.py` (specific JSON deserialization fix regression)
- `test_calculators_correct_params.py`
- `test_calculators_direct.py`
- `test_parameter_mapping.py`
- `test_shopify_calculator_tools.py`
- `test_shopify_calculators_no_db.py`
- `test_group5_calculator1_luxury_pull_up_banners.py`
- `test_group5_calculator2_selfie_frames.py`
- `test_group5_calculators3_4_5.py`

**Utility:**
- `discover_calculator_parameters.py` (calculator introspection tool)

**Recent frontend test (must stay — added in commit `6380511a` June 11, 2026):**
- `verify_settings_save_flow.js`

**Subdir (separate audit scope):**
- `tests/calculators/` — 13 pytest-style alignment tests (modern, with `TestWireBoundBooksAlignment` classes) — **out of scope** for row 42 (the row spec is "top-level tests/ cleanup", and the subdir is a separate, well-bounded test infrastructure)

## How to recover

Preserved in `git log` history. To view the pre-move state:

```bash
git log --diff-filter=R -- archive/top_level_tests_row42_dead/
```

To see the files at their original paths:

```bash
git log --all -- 'tests/test_inhouse_calculator_fix.py'
git log --all -- 'tests/test_all_calculators_with_fred_db.py'
```

## References

- **Cleanup row:** row 42 of `ARCHIVE_CLEANUP_TRACKER.md`
- **Branch:** `cleanup/top-tests-cleanup`
- **Audit doc:** `docs/agents/ROW_42_TOP_LEVEL_TESTS_CLEANUP.md` (created in this round)
