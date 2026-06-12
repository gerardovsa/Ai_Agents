# Row 42 — Top-Level `tests/` Cleanup

**Date:** 2026-06-12
**Scope:** `code+docs` — trace 30 .py + 1 .js files at top-level of `tests/`, archive dead, document the rest
**Author:** Claude (cleanup session, branch `cleanup/top-tests-cleanup`)

---

## 1. Scope

Per `ARCHIVE_CLEANUP_TRACKER.md` row 42:
> "Top-level `tests/` cleanup | code+docs | `run_group*.py`, `test_all_calculators*.py`, `test_*.py` (calculator tests). Trace each."

Heuristic from the spec:
> "not imported anywhere, not in `.vscode/tasks.json`, not in `.github/workflows/`, last modified >6 months"

User instruction for this row: aggressive — proceed with moves once classified.

---

## 2. Inventory

**Total: 30 .py + 1 .js + 1 subdir (`calculators/`) at the start of the audit, ~17.9 MB total.**

Of the 30 .py files:
- **5** are `run_*.py` (the documented calculator test runners)
- **4** are `test_persistent_semantic_*.py` (called as subprocesses by `run_all_tests.py`)
- **1** is `test_all_calculators.py` (comprehensive Dec 8 2025 test)
- **1** is `test_all_calculators_with_fred_db.py` (FRED-system, **DEAD**)
- **1** is `test_inhouse_calculator_fix.py` (17.5MB log, **DEAD**)
- **6** are per-calculator regression tests for luxury/premium/strut-cards banners
- **3** are `test_group5_calculator*.py` (Group 5 promotional-product tests)
- **4** are Shopify/calculator tests (`test_shopify_calculator_tools.py`, `test_shopify_calculators_no_db.py`, `test_calculator_with_db.py`, `test_calculators_correct_params.py`)
- **2** are standalone calculator tests (`test_calculator_fix_simple.py`, `test_calculators_direct.py`)
- **1** is `test_parameter_mapping.py` (parameter introspection utility)
- **1** is `discover_calculator_parameters.py` (calculator introspection utility)
- **1** is `verify_settings_save_flow.js` (frontend test, June 11 2026)

The `tests/calculators/` subdir has 13 pytest-style alignment tests (with `TestWireBoundBooksAlignment` classes) — **out of scope** for row 42 (the spec is "top-level tests/" only; the subdir is a separate, well-bounded test infrastructure using pytest).

---

## 3. Trace results — heuristic from row 42 spec

| Check | Tool | Result |
|---|---|---|
| `from tests.X` / `import tests.X` | `grep -rnE "(from\|import)\s+tests\." .` | **0 hits** — no Python code imports from top-level `tests/` |
| Referenced in `.vscode/tasks.json` | `cat .vscode/tasks.json \| grep -E "tests/"` | **0 hits** — tasks.json only references `tools/debug_version_hash.py`, `tools/force_regenerate_embeddings.py`, `tools/manage_semantic_cache.py` |
| Referenced in `.github/workflows/*.yml` | `grep -rE "tests/(run_group\|run_all\|test_)" .github/workflows/` | **0 hits** |
| Referenced in active docs (CLAUDE.md, README*, V4 docs) | `grep -rE "tests/(run_group\|run_all\|test_)" CLAUDE.md README* docs/` | **5 hits in CLAUDE.md §3** (the 5 `run_*.py` runners); **0 hits in any other active doc** |
| `test_persistent_semantic_*.py` called by `run_all_tests.py`? | `grep "test_persistent_semantic" tests/run_all_tests.py` | **4 hits** — yes, all 4 are subprocess-called |
| Per-calc tests referenced in historical fix logs? | `grep "test_luxury\|test_premium\|test_metal_face\|test_strut_cards" CALCULATOR_*.md` | **8 hits across 2 files**: `CALCULATOR_TEST_QUOTES_SUMMARY_JAN26_2026.md`, `CALCULATOR_VALIDATION_TESTING_REANALYSIS_JAN26_2026.md` |
| Last modified >6 months? | `git log -1 --format="%ad" --date=short -- tests/*.py` | **None.** All files last modified Jan 15-27, 2026 (~5 months ago). The heuristic does not fire. |

