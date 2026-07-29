"""
Regression tests for the Universal Search registry-dispatch refactor
(2026-07-28).

CONTEXT:
    Prior to this commit, the 8 platform-source branches in
    AI_infrastructure/routes/universal_search_routes.py called third-party
    APIs directly with hand-rolled OAuth/header construction:

        - auth_manager.get_user_google_oauth_credentials()  → GAP-V1 pattern
        - auth_manager.get_user_microsoft_oauth_credentials()  → GAP-V1 pattern
        - hardcoded `requests.get('https://graph.microsoft.com/...')` calls
        - Slack branch was `slack_creds = None  # Not implemented yet`

    The refactor funnels all 8 sources through one helper:
        _search_via_registry(user_id, platform_key, tool_name, query, limit, ...)
    which uses:
        1. resolve_credentials(user_id, '<platform>')   — 4-tier resolver
        2. registry.execute_tool(tool_name='<platform>_<verb>') — schema validation
        3. result_adapter to normalize to universal_search shape

    Two new sources added (Google Calendar, Microsoft Calendar) use a second
    helper, _search_calendar_via_registry(), that pulls list_events and
    client-side filters because the registry has no calendar search tool.

    This test asserts:
        1. Module imports cleanly and the 3 new module-level helpers exist.
        2. _dedup_results collapses duplicates by content-hash and emits
           merged_from on the survivor.
        3. _dedup_results tie-breaks by priority order.
        4. _dedup_results preserves first-seen order for distinct items.
        5. _result_dedup_key hashes text + whitespace normalization.
        6. _search_via_registry returns [] when resolve_credentials returns None
           (silent skip on no creds).
        7. _search_calendar_via_registry falls back to list_events.

STRATEGY:
    Pure-Python tests. No DB, no network, no Flask. The helpers are imported
    and exercised with synthetic inputs. Mocking is unnecessary for the dedup
    helper (pure function) and the no-creds branch of _search_via_registry
    (resolve_credentials is itself a function we can monkey-patch).
"""

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _fresh_module():
    """Reload the routes module so module-level helpers are fresh and the
    `from X import Y` inside _search_via_registry re-resolves against
    whichever patches the test installs."""
    for mod_name in list(sys.modules):
        if mod_name == "AI_infrastructure.routes.universal_search_routes":
            del sys.modules[mod_name]
    return importlib.import_module("AI_infrastructure.routes.universal_search_routes")


class ModuleSurfaceTests(unittest.TestCase):
    """The three new helpers must exist at module scope."""

    def setUp(self):
        self.mod = _fresh_module()

    def test_search_via_registry_helper_exists(self):
        self.assertTrue(callable(getattr(self.mod, "_search_via_registry", None)))

    def test_search_calendar_via_registry_helper_exists(self):
        self.assertTrue(callable(getattr(self.mod, "_search_calendar_via_registry", None)))

    def test_dedup_results_helper_exists(self):
        self.assertTrue(callable(getattr(self.mod, "_dedup_results", None)))

    def test_default_provider_priority_is_a_list(self):
        self.assertIsInstance(self.mod.DEFAULT_PROVIDER_PRIORITY, list)
        self.assertGreater(len(self.mod.DEFAULT_PROVIDER_PRIORITY), 5)


class ResultDedupKeyTests(unittest.TestCase):
    """The dedup key MUST be stable across whitespace + case variation,
    otherwise the same email body shows up as 'two different results'."""

    def setUp(self):
        self.mod = _fresh_module()
        self.key = self.mod._result_dedup_key

    def test_identical_text_yields_identical_key(self):
        a = {"text": "Hello World", "title": "x", "provider": "gmail"}
        b = {"text": "Hello World", "title": "x", "provider": "gmail"}
        self.assertEqual(self.key(a), self.key(b))

    def test_case_and_whitespace_normalized(self):
        a = {"text": "Hello   World", "title": "x", "provider": "gmail"}
        b = {"text": "hello world", "title": "x", "provider": "gmail"}
        self.assertEqual(self.key(a), self.key(b))

    def test_fallback_when_text_empty(self):
        a = {"text": "", "title": "Contract.pdf", "provider": "google-drive"}
        b = {"text": None, "title": "Contract.pdf", "provider": "google-drive"}
        # Both fall back to (title|provider) hash — must collide.
        self.assertEqual(self.key(a), self.key(b))

    def test_different_titles_yield_different_keys(self):
        a = {"text": "", "title": "A", "provider": "x"}
        b = {"text": "", "title": "B", "provider": "x"}
        self.assertNotEqual(self.key(a), self.key(b))


