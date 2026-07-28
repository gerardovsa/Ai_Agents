"""
Regression test for vector_db routes: execute_tool() signature + tool names.

Bug: RegistryV3.execute_tool is **kwargs-only. Several call sites in
AI_infrastructure/routes/vector_db/vector_db_enhanced_routes.py and
AI_infrastructure/routes/vector_db/vector_db_routes.py passed the tool name
as a positional argument, which raises:

    TypeError: execute_tool() takes 1 positional argument but 2 were given

This test exercises every fixed call site through Flask.test_client(),
stubs request.user (the auth decorator normally sets this from the JWT),
and patches RegistryV3.execute_tool to capture the kwargs it was called
with. It asserts:

  1. No TypeError on any fixed call site.
  2. RegistryV3.execute_tool was called with tool_name=... as a KEYWORD
     (not positionally).
  3. The tool_name values are the correct, registered names
     (e.g. 'pinecone_describe_index_stats', NOT 'pinecone_get_index_stats').

Strategy:
  - @require_auth is applied at IMPORT TIME on each view function. So
    we patch the *source* of require_auth at the module level BEFORE
    importing the routes, and reload the routes modules so the decorator
    binds to our no-op. This is the cleanest way to bypass auth in tests
    without spinning up JWT infrastructure.
  - RegistryV3.execute_tool is patched at the class-method level for
    each test. The enhanced routes module creates a singleton RegistryV3
    at import; the base routes create a fresh one inside each route.
    Patching the class method covers both cases.
"""

import importlib
import sys
import unittest
from pathlib import Path
from unittest import mock

from flask import Flask, request

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _noop_decorator_factory():
    """Return a fresh identity-decorator that mirrors require_auth's
    signature but does no auth at all."""
    def _passthrough(f):
        return f
    return _passthrough


