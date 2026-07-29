"""
Regression test for the LIVE `pinecone_fetch_by_metadata` tool.

CONTEXT (2026-07-29):
    The Option-2 cleanup brief described
    `pinecone_fetch_by_metadata` as a hard-error stub. An audit (see
    UNIVERAL_SEARCH_SOURCE_STATUS_2026-07-29.md for the registry gap
    note, and the in-session transcript that produced this test) found
    that the function at
    tools/implementations/pinecone/pinecone_tools.py lines 998-1114 is
    in fact fully implemented — it routes through the real Pinecone
    SDK, builds a zero-vector query with the requested filter, clamps
    `limit` to 1000, and returns the documented response shape:

        {
            "success": True,
            "vectors":          [<id+metadata pairs>],
            "total_count":      int,
            "filter_applied":   <original filter>,
            "namespace":        <original namespace>,
        }

    The companion identity test (test_pinecone_shadowing_fix.py) only
    proves the function object is NOT a stub. This test exercises the
    function end-to-end with a mocked Pinecone client, verifying:

        1. Happy path returns the documented response shape.
        2. `dimension` is pulled from index.describe_index_stats().
        3. `filter` is passed verbatim to index.query().
        4. `namespace` and `top_k=limit` are passed verbatim.
        5. Missing credentials raise a PineconeToolsError and yield
           `{"success": False, "error_type": ...}` (no hard-coded
           "DEPRECATED:" string — the old stub signature).
        6. The `fields` argument trims returned metadata.

STRATEGY:
    We patch `pinecone.Pinecone` (the SDK import the function does
    lazily inside a try block) so `Index().describe_index_stats()`
    returns a known shape and `Index().query(...)` returns synthetic
    matches. Credentials are injected via kwargs (mirroring how the
    registry dispatches them in production). No network, no DB.
"""

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _fresh_module():
    """Reload pinecone_tools so any module-level mocks in test setUp
    don't leak between test classes."""
    for mod_name in list(sys.modules):
        if mod_name in (
            "tools.implementations.pinecone",
            "tools.implementations.pinecone.pinecone_tools",
            "tools.implementations.pinecone.pinecone_strategies",
        ):
            del sys.modules[mod_name]
    return importlib.import_module("tools.implementations.pinecone.pinecone_tools")


def _make_fake_pinecone(matches, dimension=768):
    """Build a MagicMock shaped like `pinecone.Pinecone(api_key=...)`
    so the function's `Pinecone(...).Index(name).describe_index_stats()`
    and `.query(...)` calls return synthetic but well-formed data."""
    fake_index = MagicMock()
    fake_index.describe_index_stats.return_value = {"dimension": dimension}
    fake_index.query.return_value = {"matches": matches}

    fake_pc_instance = MagicMock()
    fake_pc_instance.Index.return_value = fake_index

    fake_pc_class = MagicMock()
    fake_pc_class.return_value = fake_pc_instance
    return fake_pc_class, fake_index


