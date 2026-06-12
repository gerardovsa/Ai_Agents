# Row 51 deprecation notice — 1,225 root `.md` files extracted

**Date:** 2026-06-12
**Row:** 51 (promoted from F4)
**Author:** Claude (cleanup session, branch `cleanup/root-md-cleanup`)
**Scope:** all 1,236 root-level `*.md` files at the start of the audit. **1,225 archived**, **11 kept at root**.

---

## What was moved

| Bucket | Count | Action | Target |
|---|---:|---|---|
| Contract | 7 | keep at root | `*.md` (root) |
| Runbook | 4 | keep at root | `*.md` (root) |
| Scratch | 422 | archive | `archive/timelines_and_reports/` |
| Historical | 341 | archive | `archive/timelines_and_reports/` |
| Debug | 29 | archive | `archive/analysis_reports/` |
| Suspicious | 433 | archive | `archive/timelines_and_reports/` |
| **Total** | **1,236** | | |

## Files kept at root (11)

| File | Why kept |
|---|---|
| `README.md` | Contract — main entry point |
| `README_V11.md` | Contract — V11 entry point |
| `CLAUDE.md` | Contract — agent instructions |
| `LICENSE` | (not present in repo; listed in per-feature hard rules) |
| `ARCHIVE_CLEANUP_PLAN.md` | Contract — the cleanup plan itself |
| `ARCHIVE_CLEANUP_SUMMARY_NOV30.md` | Contract — last cleanup summary |
| `ARCHIVE_CLEANUP_TRACKER.md` | Contract — live tracker |
| `ARCHIVE_SAFETY_VERIFICATION.md` | Contract — safety verification checklist |
| `CUSTOMER_REACTIVATION_DEPLOYMENT.md` | Runbook — deployment steps |
| `MARKDOWN_EXTRACTION_DEPLOYMENT.md` | Runbook — deployment steps |
| `PERFORMANCE_OPTIMIZATION_DEPLOYMENT.md` | Runbook — deployment steps |
| `START_HERE.md` | Runbook — onboarding entry point |

## Files archived (1,225)

All archived files satisfy **at least one** of:

- **Filename matches a scratch/fix/progress/summary pattern** (e.g. `*_COMPLETE.md`, `*_FIX_*.md`, `*_PHASE_*.md`, `*_V\d_*.md`, `*_POST_MORTEM.md`, etc.) — 422 files in `Scratch` bucket
- **Filename contains a 2025 or earlier date stamp** (`_NOV17`, `_DEC10_2025`, `_2025-11-22`, etc.) — 341 files in `Historical` bucket
- **Filename matches debug/analysis/research patterns** (e.g. `*_ANALYSIS_*.md`, `*_INVESTIGATION.md`, `*_RESEARCH_*.md`, etc.) — 29 files in `Debug` bucket (moved to `archive/analysis_reports/`)
- **Topic-prefixed one-shot with no inbound reference from any active doc** (e.g. `AI_AGENTS.md`, `ARCHITECTURE.md`, `THREAD_SYSTEM.md`, `VECTOR_DATABASE.md`, `SYNERGY_COLLABORATION.md`, `AUTOMATION_WORKFLOWS.md`, `TRANSCRIPTION.md`, `MODULES.md`, `QUOTE_CALCULATOR.md`, `INHOUSE_PRINT.md`, `INHOUSE_KANBAN.md`, `PROMPT_CATALOGUE.md`, etc.) — 433 files in `Suspicious` bucket

## Inbound-reference audit (Suspicious bucket)

Before archiving, all 433 "suspicious" files were checked for inbound references from active docs:

- **CLAUDE.md** — 0 references
- **README.md** / **README_V11.md** — 0 references
- **`.github/copilot-instructions.md`** — 0 references to any specific root .md (all "ARCHITECTURE" hits are to `MODULE_VISIBILITY_ARCHITECTURE.md`)
- **`.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md`** — 14 references (this is itself a meta-instruction telling agents which docs to consolidate, **not** a production doc)
- **`.github/prompts/System_Architexture.prompt.md`** — 8 references (a prompt that generates ARCHITECTURE.md, not a doc that reads it)

**Conclusion:** None of the 433 "Suspicious" files (including the topic-prefixed ones that look canonical) are referenced from any active production doc. The classifier's aggressive archive is safe per CLAUDE.md §16.4 (single-source-of-truth) and §16.8 (doc safety).

## Chain of custody

- **Branch:** `cleanup/root-md-cleanup` (off `cleanup/root-one-shot-cleanup`)
- **Commits:** 43 (1 claim + 1 classification artifacts + 41 batches of ≤30)
- **Recovery:** `git log --diff-filter=R -- archive/timelines_and_reports/ | grep -E "^[a-f0-9]+ "` and `git log --diff-filter=R -- archive/analysis_reports/`

## How to recover a specific file

```bash
# Example: recover THREAD_SYSTEM.md
git mv archive/timelines_and_reports/THREAD_SYSTEM.md ./
```

All file history is preserved via `git mv`. The file's original commit chain is intact.

## Related rows

- **Row 50** (root `.py` one-shot cleanup, 428 files) — sibling cleanup, same intent
- **F4** (this row, promoted) — was the "root .md" followup in the tracker

## References

- Tracker row 51 of `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: `docs/agents/ROW_51_ROOT_MD_CLEANUP.md`
- Classification artifacts: `tmp_row51_inventory.csv`, `tmp_row51_classification.csv`, `tmp_row51_summary.txt`