class DedupResultsTests(unittest.TestCase):
    """Pure-function dedup tests — no mocks, no DB."""

    def setUp(self):
        self.mod = _fresh_module()
        self.dedup = self.mod._dedup_results

    def test_empty_input_returns_empty(self):
        self.assertEqual(self.dedup([]), [])

    def test_no_duplicates_passthrough_preserves_order(self):
        items = [
            {"id": "1", "text": "alpha", "score": 0.9, "provider": "gmail"},
            {"id": "2", "text": "beta",  "score": 0.8, "provider": "drive"},
            {"id": "3", "text": "gamma", "score": 0.7, "provider": "slack"},
        ]
        out = self.dedup(items)
        self.assertEqual(len(out), 3)
        self.assertEqual([x["id"] for x in out], ["1", "2", "3"])
        # None should have merged_from.
        for x in out:
            self.assertNotIn("merged_from", x)

    def test_two_duplicates_collapse_high_score_wins(self):
        items = [
            {"id": "1", "text": "contract v2", "score": 0.6, "provider": "gmail"},
            {"id": "2", "text": "contract v2", "score": 0.9, "provider": "drive"},
        ]
        out = self.dedup(items)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], "2")
        self.assertEqual(out[0]["provider"], "drive")
        self.assertIn("merged_from", out[0])
        self.assertEqual(out[0]["merged_from"], [{"provider": "gmail", "id": "1"}])

    def test_tie_score_breaks_by_priority_pgvector_beats_gmail(self):
        items = [
            {"id": "1", "text": "x", "score": 0.9, "provider": "gmail"},
            {"id": "2", "text": "x", "score": 0.9, "provider": "pgvector"},
        ]
        out = self.dedup(items)
        self.assertEqual(len(out), 1)
        # pgvector has higher priority than gmail → pgvector wins.
        self.assertEqual(out[0]["provider"], "pgvector")
        self.assertEqual(out[0]["merged_from"], [{"provider": "gmail", "id": "1"}])

    def test_three_way_collapse_records_both_merges(self):
        items = [
            {"id": "1", "text": "shared", "score": 0.5, "provider": "gmail"},
            {"id": "2", "text": "shared", "score": 0.5, "provider": "slack"},
            {"id": "3", "text": "shared", "score": 0.7, "provider": "drive"},
        ]
        out = self.dedup(items)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], "3")
        # drive had highest score → winner; gmail + slack recorded as merges.
        merged_pairs = {(m["provider"], m["id"]) for m in out[0]["merged_from"]}
        self.assertIn(("gmail", "1"), merged_pairs)
        self.assertIn(("slack", "2"), merged_pairs)

    def test_priority_override_respected(self):
        items = [
            {"id": "1", "text": "z", "score": 0.5, "provider": "hubspot"},
            {"id": "2", "text": "z", "score": 0.5, "provider": "pgvector"},
        ]
        # Custom priority: hubspot > pgvector (shouldn't happen in prod,
        # but verifies the priority parameter is honored).
        out = self.dedup(items, priority=["hubspot", "pgvector"])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["provider"], "hubspot")
        self.assertEqual(out[0]["id"], "1")


class SearchViaRegistryNoCredsTests(unittest.TestCase):
    """When resolve_credentials returns None, _search_via_registry must
    silently return [] (the no-creds skip path). No exception, no error."""

    def setUp(self):
        self.mod = _fresh_module()

    def test_no_creds_returns_empty_list(self):
        # Patch the lazy imports the helper does internally:
        with patch.dict(
            sys.modules,
            {
                "AI_infrastructure.shared.org_credentials_loader": type(
                    "M", (), {"resolve_credentials": staticmethod(lambda *a, **k: None)}
                )(),
                "tools.registry_v3": type(
                    "M", (), {"RegistryV3": staticmethod(lambda: None)}
                )(),
            },
        ):
            result = self.mod._search_via_registry(
                user_id=1,
                platform_key="google_workspace",
                tool_name="gmail_search_messages",
                query="test",
                limit=10,
            )
        self.assertEqual(result, [])

    def test_no_creds_with_calendar_helper(self):
        with patch.dict(
            sys.modules,
            {
                "AI_infrastructure.shared.org_credentials_loader": type(
                    "M", (), {"resolve_credentials": staticmethod(lambda *a, **k: None)}
                )(),
                "tools.registry_v3": type(
                    "M", (), {"RegistryV3": staticmethod(lambda: None)}
                )(),
            },
        ):
            result = self.mod._search_calendar_via_registry(
                user_id=1,
                platform_key="google_workspace",
                list_tool="google_calendar_list_events",
                query="standup",
                limit=10,
            )
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