The `>6 months` heuristic did not fire on any file (everything is ~5 months old), so the trace relied on the **other 3 heuristics** + a per-file analysis of what each file actually does.

---

## 4. Files classified

### 4.1 KEEP (29 files — load-bearing or recently-validated)

**5 runners documented in CLAUDE.md §3 (must stay):**
- `run_all_tests.py` — runs persistent semantic search test suite (calls 4 test_persistent_semantic_*.py as subprocesses)
- `run_group2_tests.py` — Group 2 calculator tests (books)
- `run_group3_tests.py` — Group 3 calculator tests (notepads)
- `run_group4_tests.py` — Group 4 calculator tests (signs)
- `run_group5_tests.py` — Group 5 calculator tests (promotional products)

**4 called as subprocess by `run_all_tests.py` (must stay):**
- `test_persistent_semantic_smoke.py`
- `test_persistent_semantic_compile.py`
- `test_persistent_semantic_endpoint.py`
- `test_persistent_semantic_e2e.py`

**6 per-calc regression tests referenced in 2 historical fix logs:**
- `test_luxury_classic_pull_up_banners.py`
- `test_premium_pull_up_banners.py`
- `test_metal_face_a_frame.py`
- `test_strut_cards_a3.py`
- `test_strut_cards_a4.py`
- `test_strut_cards_a5.py`
- *References found in `CALCULATOR_TEST_QUOTES_SUMMARY_JAN26_2026.md` and `CALCULATOR_VALIDATION_TESTING_REANALYSIS_JAN26_2026.md`*

**9 standalone calculator/Shopify tests (likely useful — kept conservatively):**
- `test_all_calculators.py` (12K, comprehensive, dated Dec 8 2025)
- `test_calculator_with_db.py` (8.9K, calculator with DB connection)
- `test_calculator_fix_simple.py` (6.8K, JSON deserialization regression test for a specific bug)
- `test_calculators_correct_params.py` (5K, correct-parameter validation)
- `test_calculators_direct.py` (7.5K, direct function tests)
- `test_parameter_mapping.py` (8.5K, parameter mapping utility)
- `test_shopify_calculator_tools.py` (16K, Shopify calculator tools)
- `test_shopify_calculators_no_db.py` (8K, Shopify calculators without DB)
- `test_group5_calculator1_luxury_pull_up_banners.py` (7.5K, Group 5 specific)
- `test_group5_calculator2_selfie_frames.py` (7.5K, Group 5 specific)
- `test_group5_calculators3_4_5.py` (8.3K, Group 5 specific)
- `discover_calculator_parameters.py` (11K, calculator parameter introspection utility)

**1 recent frontend test (must stay):**
- `verify_settings_save_flow.js` — added in commit `6380511a` (June 11, 2026). Node.js test for the AI settings save flow. Uses `require('fs')` + mocked DOM + mocked fetch. Not importable from Python, so it doesn't trigger the `from tests.X` heuristic — but is a real, valid test for the SPA.

### 4.2 ARCHIVE (2 files — dead, preserved in git history)

| File | Size | Why dead |
|---|---:|---|
| `tests/test_inhouse_calculator_fix.py` | **17,488,942 bytes (17.5 MB)** | **Not a Python file.** A test log (Python `print(WARNING)` output) accidentally committed with a `.py` extension. Verified by `grep -c "^(import\|from\|def\|class\|print)"` → **0** Python code lines. 242 lines × ~72KB/line, every line consists of repeated `[WARN]` characters. The only "import" in the file is a self-referential docstring: `python test_inhouse_calculator_fix.py`. The only "reference" to this filename in the repo is in its own docstring. **Moving this file shrinks the `tests/` directory by ~97%.** |
| `tests/test_all_calculators_with_fred_db.py` | 9,216 bytes (9K) | Imports `from inhouse_modules.db_connector import InHousePrintDB` and `from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator`. **Neither path exists** in the live code (verified `find . -maxdepth 4 -type d -name inhouse_modules` → no hits). "FRED" is the legacy InHouse Print system, superseded by Supabase + AI-agents per CLAUDE.md §1. **The script would raise `ImportError` on first import.** |

**Move target:** `archive/top_level_tests_row42_dead/` (new subdir, per row 43/44/45/48 precedent of dated/row-tagged bundle names).

