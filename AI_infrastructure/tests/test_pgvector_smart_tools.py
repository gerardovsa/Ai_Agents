"""
Regression test for the pgvector smart/education tool parity work.

Context:
    pgvector originally shipped with 6 "core" tools (query, upsert, delete,
    list_documents, describe_stats, upload_document) but was missing the
    6 "smart/education" tools that Pinecone provides:
        - query_namespaces
        - fetch_by_metadata
        - search_summaries
        - get_vector_details
        - search_and_retrieve
        - explain_strategies

    This test asserts:
        1. Each of the 6 smart tools is importable from
           tools/implementations/pgvector/pgvector_tools.py
        2. They are NOT shadows of any existing core tool
           (regression guard against the same stub-shadowing bug we fixed
           on the Pinecone side — see test_pinecone_shadowing_fix.py).
        3. The new helper `_translate_filter_to_sql` correctly translates
           every supported Pinecone filter operator into a JSONB WHERE
           fragment with the right number of %s placeholders.

Strategy:
    Pure-Python identity and translation tests — no DB, no network, no
    embedding calls. The translation helper is the load-bearing piece
    because every other filter-aware tool funnels through it.
"""

import importlib
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)


# The 6 smart/education tools ported from Pinecone → pgvector.
SMART_TOOL_NAMES = [
    "pgvector_query_namespaces",
    "pgvector_fetch_by_metadata",
    "pgvector_search_summaries",
    "pgvector_get_vector_details",
    "pgvector_search_and_retrieve",
    "pgvector_explain_strategies",
]

# Core tools that the new smart tools MUST NOT shadow (same family of bug
# as the Pinecone stub-shadowing incident).
CORE_TOOL_NAMES = [
    "pgvector_query_vectors",
    "pgvector_upsert_vectors",
    "pgvector_delete_vectors",
    "pgvector_list_documents",
    "pgvector_describe_stats",
    "pgvector_upload_document",
]


class PgvectorSmartToolsPresenceTests(unittest.TestCase):
    """Every smart tool must be importable from pgvector_tools.py."""

    @classmethod
    def setUpClass(cls):
        for mod_name in ("tools.implementations.pgvector.pgvector_tools",):
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        cls.mod = importlib.import_module("tools.implementations.pgvector.pgvector_tools")

    def test_all_six_smart_tools_exist(self):
        for name in SMART_TOOL_NAMES:
            with self.subTest(name=name):
                self.assertTrue(
                    hasattr(self.mod, name),
                    f"{name!r} is not defined in pgvector_tools.py",
                )
                fn = getattr(self.mod, name)
                self.assertTrue(callable(fn), f"{name!r} is not callable")

    def test_helper_exists_and_is_callable(self):
        self.assertTrue(hasattr(self.mod, "_translate_filter_to_sql"))
        self.assertTrue(callable(self.mod._translate_filter_to_sql))

    def test_no_smart_tool_shadows_a_core_tool(self):
        """Regression guard: a smart tool must be a DIFFERENT function object
        from every core tool. If someone accidentally defines
        `pgvector_query_namespaces = pgvector_query_vectors` at module
        scope, this catches it."""
        for smart in SMART_TOOL_NAMES:
            smart_fn = getattr(self.mod, smart)
            for core in CORE_TOOL_NAMES:
                with self.subTest(smart=smart, core=core):
                    core_fn = getattr(self.mod, core)
                    self.assertIsNot(
                        smart_fn, core_fn,
                        f"{smart!r} is a shadow of {core!r}",
                    )


