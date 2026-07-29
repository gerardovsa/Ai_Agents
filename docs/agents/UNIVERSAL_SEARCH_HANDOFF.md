# Hand-off Brief: Universal Search Remaining Source Types + Result Dedup

> **Status:** Two of eleven source types implemented (pgvector, Pinecone). Nine remaining.
> **Author:** Prior session agent. Hand-off date: 2026-07-28.
> **Estimated scope:** 9 source branches × ~30 lines + 1 dedup layer + tests. Not trivial — do not budget as a one-shot.

---

## 1. Context (read first)

The Universal Search endpoint lives at `AI_infrastructure/routes/universal_search_routes.py`. It is a Flask route that fans out to multiple external sources, gathers results, and returns a unified list. The endpoint is registered against the blueprint and accepts a `query_text` plus a `limit`.

**Current state of the endpoint** (post 2026-07-28 fixes):

| Option | Source | Status | Implementation notes |
|---|---|---|---|
| 1 | pgvector (`ai_infrastructure.org_vector_documents`) | **Working** | Bugfixed 2026-07-28 — was hitting the empty `vector_embeddings` table. Now org-scoped with vector similarity > 0.3 threshold. |
| 2 | (other source — read endpoint to confirm what's currently a stub vs unimplemented) | TBD | Open the file and check the `if/elif` chain. Some branches may be TODO, some may be missing entirely. |
| 3 | Pinecone (4-tier cred resolver + registry dispatch) | **Working** | Was a TODO stub before 2026-07-28. Resolves credentials via `resolve_credentials(user_id, 'pinecone')`, dispatches via `registry.execute_tool(tool_name='pinecone_query_vectors', ...)`. Silent skip if no creds. |

**Open the file first.** The Option 2/3 numbering above may not match the file's option numbering — the source-type list is more important than the option numbers.

---

## 2. The nine remaining source types

Each of these needs a fan-out branch that follows the **same shape** as the pgvector and Pinecone branches already implemented. The shape is:

```python
# Pattern for each source — copy this template
try:
    # 1. Resolve credentials via the 4-tier resolver
    from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
    creds = resolve_credentials(user_id, '<platform_key>')
    if creds:
        # 2. Dispatch via the registry
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
        result = registry.execute_tool(
            tool_name='<platform>_<search_tool>',
            query=<query>,
            top_k=limit,
            _user_id=user_id,
            _injected_credentials=True,
        )
        # 3. Map result -> vector_results shape (id, title, text, provider, score)
        if result.get('success') and result.get('matches'):
            for m in result['matches']:
                vector_results.append({
                    'id': m.get('id'),
                    'title': m.get('title', m.get('subject', m.get('name', ''))),
                    'text': m.get('text', m.get('snippet', m.get('body', ''))),
                    'provider': '<platform>',
                    'score': m.get('score', 0.0),
                    'metadata': m.get('metadata', {}),
                })
except Exception as e:
    print(f'[UNIVERSAL SEARCH] <platform> search failed: {e}')
```

**Source types to implement** (in priority order — most commonly requested first):

| # | Source | Platform key | Expected tool name | Notes |
|---|---|---|---|---|
| 4 | Gmail | `google_workspace` | `gmail_search_messages` or `google_workspace_search_gmail` | Confirm exact registered name in `tools/implementations/google_workspace/`. |
| 5 | Google Drive | `google_workspace` | `google_drive_search_files` | Same — check the actual tool name. May be a single multi-tool for Google. |
| 6 | Outlook / OneDrive | `microsoft_365` | `outlook_search_messages` / `onedrive_search_files` | Same shape. |
| 7 | SharePoint | `microsoft_365` | `sharepoint_search_files` | Site-aware. |
| 8 | Calendar | `google_workspace` or `microsoft_365` | `calendar_search_events` | Probably one tool per provider. |
| 9 | Slack | `slack` | `slack_search_messages` | Requires Slack OAuth. |
| 10 | GitHub | `github` | `github_search_code` or `github_search_repos` | Two tools — pick the right one based on query intent. |
| 11 | Notion | `notion` | `notion_search_pages` | Requires Notion OAuth. |
| 12 | HubSpot | `hubspot` | `hubspot_search_contacts` or `hubspot_search_companies` | Two tools — pick by intent. |

> **Before writing any of these, verify the actual registered tool name** with:
> `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(sorted([n for n in r.tools if 'gmail' in n.lower()]))"`
> The names in the table above are educated guesses. Pin the real name before dispatching.

---

## 3. Result merging / dedup (separate concern)

After the nine branches are implemented, the endpoint will return more than the user expects when content exists in multiple sources (e.g., a contract as both a Gmail attachment and a Drive file). Current behavior: append blindly.

**Recommended dedup design:**

1. **Compute a content hash per result.** Use `hashlib.sha1(text.encode('utf-8')).hexdigest()` on the lowercased, whitespace-stripped `text` field. Fall back to `(title + provider)` hash if `text` is empty.
2. **Bucket results by hash.** Python `dict[hash, list[results]]`.
3. **Pick the winner per bucket:** max `score`, ties broken by `provider` priority order (pgvector > pinecone > drive > gmail > onedrive > outlook > github > notion > slack > calendar > hubspot — adjust by user request).
4. **Emit a `merged_from` field** on the surviving result: `[{'provider': 'gmail', 'id': '...'}, ...]` so the AI can cite sources.

**Place this in a new helper** — e.g. `_dedup_results(results: list, priority: list) -> list` at module scope — so the route stays readable. Add tests with a fixture of N=20 results across 5 sources and assert:
- No duplicate content survives
- `merged_from` lists every input that contributed
- Highest-score provider wins on ties

---

## 4. Tests required

For each new source branch, write a **unit test** at `AI_infrastructure/tests/test_universal_search_<source>.py` following the existing pattern in `test_pgvector_smart_tools.py`. Test scope:

- Source branch runs when creds are present and returns results in the documented shape.
- Source branch silently skips when creds are absent (no exception, no error in response).
- Source branch maps the platform's raw match shape → the `vector_results` dict shape (`id, title, text, provider, score, metadata`).
- No network or DB calls — mock the registry and credential resolver.

For the dedup layer:
- 20-result fixture covering 5 sources, 4 duplicate content groups.
- Assert no duplicates survive.
- Assert `merged_from` is populated for collapsed entries.
- Assert tie-breaking matches the priority order.

---

## 5. Don't-do list (hard constraints from CLAUDE.md)

- **Do NOT** add the 9 source branches to `SystemPromptBuilder` — it is dead code in production (see prior-session finding: only referenced from `core/archived/conversation_manager.py`). The live prompt builder is `UnifiedAIClient.get_system_prompt()` in `core/unified_ai_client.py:340`.
- **Do NOT** use `os.getenv` for any new platform credential — always `resolve_credentials(user_id, '<platform>')` (CLAUDE.md §4 4-tier resolver).
- **Do NOT** emit real error messages from the third-party API to the client — sanitize before returning (CLAUDE.md §9).
- **Do NOT** log message contents, PII, or full result text. Log provider + result count only.
- **Do NOT** call `process_streaming` / `UnifiedAIClient` from this endpoint — Universal Search is read-only and does not invoke the AI provider.

---

## 6. Definition of done

- [ ] All 9 source branches implemented and registered in the endpoint's `if/elif` chain.
- [ ] Result dedup layer added, with `merged_from` populated.
- [ ] One unit test per new source (no-network, mocked creds).
- [ ] Dedup test with 20-result fixture.
- [ ] Smoke check: `python -c "from AI_infrastructure.routes.universal_search_routes import ..."` succeeds.
- [ ] Smoke check: hit the running endpoint with a Flask test client and verify all 11 sources are reachable when creds are present (pgvector always reachable from DB).
- [ ] `git status` clean except for this round's files.
- [ ] Conventional Commits message drafted (`feat(universal-search): implement 9 remaining source types + result dedup`).
- [ ] `.\.vscode\fix-bom.ps1` run.

---

## 7. Related context (do not redo, but read first)

- **CLAUDE.md §4** — the 4-tier credential resolver (`org_credentials_loader.py`). Every new branch uses this.
- **CLAUDE.md §4** — RLS rules. The user_id must be `g.rls_user_id`, not a query param. The endpoint already uses `request.user.get('user_id')` (or similar) — confirm.
- **CLAUDE.md §13 risk #5** — BOM hygiene. Run `fix-bom.ps1` before every commit.
- **Prior-session note**: `unified_ai_client.py:340` is the actual prompt builder. If your work also touches prompt content, edit there, not in `SystemPromptBuilder`.
- **Prior-session note**: 4 Supabase DBs reachable. Confirm target before any DDL: `ryoicrdifiqhqpsnjmdo` is the AI Platform. Don't write to the MCP control plane (`qmeejvdpqftaynkijiae`) without explicit user confirmation.
- **Live MCP inventory**: CLAUDE.md §18 — `mcp__supabase-prod__` is the AI Platform; use it for verification queries against `ai_infrastructure.org_vector_documents`.

---

## 8. Open questions to flag to the user before starting

1. **Provider priority order for dedup ties** — the order in §3 is a guess. The user may want a different default (e.g., Gmail > Drive because Gmail is more recent activity).
2. **Result cap per source** — current endpoint fans out without per-source caps. Should each source be capped at `limit` before merge, or post-merge capped at the global `limit`?
3. **`merged_from` UX** — should the AI explain "I found this in 3 places" every time, or only when the user asks "where did you find this?" Recommend the latter to keep prompts lean.

Don't ask all three at once. Ask the priority question first, work it in, and surface the other two when their decision points arrive.