class PineconeFetchByMetadataTests(unittest.TestCase):
    """End-to-end behaviour of pinecone_fetch_by_metadata with a
    mocked Pinecone SDK. Verifies the function is operational, not a
    hard-error stub."""

    def setUp(self):
        self.pinecone_tools = _fresh_module()
        self.fn = self.pinecone_tools.pinecone_fetch_by_metadata

    # ------------------------------------------------------------------
    # Happy-path: documented response shape + filter passthrough.
    # ------------------------------------------------------------------

    def test_returns_documented_response_shape(self):
        matches = [
            {
                "id": "vec_1",
                "metadata": {"title": "Contract A", "year": 2024},
                "namespace": "",
            },
            {
                "id": "vec_2",
                "metadata": {"title": "Contract B", "year": 2025},
                "namespace": "",
            },
        ]
        fake_pc, fake_index = _make_fake_pinecone(matches, dimension=1536)

        with patch.dict(sys.modules, {"pinecone": MagicMock(Pinecone=fake_pc)}):
            result = self.fn(
                filter={"category": {"$eq": "legal"}},
                namespace="user_1",
                limit=10,
                _user_id=42,
                pinecone_api_key="sk-test",
                pinecone_index_name="prod-index",
            )

        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertEqual(result["total_count"], 2)
        self.assertEqual(result["namespace"], "user_1")
        self.assertEqual(result["filter_applied"], {"category": {"$eq": "legal"}})
        # Both match ids present.
        returned_ids = {v["id"] for v in result["vectors"]}
        self.assertEqual(returned_ids, {"vec_1", "vec_2"})
        # No "DEPRECATED:" string — the old stub signature would have
        # emitted something like
        #   {"success": False, "error": "DEPRECATED: Use pinecone_..."}
        self.assertNotIn("error", result)

    def test_limit_clamped_to_1000_and_passed_as_top_k(self):
        matches = [{"id": f"vec_{i}", "metadata": {"i": i}} for i in range(3)]
        fake_pc, fake_index = _make_fake_pinecone(matches, dimension=512)

        with patch.dict(sys.modules, {"pinecone": MagicMock(Pinecone=fake_pc)}):
            self.fn(
                filter={"x": {"$eq": 1}},
                namespace="",
                limit=5000,  # > 1000; the function clamps internally
                _user_id=1,
                pinecone_api_key="k",
                pinecone_index_name="idx",
            )

        # top_k must be the clamped value, not 5000.
        call_kwargs = fake_index.query.call_args.kwargs
        self.assertEqual(call_kwargs["top_k"], 1000)
        self.assertTrue(call_kwargs["include_metadata"])
        self.assertFalse(call_kwargs["include_values"])

    def test_zero_vector_uses_dimension_from_describe_index_stats(self):
        matches = [{"id": "v1", "metadata": {}}]
        # dimension=512 → zero_vector has 512 entries.
        fake_pc, fake_index = _make_fake_pinecone(matches, dimension=512)

        with patch.dict(sys.modules, {"pinecone": MagicMock(Pinecone=fake_pc)}):
            self.fn(
                filter={"x": {"$eq": 1}},
                _user_id=1,
                pinecone_api_key="k",
                pinecone_index_name="idx",
            )

        call_kwargs = fake_index.query.call_args.kwargs
        vector_used = call_kwargs["vector"]
        self.assertEqual(len(vector_used), 512)
        self.assertTrue(all(v == 0.0 for v in vector_used))

    def test_describe_stats_failure_falls_back_to_1536(self):
        matches = [{"id": "v1", "metadata": {}}]
        fake_pc, fake_index = _make_fake_pinecone(matches)
        # Force describe_index_stats to raise; function catches it.
        fake_index.describe_index_stats.side_effect = RuntimeError("network")

        with patch.dict(sys.modules, {"pinecone": MagicMock(Pinecone=fake_pc)}):
            result = self.fn(
                filter={"x": {"$eq": 1}},
                _user_id=1,
                pinecone_api_key="k",
                pinecone_index_name="idx",
            )

        # Still succeeded — fell back to default 1536-dim zero vector.
        self.assertTrue(result["success"])
        call_kwargs = fake_index.query.call_args.kwargs
        self.assertEqual(len(call_kwargs["vector"]), 1536)

    # ------------------------------------------------------------------
    # Filter / namespace passthrough — the things the AI relies on.
    # ------------------------------------------------------------------

    def test_filter_and_namespace_passed_to_pinecone_query(self):
        matches = [{"id": "v", "metadata": {}}]
        fake_pc, fake_index = _make_fake_pinecone(matches)

        sentinel_filter = {"category": {"$eq": "finance"}, "year": {"$gte": 2024}}
        with patch.dict(sys.modules, {"pinecone": MagicMock(Pinecone=fake_pc)}):
            self.fn(
                filter=sentinel_filter,
                namespace="n_42_finance",
                limit=50,
                _user_id=42,
                pinecone_api_key="k",
                pinecone_index_name="idx",
            )

        call_kwargs = fake_index.query.call_args.kwargs
        self.assertEqual(call_kwargs["namespace"], "n_42_finance")
        self.assertEqual(call_kwargs["filter"], sentinel_filter)
        self.assertEqual(call_kwargs["top_k"], 50)

    # ------------------------------------------------------------------
    # Field trimming.
    # ------------------------------------------------------------------

    def test_fields_trim_returned_metadata(self):
        matches = [
            {
                "id": "v",
                "metadata": {
                    "title": "T",
                    "author": "A",
                    "internal_note": "secret",
                },
            }
        ]
        fake_pc, _ = _make_fake_pinecone(matches)

        with patch.dict(sys.modules, {"pinecone": MagicMock(Pinecone=fake_pc)}):
            result = self.fn(
                filter={"x": {"$eq": 1}},
                fields=["title", "author"],
                _user_id=1,
                pinecone_api_key="k",
                pinecone_index_name="idx",
            )

        self.assertEqual(result["total_count"], 1)
        meta = result["vectors"][0]["metadata"]
        self.assertEqual(set(meta.keys()), {"title", "author"})
        self.assertNotIn("internal_note", meta)

    # ------------------------------------------------------------------
    # Error paths — the function returns {success: False}, never raises.
    # ------------------------------------------------------------------

    def test_missing_user_id_returns_failure(self):
        # No `_user_id` kwarg → function raises PineconeToolsError
        # which is caught → returns success=False with error_type.
        result = self.fn(
            filter={"x": {"$eq": 1}},
            pinecone_api_key="k",
            pinecone_index_name="idx",
        )

        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error_type"], "PineconeToolsError")

    def test_missing_credentials_returns_failure(self):
        result = self.fn(
            filter={"x": {"$eq": 1}},
            _user_id=1,
            # No pinecone_api_key, no pinecone_index_name.
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "PineconeToolsError")

    def test_response_never_carries_deprecation_marker(self):
        """Regression: the old stub returned a 'DEPRECATED: ...' string.
        In any error path the new implementation must NOT carry that
        signature — otherwise callers might key off it."""
        result = self.fn(
            filter={"x": {"$eq": 1}},
            _user_id=1,
        )  # Missing api key + index name

        self.assertFalse(result["success"])
        # Either no error key, or an error key that doesn't say DEPRECATED.
        err_text = (result.get("error") or "")
        self.assertNotIn("DEPRECATED", err_text)


if __name__ == "__main__":
    unittest.main()