class TranslateFilterToSqlTests(unittest.TestCase):
    """The translation helper is the load-bearing piece — every operator
    must produce correct SQL with the right number of %s placeholders."""

    @classmethod
    def setUpClass(cls):
        for mod_name in ("tools.implementations.pgvector.pgvector_tools",):
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        cls.mod = importlib.import_module("tools.implementations.pgvector.pgvector_tools")
        # staticmethod() prevents Python's descriptor protocol from binding
        # `self` when tests do `self.translate(...)`. Without it, the function
        # receives an implicit first arg and the test errors with
        # "takes 2 positional arguments but 3 were given".
        cls.translate = staticmethod(cls.mod._translate_filter_to_sql)

    # ── Empty / trivial inputs ────────────────────────────────────────

    def test_empty_dict_returns_TRUE(self):
        params: list = []
        self.assertEqual(self.translate({}, params), 'TRUE')
        self.assertEqual(params, [])

    def test_none_returns_TRUE(self):
        params: list = []
        self.assertEqual(self.translate(None, params), 'TRUE')  # type: ignore[arg-type]
        self.assertEqual(params, [])

    # ── Plain values → $eq shorthand ──────────────────────────────────

    def test_plain_value_is_eq(self):
        params: list = []
        clause = self.translate({"document_id": "abc"}, params)
        self.assertEqual(clause, "metadata->>'document_id' = %s")
        self.assertEqual(params, ["abc"])

    # ── Scalar operators ──────────────────────────────────────────────

    def test_eq_operator(self):
        params: list = []
        clause = self.translate({"document_id": {"$eq": "abc"}}, params)
        self.assertIn("= %s", clause)
        self.assertEqual(params, ["abc"])

    def test_ne_operator(self):
        params: list = []
        clause = self.translate({"status": {"$ne": "deleted"}}, params)
        self.assertIn("<> %s", clause)
        self.assertEqual(params, ["deleted"])

    def test_gt_operator_casts_to_float(self):
        params: list = []
        clause = self.translate({"year": {"$gt": 2024}}, params)
        self.assertIn("::float > %s::float", clause)
        self.assertEqual(params, ["2024"])

    def test_gte_lt_lte_operators(self):
        for op, sym in [("$gte", ">="), ("$lt", "<"), ("$lte", "<=")]:
            params: list = []
            clause = self.translate({"year": {op: 2024}}, params)
            self.assertIn(f"::float {sym} %s::float", clause,
                          f"operator {op} should produce '{sym}' comparison")

    # ── Membership operators ──────────────────────────────────────────

    def test_in_operator_produces_one_placeholder_per_element(self):
        params: list = []
        clause = self.translate({"tag": {"$in": ["a", "b", "c"]}}, params)
        self.assertIn("IN (%s,%s,%s)", clause)
        self.assertEqual(params, ["a", "b", "c"])

    def test_nin_operator_handles_nulls(self):
        params: list = []
        clause = self.translate({"tag": {"$nin": ["a", "b"]}}, params)
        self.assertIn("IS NULL OR", clause)
        self.assertIn("NOT IN", clause)
        self.assertEqual(params, ["a", "b"])

    def test_in_with_empty_array_returns_FALSE(self):
        params: list = []
        clause = self.translate({"tag": {"$in": []}}, params)
        self.assertEqual(clause, "FALSE")
        self.assertEqual(params, [])

    def test_nin_with_empty_array_returns_TRUE(self):
        params: list = []
        clause = self.translate({"tag": {"$nin": []}}, params)
        self.assertEqual(clause, "TRUE")
        self.assertEqual(params, [])

    # ── Existence operator (no %s placeholders) ──────────────────────

    def test_exists_true_uses_jsonb_question_operator(self):
        params: list = []
        clause = self.translate({"filename": {"$exists": True}}, params)
        self.assertIn("(metadata ? 'filename')", clause)
        self.assertEqual(params, [])

    def test_exists_false_negates(self):
        params: list = []
        clause = self.translate({"filename": {"$exists": False}}, params)
        self.assertIn("NOT (metadata ? 'filename')", clause)
        self.assertEqual(params, [])

    # ── Multi-key composition ────────────────────────────────────────

    def test_multiple_keys_are_AND_joined(self):
        params: list = []
        clause = self.translate(
            {"document_id": {"$eq": "abc"}, "year": {"$gte": 2024}},
            params,
        )
        self.assertIn(" AND ", clause)
        # One %s per comparison
        self.assertEqual(clause.count("%s"), 2)
        self.assertEqual(sorted(params), ["2024", "abc"])

    # ── Defensive: unknown operator is skipped (no crash) ─────────────

    def test_unknown_operator_is_skipped(self):
        params: list = []
        # Should NOT raise. Either drops the clause or returns TRUE.
        clause = self.translate({"foo": {"$bogus": "x"}}, params)
        self.assertIsInstance(clause, str)


class ExplainStrategiesStaticTests(unittest.TestCase):
    """The education tool is a static knowledge base — verify it has the
    shape the system prompt and the AI rely on."""

    @classmethod
    def setUpClass(cls):
        for mod_name in ("tools.implementations.pgvector.pgvector_tools",):
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        cls.mod = importlib.import_module("tools.implementations.pgvector.pgvector_tools")

    def test_explain_strategies_returns_expected_keys(self):
        # Call with a dummy _user_id (signature parity); no DB or network.
        result = self.mod.pgvector_explain_strategies(_user_id=1)
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("provider"), "pgvector")
        strategies = result.get("strategies") or {}
        for required_key in (
            "metric",
            "default_threshold",
            "embedding_dim",
            "embedding_providers",
            "index_type",
            "rls",
            "namespace_strategy",
            "reindex_on_swap",
            "best_for",
            "limits",
        ):
            with self.subTest(key=required_key):
                self.assertIn(required_key, strategies)

    def test_reindex_on_swap_states_NO(self):
        """Critical contract: switching providers does NOT move data.
        The system prompt injects this fact so the AI tells users
        their old data is still queryable via the secondary."""
        result = self.mod.pgvector_explain_strategies(_user_id=1)
        self.assertTrue(
            result["strategies"]["reindex_on_swap"].upper().startswith("NO"),
            "reindex_on_swap MUST start with 'NO' so the AI does not "
            "promise a destructive re-index when the user changes provider",
        )

    def test_embedding_dim_matches_schema(self):
        """Migration 049 set the column to vector(768). If a future
        change bumps this, this test fires before production breakage."""
        result = self.mod.pgvector_explain_strategies(_user_id=1)
        self.assertEqual(result["strategies"]["embedding_dim"], 768)


if __name__ == "__main__":
    unittest.main()