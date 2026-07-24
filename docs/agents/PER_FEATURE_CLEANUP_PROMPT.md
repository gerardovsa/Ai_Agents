# Per-Feature Cleanup Prompt
**Use:** Once per row in `ARCHIVE_CLEANUP_TRACKER.md`.
**Replaces:** None — this is the canonical per-feature prompt, updated for the June 2026 round to include code-tracing and unused-script detection.

---

```markdown
# Task: Process one row of the archive-cleanup tracker

You are processing **one** row of `ARCHIVE_CLEANUP_TRACKER.md` for the
`AI_agents_V11` project. The repo is a multi-tenant Flask + vanilla-JS SPA
on Supabase, deployed to Render from the `v11` branch.

## Inputs (filled in by the human)

- **`WORKING_DIR`**: the **staging copy** path, e.g.
  `C:\Users\gpoli\GIT\AI_Agents_V11 - Copy (15)\AI_agents\`. All file
  operations happen in this directory, never in the canonical repo.
- **Tracker row number**: `<N>` (e.g. `9`).
- **Feature / area**: `<feature-slug>` (e.g. `shopify`).
- **Feature description**: `<copy from the tracker row Notes column>`.
- **Scope**: one of `docs` | `code` | `code+docs` | `code-trace` | `meta`.
- **Working branch**: `cleanup/<feature-slug>`.

If any input is blank or ambiguous, **stop and ask**.

## Authoritative context — read these first, in order

1. `ARCHIVE_CLEANUP_TRACKER.md` — confirm the row is `TODO` and that no
   one else has `CLAIMED` it. If a collision, the **earlier timestamp**
   in the `Owner` column wins; pick a different row.
2. `CLAUDE.md` — at minimum:
   - §2 (Repository Structure)
   - §13 (Known Risks) — read every risk that touches your row
   - §16 (Documentation Maintenance Workflow) — full read
   - §17 (Quick Reference)
3. The companion docs at the top of `CLAUDE.md` — only the ones
   relevant to your feature. Most features touch
   `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` and/or
   `VECTOR_DB_DEVELOPER_REFERENCE.md`.
4. The precedent cleanup files: `ARCHIVE_CLEANUP_PLAN.md`,
   `ARCHIVE_CLEANUP_SUMMARY_NOV30.md`, `ARCHIVE_SAFETY_VERIFICATION.md`
   (skim only).

## What to do

### Step 0 — Switch to the staging copy

```powershell
cd $WORKING_DIR
git status
git checkout -b cleanup/<feature-slug>
```

Verify you are in the staging copy, not the canonical repo, before
touching anything.

### Step 1 — Claim the row

Edit `ARCHIVE_CLEANUP_TRACKER.md`:

- `Status` → `CLAIMED`
- `Owner` → your session/agent ID
- `Branch` → `cleanup/<feature-slug>`

Commit: `chore(cleanup/<slug>): claim row N`.
Push the branch to your fork or to a remote in the staging copy.

### Step 2 — Inventory within scope

Run inside the staging copy. Adapt the paths to the row's
`Code paths involved` from the tracker.

```powershell
# All files under the feature
Get-ChildItem -Path "<feature-path>" -Recurse -File |
  Select-Object FullName, Length, LastWriteTime

# Just docs
Get-ChildItem -Path "<feature-path>" -Recurse -Include *.md -File |
  Select-Object FullName, Length, LastWriteTime

# Python scripts
Get-ChildItem -Path "<feature-path>" -Recurse -Include *.py -File |
  Where-Object { $_.Name -notlike '__init__.py' } |
  Select-Object FullName, LastWriteTime

# JS / HTML / CSS / SQL
Get-ChildItem -Path "<feature-path>" -Recurse -Include *.js,*.html,*.css,*.sql -File |
  Select-Object FullName, LastWriteTime
```

For `code-trace` and `meta` rows, expand the path to cover the **whole
feature graph** — every directory the row's `Code paths involved`
column mentions.

### Step 3 — Build the trace map (code-trace rows only)

This is the core of the per-feature work. The map has five sections.
**You must produce all five**, even if some are empty.

```markdown
### Trace map for <feature>

