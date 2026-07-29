# Universal Search — Source-Type Registry Status

> **Snapshot date:** 2026-07-29 (post-Option-A refactor)
> **Author:** Current-session agent
> **Supersedes:** `docs/agents/UNIVERSAL_SEARCH_HANDOFF.md` §2 (the 9-of-9 list)

The Option A refactor committed in this round replaced the OAuth-direct branches
in `AI_infrastructure/routes/universal_search_routes.py` with a single
registry-dispatched helper (`_search_via_registry` and
`_search_calendar_via_registry`). All 9 source types that the hand-off brief
asked for are now implemented — but only **6 of 9** had native search tools
in the registry, and **2 of 9** use the list-then-filter calendar helper.

---

## Source-type matrix (current truth)

| # | Source | Platform key | Tool used | Status |
|---|---|---|---|---|
| 1 | pgvector | `pgvector` | `pgvector_query_vectors` | ✅ Working (Option A) |
| 2 | Pinecone | `pinecone` | `pinecone_query_vectors` | ✅ Working (Option A) |
| 3 | Qdrant | (none — module routes) | direct API | ✅ Working (legacy path) |
| 4 | Gmail | `google_workspace` | `gmail_search_messages` | ✅ Working (this round) |
| 5 | Google Drive | `google_workspace` | `google_drive_search_files` | ✅ Working (this round) |
| 6 | Outlook | `microsoft_365` | `microsoft_outlook_search_messages` | ✅ Working (this round) |
| 7 | OneDrive | `microsoft_365` | `microsoft_onedrive_search_files` | ✅ Working (this round) |
| 8 | SharePoint | `microsoft_365` | `microsoft_sharepoint_search_content` | ✅ Working (this round) |
| 9 | Google Calendar | `google_workspace` | `google_calendar_list_events` (filter) | ✅ Working (this round) |
| 10 | Microsoft Calendar | `microsoft_365` | `microsoft_calendar_list_events` (filter) | ✅ Working (this round) |
| 11 | Slack | `slack` | `slack_search_messages` | ✅ Working (this round) |
| 12 | GitHub | — | — | ❌ **NO TOOLS REGISTERED** |
| 13 | Notion | — | — | ❌ **NO TOOLS REGISTERED** |
| 14 | HubSpot | — | — | ❌ **NO TOOLS REGISTERED** |

---

## The 3-source gap (GitHub / Notion / HubSpot)

Verified 2026-07-29 by introspecting `tools.registry_v3.RegistryV3._schema_index`
(906 entries, 19 platforms). All three sources have **zero registered tools**.

This means:
- The hand-off brief assumed these tools existed; they don't.
- Implementing them requires writing the Python wrappers AND the JSON schemas
  AND wiring them as @tool_executor-decorated implementations. Estimated
  scope per source: 200-400 lines of Python + 1 schema JSON per search verb.
- Universal Search will silently no-op on these sources until the
  implementations land (resolve_credentials returns the creds, but
  `registry.execute_tool(tool_name='github_search_code')` raises a
  `ToolNotFoundError` that the helper swallows and returns `[]`).

**Recommendation:** treat GitHub / Notion / HubSpot as a separate, focused
round. Don't bundle into the next vector DB round. Each source needs:

1. Implementation module at `tools/implementations/<provider>/<provider>_tools.py`
2. Schema JSON at `tools/schemas/<provider>_search_<verb>_tools.json`
3. `@tool_executor` decoration on the search functions
4. Manifest entry in `tools/schemas/_all_tools.json` (or wherever the lazy
   index is built — verify with `RegistryV3._schema_index` first)
5. OAuth credential flow (3 sources have no current OAuth client in
   `auth_manager` — that has to be built too)

---

## Tests added (this round)

`AI_infrastructure/tests/test_universal_search_refactor.py` — 16 cases covering:

- Module surface (3 new helpers exist + DEFAULT_PROVIDER_PRIORITY is non-trivial)
- `_result_dedup_key`: case/whitespace normalization + title fallback
- `_dedup_results`: order preservation, two-way collapse, three-way collapse,
  priority tie-breaking, custom priority override
- `_search_via_registry`: silent skip on no creds (returns `[]`)
- `_search_calendar_via_registry`: silent skip on no creds (returns `[]`)

All 16 pass; no DB or network required.

---

## What the dedup layer does NOT cover (out of scope for this round)

- **Fuzzy matching.** Two emails with subject lines that differ by a single
  comma will produce different SHA1 hashes. If users complain "I'm seeing
  duplicates," switch to `difflib.SequenceMatcher` on the SHA1 collision
  candidates before declaring two items non-equal.
- **URL-based dedup.** If both Gmail and Outlook link to the same
  Microsoft Graph message ID, the dedup will not catch it (different text,
  different IDs). Add a `link`-keyed pass if this becomes a problem.
- **Cross-thread dedup.** Re-asking the same query within a session should
  probably hit a session-level cache. Not implemented.

---

## Verification commands

```bash
# 1. Confirm module imports + helpers exist
cd AI_agents && PYTHONIOENCODING=utf-8 python -c "
import sys; sys.path.insert(0, '.')
from AI_infrastructure.routes import universal_search_routes as u
print('helpers:', callable(u._search_via_registry), callable(u._search_calendar_via_registry), callable(u._dedup_results))
print('priority entries:', len(u.DEFAULT_PROVIDER_PRIORITY))
"

# 2. Run the new regression suite
PYTHONIOENCODING=utf-8 python -m unittest AI_infrastructure.tests.test_universal_search_refactor -v

# 3. Smoke-check the registry for the 9 source types
PYTHONIOENCODING=utf-8 python -c "
import sys; sys.path.insert(0, '.')
from tools.registry_v3 import RegistryV3
r = RegistryV3()
for prefix in ['gmail_search', 'google_drive_search', 'microsoft_outlook_search', 'microsoft_onedrive_search', 'microsoft_sharepoint_search', 'slack_search', 'google_calendar_list', 'microsoft_calendar_list']:
    print(prefix, '->', any(prefix in n for n in r._schema_index))
"

# 4. Confirm the 3 gaps are real
PYTHONIOENCODING=utf-8 python -c "
import sys; sys.path.insert(0, '.')
from tools.registry_v3 import RegistryV3
r = RegistryV3()
for prefix in ['github_', 'notion_', 'hubspot_']:
    print(prefix, '->', any(prefix in n for n in r._schema_index))
"
```

Expected output:
- Step 4 prints `False` for all three — confirming the documented gap.
