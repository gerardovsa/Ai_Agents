# Deprecation Notice: `copilot-instructions.md.disabled`

**Date archived at this location:** June 12, 2026
**Originally disabled:** November 2025
**Status:** RETIRED — superseded by `.github/copilot-instructions.md`

---

## What this file is

`copilot-instructions.md.disabled` is a **68K snapshot of the November 2025 version of `.github/copilot-instructions.md`**. It was the active instruction file for the GitHub Copilot coding agent during November 2025. In November 2025, it was renamed to `.disabled` (a common convention to keep the old version available while the new version took over).

By the time of this archive (June 12, 2026), the `.disabled` file had been sitting unchanged for **7+ months** in the `.github/` directory. Its purpose — as a rollback target if the new copilot-instructions.md had problems — was no longer serving any function, because the new file had been stable for many releases.

## Why it was moved

Per `ARCHIVE_CLEANUP_TRACKER.md` row 48, the spec was: "retire `copilot-instructions.md.disabled`". The hard rule from the per-feature cleanup prompt is **"never `rm`, always `git mv`"** — so the file was preserved in `git log` and on disk by moving it to this archive location.

## What replaced it

The active file is `.github/copilot-instructions.md` (60K as of June 12, 2026). It is the **source of truth** referenced from `CLAUDE.md` §1, §13, §16, §17, and elsewhere.

Note: `CLAUDE.md` also references `copilot-instructions.md` heavily, and is itself the **AI-agent equivalent** of `copilot-instructions.md` (per `CLAUDE.md` line 3: "Mirrors the intent of `.github/copilot-instructions.md` but is **scoped for AI-agent operation**"). Both will be updated as part of row 49 (rewriting `copilot-instructions.md` to point at canonical docs).

## How to recover

Preserved in `git log` history. To view the pre-archive state at the original `.github/` path:

```bash
git log --diff-filter=R -- archive/copilot-instructions_disabled_nov2025/
```

To see the file at its original path (`.github/copilot-instructions.md.disabled`):

```bash
git log --all -- '.github/copilot-instructions.md.disabled'
```

## References

- **Cleanup row:** row 48 of `ARCHIVE_CLEANUP_TRACKER.md` (batch 3)
- **Branch:** `cleanup/github-cleanup` (commit pending in this batch)
- **Originally disabled:** Nov 2025 (7+ months of stability before retirement)
