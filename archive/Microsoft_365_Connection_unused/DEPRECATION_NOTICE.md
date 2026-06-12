# Deprecation Notice: `Microsoft_365_Connection/{email_sender,microsoft365_client,quote_request_processor,test_email_integration}.py`

**Date archived at this location:** June 12, 2026
**Status:** EXTRACTED from `Microsoft_365_Connection/` (not deleted — preserved here for historical reference)

---

## What was extracted

4 Python files were extracted from the live `Microsoft_365_Connection/` directory. The directory itself was kept at the repo root because **`microsoft365_oauth_manager.py` is still actively imported** by:

- `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` (line 39) — the **current** route
- `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED copy.py` (line 37) — a ` copy.py` (historical duplicate)
- `AI_infrastructure/IMPORT_PATH_VERIFICATION_COMPLETE.md` (line 74) — historical doc

## What was extracted (and why)

The other 4 files in the directory were **not imported by any live code** (verified via `grep -rnE "^from Microsoft_365_Connection\." AI_infrastructure tools`):

| File | Size | Reason for extraction |
|---|---:|---|
| `email_sender.py` | 18K | No `from Microsoft_365_Connection.email_sender` anywhere |
| `microsoft365_client.py` | 35K | No `from Microsoft_365_Connection.microsoft365_client` anywhere |
| `quote_request_processor.py` | 16K | No `from Microsoft_365_Connection.quote_request_processor` anywhere |
| `test_email_integration.py` | 17K | Test script, but not referenced by any test runner |

These files may have been used in the past (e.g. by the now-archived `routes/microsoft_auth_routes_V2_FIXED copy.py` route, or by an earlier iteration of the Microsoft 365 integration). They are preserved in `git log` and on disk at this archive location.

## What's now in `Microsoft_365_Connection/`

After this extraction, the live directory contains only:

- `microsoft365_oauth_manager.py` (19K) — the **only load-bearing file**

This slim-down makes the boundary of what's "live" much clearer.

## How to recover

Preserved in `git log` history. To view the pre-extract state:

```bash
git log --diff-filter=R -- archive/Microsoft_365_Connection_unused/
```

To see the files at their original path:

```bash
git log --all -- 'Microsoft_365_Connection/email_sender.py'
```

## References

- **Cleanup row:** row 43 of `ARCHIVE_CLEANUP_TRACKER.md` (batch 2)
- **Branch:** `cleanup/integration-dirs-audit` (commit pending in this batch)
- **Audit doc:** `docs/agents/ROW_43_INTEGRATION_DIRS_AUDIT.md` (planned)