def _build_test_app(enhanced_bp, base_bp):
    """Build a Flask app that mounts the two blueprints and stubs request.user."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _fake_auth():
        if request.method == "OPTIONS":
            return None
        # The enhanced routes use request.user.get('user_id').
        request.user = {"user_id": 42}

    app.register_blueprint(enhanced_bp)
    app.register_blueprint(base_bp)
    return app


class _ExecuteToolRecorder:
    """Stand-in for RegistryV3.execute_tool. Records every call's
    positional + keyword args. Returns canned successful responses shaped
    like the real tools' outputs so the routes' response builders work."""

    def __init__(self):
        self.calls = []  # list of (args, kwargs)

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        # Return DIFFERENT shapes per tool, matching the real implementations.
        tool_name = kwargs.get("tool_name", "")
        # describe_index_stats returns namespaces keyed by name (dict-of-dict).
        if tool_name == "pinecone_describe_index_stats":
            return {
                "success": True,
                "namespaces": {
                    "user_42_legal": {"vector_count": 7},
                    "user_42_finance": {"vector_count": 12},
                },
                "total_vector_count": 19,
                "dimension": 1536,
                "metric": "cosine",
            }
        # list_namespaces returns namespaces as a LIST of dicts.
        if tool_name == "pinecone_list_namespaces":
            return {
                "success": True,
                "namespaces": [
                    {"name": "user_42_legal", "vector_count": 7, "created_at": "2026-07-01T00:00:00Z"},
                    {"name": "user_42_finance", "vector_count": 12, "created_at": "2026-07-02T00:00:00Z"},
                ],
            }
        # query_vectors returns matches with id/score/metadata.
        if tool_name == "pinecone_query_vectors":
            return {
                "success": True,
                "matches": [{"id": "vec_1", "score": 0.9, "metadata": {"k": "v"}}],
            }
        # query_namespaces (alias -> list_namespaces for now).
        if tool_name == "pinecone_query_namespaces":
            return {
                "success": True,
                "matches": [{"id": "vec_1", "score": 0.9, "metadata": {"k": "v"}}],
                "namespaces_searched": kwargs.get("namespaces", []),
            }
        # delete_vectors returns a count.
        if tool_name == "pinecone_delete_vectors":
            return {"success": True, "vectors_deleted": 7}
        # Default fallback.
        return {"success": True}


def _load_routes_with_no_op_auth():
    """Force-reload the two routes modules with @require_auth replaced
    by a no-op. Required because the decorator is bound at import time."""
    import AI_infrastructure.auth.user_auth as user_auth_mod

    # Patch the SOURCE before the routes modules are (re-)imported.
    with mock.patch.object(user_auth_mod, "require_auth", _noop_decorator_factory()):
        # Drop cached imports so re-import re-runs @require_auth with our no-op.
        for mod_name in [
            "AI_infrastructure.routes.vector_db.vector_db_enhanced_routes",
            "AI_infrastructure.routes.vector_db.vector_db_routes",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        enhanced_mod = importlib.import_module(
            "AI_infrastructure.routes.vector_db.vector_db_enhanced_routes"
        )
        base_mod = importlib.import_module(
            "AI_infrastructure.routes.vector_db.vector_db_routes"
        )

    return enhanced_mod.vector_db_enhanced_bp, base_mod.vector_db_bp


class VectorDbExecuteToolSignatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enhanced_bp, cls.base_bp = _load_routes_with_no_op_auth()
        cls._recorder = _ExecuteToolRecorder()

    def _patched_execute_tool(self):
        """Patch RegistryV3.execute_tool. The base routes construct a fresh
        RegistryV3 inside each route, and the enhanced routes use a module-level
        singleton. Patching the class method covers both."""
        return mock.patch(
            "tools.registry_v3.RegistryV3.execute_tool",
            new=self._recorder,
            create=True,
        )

    def _run_with_patches(self, client_fn):
        with self._patched_execute_tool():
            app = _build_test_app(self.enhanced_bp, self.base_bp)
            client = app.test_client()
            return client_fn(client)

    # ------------------------------------------------------------------
    # vector_db_enhanced_routes.py — 5 fixed call sites
    # ------------------------------------------------------------------

    def test_query_namespaces_uses_keyword_tool_name(self):
        resp = self._run_with_patches(lambda c: c.post(
            "/api/vector-db/query-namespaces",
            json={
                "query_text": "what is a contract?",
                "namespaces": ["user_42_legal"],
            },
        ))
        self.assertEqual(resp.status_code, 200, resp.get_json())
        self._assert_keyword_tool_name_in_calls([
            "pinecone_query_namespaces",
            "pinecone_describe_index_stats",
        ])

    def test_fetch_by_metadata_uses_pinecone_query_vectors(self):
        resp = self._run_with_patches(lambda c: c.post(
            "/api/vector-db/fetch-by-metadata",
            json={
                "filter": {"category": {"$eq": "legal"}},
                "query_text": "legal docs",
            },
        ))
        self.assertEqual(resp.status_code, 200, resp.get_json())
        self._assert_keyword_tool_name_in_calls(["pinecone_query_vectors"])
        # And the response must use the new 'vectors' key, not 'matches'.
        body = resp.get_json()
        self.assertIn("vectors", body)
        self.assertNotIn("matches", body)

    def test_fetch_by_metadata_rejects_missing_query_text(self):
        resp = self._run_with_patches(lambda c: c.post(
            "/api/vector-db/fetch-by-metadata",
            json={"filter": {"category": {"$eq": "legal"}}},
        ))
        self.assertEqual(resp.status_code, 400)
        self.assertIn("query_text", resp.get_json().get("error", ""))

    def test_list_namespaces_uses_describe_index_stats(self):
        resp = self._run_with_patches(lambda c: c.get(
            "/api/vector-db/namespaces?include_stats=true",
        ))
        self.assertEqual(resp.status_code, 200, resp.get_json())
        self._assert_keyword_tool_name_in_calls(["pinecone_describe_index_stats"])
        # CRITICAL: the buggy 'pinecone_describe_index' (without the _stats
        # suffix) must NOT be called. We use an exact-match check rather
        # than substring, because 'pinecone_describe_index_stats' contains
        # 'pinecone_describe_index' as a substring and would yield a false
        # positive.
        for _args, kwargs in self._recorder.calls:
            tool_name = kwargs.get("tool_name", "")
            self.assertNotEqual(
                tool_name, "pinecone_describe_index",
                f"execute_tool was called with the non-existent "
                f"'pinecone_describe_index'; use 'pinecone_describe_index_stats'.",
            )

    def test_describe_namespace_extracts_dimension_from_stats(self):
        resp = self._run_with_patches(lambda c: c.get(
            "/api/vector-db/namespaces/user_42_legal",
        ))
        self.assertEqual(resp.status_code, 200, resp.get_json())
        body = resp.get_json()
        # Dimension + metric should come from the canned stats result.
        self.assertEqual(body["namespace"]["dimension"], 1536)
        self.assertEqual(body["namespace"]["metric"], "cosine")
        self._assert_keyword_tool_name_in_calls(["pinecone_describe_index_stats"])
        all_tool_names = [
            k.get("tool_name") for _a, k in self._recorder.calls if isinstance(k, dict)
        ]
        self.assertNotIn("pinecone_describe_index", all_tool_names)

    def test_delete_namespace_uses_describe_index_stats_then_delete(self):
        resp = self._run_with_patches(lambda c: c.delete(
            "/api/vector-db/namespaces/user_42_legal?confirm=DELETE",
        ))
        self.assertEqual(resp.status_code, 200, resp.get_json())
        self._assert_keyword_tool_name_in_calls([
            "pinecone_describe_index_stats",
            "pinecone_delete_vectors",
        ])

    # ------------------------------------------------------------------
    # vector_db_routes.py — 5 fixed call sites (signature-only)
    # ------------------------------------------------------------------

    def test_base_routes_use_keyword_tool_name(self):
        def _exercise(client):
            r1 = client.get("/api/vector-db/stats?user_id=42")
            self.assertEqual(r1.status_code, 200, r1.get_json())
            r2 = client.get("/api/vector-db/documents?user_id=42")
            self.assertEqual(r2.status_code, 200, r2.get_json())
            r3 = client.delete(
                "/api/vector-db/document/user_42_legal",
                json={"user_id": 42},
            )
            self.assertEqual(r3.status_code, 200, r3.get_json())
            return r3

        resp = self._run_with_patches(_exercise)
        self._assert_keyword_tool_name_in_calls([
            "pinecone_describe_index_stats",
            "pinecone_list_namespaces",
            "pinecone_delete_vectors",
        ])

    # ------------------------------------------------------------------
    # Regression sentinel: prove the recorder catches the bug if it
    # regresses. Re-import one route handler patched to call positionally.
    # ------------------------------------------------------------------

    def _assert_keyword_tool_name_in_calls(self, expected_names):
        """Each expected tool_name must appear as a KEYWORD kwarg, not positionally.

        If a call site regresses to `execute_tool('pinecone_X', ...)`,
        Python packs 'pinecone_X' into *args and the kwargs dict has no
        'tool_name' key. We assert both: the keyword is present, AND
        no positional tool_name leaked through.
        """
        seen_tool_names = []
        for args, kwargs in self._recorder.calls:
            if isinstance(kwargs, dict) and "tool_name" in kwargs:
                seen_tool_names.append(kwargs["tool_name"])
        for name in expected_names:
            self.assertIn(
                name,
                seen_tool_names,
                f"Expected tool_name='{name}' as a keyword kwarg; got {seen_tool_names!r}",
            )
        # Regression sentinel: no tool_name should have ended up in *args.
        for args, kwargs in self._recorder.calls:
            self.assertEqual(
                args, (),
                f"execute_tool() was called positionally with {args!r}; "
                f"all call sites must use tool_name='...' keyword. kwargs={kwargs!r}",
            )

    def test_recorder_catches_positional_regression(self):
        """If a call site regresses to `execute_tool('pinecone_X', ...)`,
        Python packs 'pinecone_X' into *args and the kwargs dict has no
        'tool_name' key. The assertion below proves the recorder sees that."""

        # Simulate the old (buggy) call shape directly.
        self._recorder.calls.clear()
        self._recorder("pinecone_describe_index_stats", _user_id=42)

        args, kwargs = self._recorder.calls[0]
        # Bug signature: positional arg in *args.
        self.assertEqual(args, ("pinecone_describe_index_stats",))
        # Bug signature: no tool_name kwarg.
        self.assertNotIn("tool_name", kwargs)
        # This is exactly what would have surfaced in the original bug —
        # registry_v3.py:1435 `def execute_tool(self, **kwargs)` would raise
        # TypeError("takes 1 positional argument but 2 were given").


if __name__ == "__main__":
    unittest.main()