### 4.3 OUT OF SCOPE (flagged for future rows)

| Item | Location | Future row |
|---|---|---|
| `tests/calculators/` (subdir) | 13 pytest-style alignment tests | future "pytest infrastructure" row (not yet scheduled) |
| Top-level `test_inhouse_calculator_fix.py` (9.5K, real test — **different** file from the 17.5MB log) | repo root, not in `tests/` | row 40 (one-shot scripts) — will eventually check if this 9.5K file is also a candidate |
| 12 standalone calculator tests kept conservatively in §4.1 | `tests/test_*.py` | could be re-evaluated when `tests/calculators/` (pytest) infra is audited |

---

## 5. CLAUDE.md updates

CLAUDE.md §3 line 195-202 lists the 5 calculator test runners. **All 5 are kept in this row** — no change needed. A brief audit-completion note can be added.

| Line | Section | Change |
|---|---|---|
| 195 | §3 "Tests" | Add a note: "Row 42 audit (June 12, 2026) verified these 5 are the only top-level `tests/` scripts documented in CLAUDE.md; 2 dead files moved to `archive/top_level_tests_row42_dead/` (17.5MB log + 9K FRED-system test); 24 other top-level test files remain as load-bearing or recently-validated" |

---

## 6. Files moved (chain of custody)

| # | From | To | Notes |
|---|---|---|---|
| 1 | `tests/test_inhouse_calculator_fix.py` | `archive/top_level_tests_row42_dead/test_inhouse_calculator_fix.py` | 17.5MB log file; 0 Python code |
| 2 | `tests/test_all_calculators_with_fred_db.py` | `archive/top_level_tests_row42_dead/test_all_calculators_with_fred_db.py` | 9K; uses non-existent inhouse_modules |

**Plus 1 DEPRECATION_NOTICE.md created** at `archive/top_level_tests_row42_dead/DEPRECATION_NOTICE.md` (following the row 43/44/45/48 precedent).

**Plus 1 CLAUDE.md update** (line 195, §3 Tests).

**Plus 1 findings doc** (this file).

**Plus 1 tracker update** (row 42 → DONE).

**Total: 3 file modifications, 1 new doc, 2 commits.**

Commit chain on `cleanup/top-tests-cleanup`:
- `847dd8f8` chore(cleanup/top-tests-cleanup): row 42 — claim, scope top-level tests/ cleanup
- `86afbef2` chore(cleanup/top-tests-cleanup): row 42 — move 2 dead top-level test files under archive
- (pending) row 42 — stamp CLAUDE.md, log findings, mark DONE

---

## 7. Verification

| Check | Result |
|---|---|
| `git grep "from tests\." .` (worktree) | 0 hits (no live importer) |
| `find tests/ -maxdepth 1 -type f -name "*.py" -o -name "*.js"` (after move) | 28 .py + 1 .js (was 30 .py + 1 .js) |
| `du -sh tests/` (after move) | 376K (was ~17.9M, **97.9% reduction**) |
| `ls archive/top_level_tests_row42_dead/` | DEPRECATION_NOTICE.md + 2 dead files |
| `find . -name "test_inhouse_calculator_fix.py"` | 1 hit in archive; 1 separate top-level 9.5K file (out of scope, not the same file) |
| `find . -name "test_all_calculators_with_fred_db.py"` | 1 hit in archive (no other occurrences) |
| `git status` (post-move) | clean (2 commits on `cleanup/top-tests-cleanup`) |
| 5 documented runners still present | ✓ (run_all_tests.py, run_group2/3/4/5_tests.py all intact) |
| 4 subprocess-called tests still present | ✓ (test_persistent_semantic_smoke/compile/endpoint/e2e.py) |

---

## 8. References

- **Tracker row:** row 42 of `ARCHIVE_CLEANUP_TRACKER.md` (status: DONE)
- **Branch:** `cleanup/top-tests-cleanup` (off `cleanup/core-archived-freeze`)
- **Deprecation notice:** `archive/top_level_tests_row42_dead/DEPRECATION_NOTICE.md`
- **CLAUDE.md update:** §3 line 195
- **Related rows:** row 40 (one-shot scripts — will eventually check the 9.5K top-level `test_inhouse_calculator_fix.py`); row 49 (copilot-instructions.md rewrite — DEFERRED)
