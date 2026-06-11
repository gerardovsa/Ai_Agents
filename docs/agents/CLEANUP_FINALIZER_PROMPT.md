# Cleanup Finalizer Prompt
**Use:** Run **once** at the end of a cleanup round to verify and write the round summary.
**Replaces:** None — this is the canonical finalizer prompt.
**Created:** 2026-06-11.

---

```markdown
# Task: Finalize the archive-cleanup round for AI_agents_V11

You are closing out the active round of the archive-cleanup tracker for
`AI_agents_V11`. The repo is a multi-tenant Flask + vanilla-JS SPA on
Supabase, deployed to Render from the `v11` branch.

## Authoritative context

1. `ARCHIVE_CLEANUP_TRACKER.md` (the tracker). Confirm every row is in a
   terminal state (`DONE`, `SKIPPED` with reason, or `BLOCKED` with
   disposition).
2. `CLAUDE.md` §16 (Documentation Maintenance Workflow) — especially
   §16.10 "Definition of clean".
3. The chain-of-custody log at the bottom of the tracker.
4. The three precedent cleanup files: `ARCHIVE_CLEANUP_PLAN.md`,
   `ARCHIVE_CLEANUP_SUMMARY_NOV30.md`, `ARCHIVE_SAFETY_VERIFICATION.md`.
5. The companion prompt files at `docs/agents/`:
   - `PER_FEATURE_CLEANUP_PROMPT.md`
   - `CLEANUP_BOOTSTRAP_PROMPT.md`
   - `CLEANUP_FINALIZER_PROMPT.md` (this file)

## What to do

### Step 1 — Verify the tracker

For every row:

- `Status` is one of: `DONE`, `SKIPPED`, `BLOCKED`.
- For `DONE`: the `PR` column is filled, the chain-of-custody has an
  entry, and the branch has been merged (or is in the queue to merge —
  flag for the human).
- For `SKIPPED`: the `Notes` column has a one-line reason.
- For `BLOCKED`: the `Notes` column has a disposition
  (e.g. "split into rows 14a/14b and re-queued").

If any row is in `TODO` / `CLAIMED` / `IN_PROGRESS`, stop and tell
the human which rows are still open.

### Step 2 — Run the §16.10 cleanup checks

For each item in the §16.10 "Definition of clean" checklist, run the
check and report PASS/FAIL:

- **Repo-root `.md` count is bounded.** Should be small — most should
  be Contract or Canonical. Report the count.
- **Every link in `CLAUDE.md` and `.github/copilot-instructions.md`
  resolves to an existing file.** Use `Grep` for the paths and
  `Test-Path` for the targets.
- **No `from AI_infrastructure.core.archived.X` or
  `from core.archived.X` imports anywhere in live code**
  (`Grep` for `from .*archived`).
- **No `import` / `from … import` references any path under
  `archive/`** (`Grep` for `archive/...` in Python imports).
- **No hardcoded `user_id = 1`** outside of test fixtures and the
  explicit fallback in `agent_routes_v4.py`.
- **No live code imports from `archive/`** (covered by the bullet above;
  restate for emphasis).
- **The new authoritative docs**
  (`ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`,
  `VECTOR_DB_DEVELOPER_REFERENCE.md`, `CLAUDE.md`,
  `README_V11.md`) **do not contradict each other** on any fact you
  can spot-check.

### Step 3 — Run the smoke test (per CLAUDE.md §13)

These are quick "did we break anything" checks. Run each and report
the output:

```powershell
# Backend boots & can talk to the DB
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT 1', fetch_mode='value'))"

# Tool registry is intact
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(len(r.tools))"

# No connection leaks introduced
python AI_infrastructure/tools/audit_connection_leaks.py

# No BOM introduced
.\.vscode\fix-bom.ps1
```

If any of these fail, mark the round `INCOMPLETE` and surface the
failure. Do not proceed to Step 4.

### Step 4 — Write the round summary

Create `ARCHIVE_CLEANUP_SUMMARY_<YYYY-MM-DD>.md` at the repo root, modeled
on `ARCHIVE_CLEANUP_SUMMARY_NOV30.md`. Use the current date in the
filename (e.g. `ARCHIVE_CLEANUP_SUMMARY_JUN11_2026.md`). Include:

- **Round scope** — date, owner, the row count of the plan.
- **Per-row disposition** — for each row: DONE / SKIPPED / BLOCKED +
  one-line summary + PR link.
- **Totals** — files moved, files kept, inbound links fixed, docs
  consolidated, scripts archived, doc/code contradictions surfaced.
- **§16.10 checklist results** — PASS/FAIL for each item.
- **Smoke test results** — PASS/FAIL for each smoke check.
- **Residual risks** — anything that needs a future round.
- **Chain-of-custody copy** — append the full log from the tracker so
  the summary is self-contained.
- **Recommended next round** — what to tackle next time.

### Step 5 — Update the tracker

Mark the entire round as finalised. Edit the header section of the
tracker:

- Change `Active round:` line to:
  ```
  Active round: <MONTH> <YEAR> — FINALISED <YYYY-MM-DD> (see ARCHIVE_CLEANUP_SUMMARY_<YYYY-MM-DD>.md)
  ```

### Step 6 — Report

- Path of the new summary file.
- The §16.10 PASS/FAIL table.
- The smoke-test PASS/FAIL table.
- The PR link for the summary.
- Any items that did not pass, with the human's decision required.

## Hard rules

- Do not start a new round. The point of the finalizer is to close
  *this* round, not open the next one.
- Do not modify any per-feature branch. The summary is the only
  new artefact.
- If the §16.10 checks fail, write the summary anyway, but mark the
  round as `INCOMPLETE` at the top and list what still needs work.
- If the smoke test fails, the round is `INCOMPLETE`. Do not finalise.
- The finalizer is read-only against the per-feature branches — it
  only writes the summary and updates the tracker's header.
```
