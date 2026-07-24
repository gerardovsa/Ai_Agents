# Cleanup Bootstrap Prompt
**Use:** Run **once** at the start of a cleanup round to seed `ARCHIVE_CLEANUP_TRACKER.md`.
**Replaces:** None — this is the canonical bootstrap prompt.
**Created:** 2026-06-11.

---

```markdown
# Task: Bootstrap the archive-cleanup tracker

You are bootstrapping a documentation + unused-script cleanup pass for the
`AI_agents_V11` repository at `c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents`
(Windows, PowerShell + bash available, Python 3.13). This is a multi-tenant
Flask + vanilla-JS SPA on Supabase. Repo currently has ~1,240 .md files at
the root plus many subdirectories.

## Authoritative context — read these first

1. `CLAUDE.md` (especially §16 "Documentation Maintenance Workflow" and
   §17 "Quick Reference").
2. The companion docs at the top of `CLAUDE.md` — note especially
   `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` and
   `VECTOR_DB_DEVELOPER_REFERENCE.md`.
3. The precedent cleanup files if they exist:
   `ARCHIVE_CLEANUP_PLAN.md`, `ARCHIVE_CLEANUP_SUMMARY_NOV30.md`,
   `ARCHIVE_SAFETY_VERIFICATION.md`.
4. The companion cleanup prompt files at `docs/agents/`:
   - `PER_FEATURE_CLEANUP_PROMPT.md` (for each per-feature pass)
   - `CLEANUP_BOOTSTRAP_PROMPT.md` (this file)
   - `CLEANUP_FINALIZER_PROMPT.md` (run once at the end)

## What to do

1. **Verify `ARCHIVE_CLEANUP_TRACKER.md` does not exist** at the repo
   root (or at the working copy if you are working in a worktree).
   If it does, stop and tell the user.
2. **Read the project's own existing cleanup files** (if any of the three
   precedent files above exist) and pull any "TODO" items they reference
   into the new tracker.
3. **Run a quick PowerShell inventory** to get accurate counts:
   ```powershell
   Get-ChildItem -Recurse -Include *.md -File | Measure-Object
   Get-ChildItem -Path . -Filter *.md -File | Measure-Object
   Get-ChildItem archive/documentation 2>$null | Measure-Object
   Get-ChildItem docs/archive 2>$null | Measure-Object
   Get-ChildItem AI_infrastructure/migrations/*.sql 2>$null | Measure-Object
   ```
4. **Create `ARCHIVE_CLEANUP_TRACKER.md` at the working-directory root**,
   using the structure in the existing tracker (see Section template
   below). Fill in:
   - The **Last updated** date.
   - The **Active round** name.
   - The **Staging copy** path (or note if you are using a git worktree
     — see the "Staging copy vs worktree" section in this prompt).
   - The four PowerShell inventory numbers in the "Staging" notes
     section.
5. **Match the existing tracker template structure** if the file already
   exists from a prior round — the contract is that other agents will
   read and update it.
6. **Commit** the new file with message:
   `chore(docs): bootstrap ARCHIVE_CLEANUP_TRACKER.md (June 2026 round)`
7. **Open a PR** titled "Bootstrap archive cleanup tracker (June 2026)".
8. **Do not start any cleanup work in this session.**

## Tracker template (use this structure)

The tracker MUST contain these sections, in this order:

1. **Header** — title, last-updated date, owner, active round, staging
   copy / worktree path, and the warning that the file is not to be
   archived or moved.
2. **How to use this tracker** — the 7-step procedure (read §16 of
   CLAUDE.md, claim a row, branch, process, update, PR, etc.) plus the
   status-legend table and scope-legend table.
3. **Where to put archived files (the rule)** — the table mapping
   "what you're retiring" to "destination path."
4. **Master table** — organised into sections (subsystems, external
   modules, internal modules, top-level meta). One row per item.
5. **Per-feature "trace and verify" output template** — the trace-map
   template agents must use for `code-trace` rows.
6. **Chain of custody** — append-only log; one line per agent session.
7. **Definition of done for this round** — the explicit checklist.
8. **Out of scope** — the do-not-touch list.
9. **Conflict resolution** — the policy on row collisions and re-opens.
10. **Promote-to-canonical workflow** — how a staging-pass becomes a
    canonical change.

**The current canonical tracker has 49 rows in 4 sections.** Use the
same row structure and section names; update row descriptions to match
the new round if needed.

## Staging copy vs worktree (important)

There are two acceptable ways to do the per-feature work in isolation:

| Approach | When to use | Setup command |
|---|---|---|
| **File copy** (e.g. `AI_Agents_V11 - Copy (15)`) | Already in place, simple | Just work inside the copy |
| **Git worktree** (recommended) | Cleaner isolation, same git repo | `git worktree add <path> -b cleanup/<branch>` |

**Recommended: git worktree.** A worktree is a second working directory
on a different branch of the same git repo. Changes in one are isolated
until merged. A file copy is a literal duplicate — you have to manually
sync changes back.

If you set up a worktree, set the tracker's **Staging copy** line to
`Worktree: <path> on branch cleanup/<branch> (added via git worktree)`.
Otherwise set it to the literal file-copy path.

## Report

- Path of the created file (worktree path or canonical path).
- The four PowerShell inventory numbers.
- The PR link.
- Any deviations from the existing tracker template, with reason.
- The row count (should be 49 if following the existing template).
```