**Files involved (verified live):**
- `path/to/file.py` — imported by [list of importers], referenced in
  [docs/route/callers]
- ...

**Files involved (orphaned, candidate for archive):**
- `path/to/old_script.py` — last modified 2025-09-14, no importers,
  no doc references, not in any task/workflow
- ...

**Doc claims verified:**
- ✅ `<doc claim>` confirmed by `path/to/code.py:line`
- ❌ `<doc claim>` contradicted by `path/to/code.py:line` —
  RECOMMEND: update the doc

**Code claims verified:**
- ✅ `<doc path>` still exists
- ❌ `<doc path>` no longer exists — RECOMMEND: update the doc to
  remove the reference

**Dead code found (scripts that don't seem to be imported or referenced):**
- `path/to/dead.py` — heuristic: no importer, no doc ref, not in
  `.vscode/tasks.json`, not in `.github/workflows/`, last modified
  >6 months ago
- ...

**Dead docs found (files that contradict current code or are stale fix logs):**
- `path/to/stale.md` — last touched >6 months, contradicts migration 051
- ...
```

**Heuristics for "dead":**
- **Python script**: not imported by any other .py file (Grep for the
  filename without extension AND for unique class/function names).
  Not referenced in `.vscode/tasks.json`, `.github/workflows/*.yml`,
  `package.json` scripts, or any .md doc. Last modified >6 months.
- **Markdown doc**: not linked from any other .md, .html, or .py doc
  string. Not referenced in `CLAUDE.md` or
  `.github/copilot-instructions.md`. Not the target of a relative
  link in the frontend. Last modified >6 months.
- **Top-level fix log** (e.g. `WELCOME_TO_PRIME_FIX_COMPLETE.md`):
  the fix is older than the most recent migration that touches the
  fixed code → candidate for `docs/archive/`.

If uncertain, mark `Suspicious` and **do not move it**. The human
decides.

### Step 4 — Classify every .md (per CLAUDE.md §16.3)

For each .md in scope, pick exactly one:

| Bucket | Definition | Default action |
|---|---|---|
| **Canonical** | Single source of truth, current | Keep at original location |
| **Historical** | Once correct, now superseded | Move to `docs/archive/` or `archive/documentation/` |
| **Scratch** | Debug log, fix summary, not durable | Move to `docs/archive/` |
| **Deprecated** | Documents a removed feature | Move to `archive/deprecated/<YYYY-MM-DD>/` |
| **Debug / personal notes** | One-purpose analysis | Move to `archive/analysis_reports/` |
| **Contract** | Code expects a fixed path | Never archive |
| **Runbook** | Step-by-step ops procedure | Keep at root or `docs/` |

### Step 5 — Verify code claims (for `code-trace` and `code+docs` rows)

For every **Canonical** doc, sample-check 2–3 facts:

- Cited file paths exist (`Test-Path`).
- Cited function/class still exists (`Grep`).
- Cited migration still exists.
- Cited env var or table column still exists.

If a Canonical doc fails verification, surface the contradiction in
the report — **do not silently fix the doc**. The human decides
which side is right (per CLAUDE.md §16.4 precedence:
migrations > code > newest analysis > most-recent updated > PR author).

### Step 6 — Propose, then execute

Produce this table in your report:

| File | Current path | Bucket | Proposed action | Proposed path | Risk | Notes |
|------|--------------|--------|-----------------|---------------|------|-------|

Where **proposed action** is one of:
- `keep` (no change)
- `git mv` to a path in `archive/<category>/` (for code)
- `git mv` to `docs/archive/` (for general docs)
- `git mv` to `docs/<topic>/archive/` (for topic docs)
- `git mv` to `archive/deprecated/<YYYY-MM-DD>/` with a new
  `DEPRECATION_NOTICE.md` (for feature retirement)
- Prefix rename to `_ARCHIVED_<name>.md` (in-place, for still-linked docs)
- `merge` into another Canonical doc (specify the survivor)
- `delete` (only if already in `archive/deprecated/` and human has
  approved the deletion)

Then execute the proposed moves with `git mv` only — **never `rm`**.

If the table is larger than 30 files, **stop and ask the human** before
executing. Break it into batches of ≤30 and report per batch.

**Use the destination rules from the tracker:**

- Code → `archive/<category>/`
- General docs → `docs/archive/`
- Topic docs → `docs/<topic>/archive/`
- Feature retirement → `archive/deprecated/<YYYY-MM-DD>/`

### Step 7 — Update inbound cross-references

After every move, search for inbound references:

```powershell
# Find files that link to or mention the moved path
Grep -r "<old_relative_path>" --include=*.md --include=*.html --include=*.py
```

For each hit, decide: update the link, or note the link rot for the
`copilot-instructions.md` rewrite (tracker row 49).

Also update `CLAUDE.md` if it references the moved doc.

### Step 8 — Update the tracker

Edit `ARCHIVE_CLEANUP_TRACKER.md`:

- Target row `Status` → `DONE` (or `SKIPPED` with reason, or
  `BLOCKED` with disposition).
- Add a one-line entry to **Chain of custody**:
  `YYYY-MM-DD | <feature> | cleanup/<slug> | <PR-link> | <files-moved count> | DONE`

Commit: `chore(cleanup/<slug>): row N done (<files-moved> files)`.
Push the branch.

### Step 9 — Final report

The report to the human must include:

1. **Claimed row number** and your session ID.
2. **Trace map** (Step 3) — full, all 5 sections, even if empty.
3. **Proposed-action table** (Step 6) — full.
4. **Files moved**: count and list.
5. **Files kept**: count.
6. **Files marked Suspicious**: list with reason.
7. **Inbound links updated**: count and the surviving docs.
8. **Doc/code contradictions found**: list, with your recommendation
   per CLAUDE.md §16.4 precedence.
9. **PR link** in the staging copy.
10. **Risks** (anything you did not verify).
11. **Suggested next row** in the tracker.

## Hard rules (from CLAUDE.md §16.8)

- Never `rm` a file. Always `git mv`.
- Never delete a `.md` file just because it is old.
- Never break inbound links silently — fix them or note the rot.
- Never touch `README.md`, `README_V11.md`, `LICENSE`,
  `requirements.txt`, `package.json`, `runtime.txt`,
  `.env.example`, `.env.master`.
- Never consolidate two docs that disagree — surface the conflict.
- Never move a file that the agent's own tools or other code still
  imports.
- Never delete `archive/` subdirectories en masse.
- Never modify a doc named in `ARCHIVE_CLEANUP_PLAN.md` if that plan
  is still active.
- Never modify `ARCHIVE_CLEANUP_TRACKER.md` rows that aren't yours.
  Append-only to the chain of custody.
- If your feature touches `agent_routes_v4.py` or any file with
  hardcoded `user_id = 1`, **stop and report** — that is a security
  smell, not a cleanup candidate.
- **Work in the staging copy only** (`$WORKING_DIR`). Never modify
  the canonical `AI_Agents_V11` directly.

## Out of scope

- Other rows in the tracker.
- `node_modules/`, `.git/`, `.pytest_cache/`, `.vscode/`, `__pycache__/`.
- BGE model files at `/data/vdb_models/` or `~/.cache/vdb_models/`.
- The `archive/` and `docs/archive/` subdirectories themselves
  (other than to add a new bundle for *this* feature).
- Runtime data dirs: `data/`, `exports/`, `logs/`, `templates/`,
  `marketing/`, `examples/`.

## Escalation

If the feature is bigger than you can safely process in one session:

- Stop at Step 6 (the proposed table).
- Report what you found and what remains.
- Mark the row `BLOCKED` in the tracker with a reason.
- Suggest a sub-split (e.g. "split row N into Na and Nb") and add the
  new rows at the bottom of the tracker.
```
