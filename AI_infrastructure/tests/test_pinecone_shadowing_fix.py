"""
Regression test for the Pinecone tool-shadowing bug.

Bug (pre-fix):
    tools/implementations/pinecone.py and
    tools/implementations/pinecone/__init__.py each redefined
    six tool names as stub functions AFTER importing only the 8
    active tools from the subfolder. Because Python's last-binding-wins,
    the stubs shadowed the REAL implementations in
    pinecone_tools.py (138-line parallel search, metadata-only fetch,
    etc.) and pinecone_strategies.py (1348-line education tool).

    Result: The JSON schema advertised 13 tools to the AI. The model
    called them. The worker dispatched to a stub that returned either
    a hard error or a wrong-shape response (e.g. list_namespaces data
    instead of parallel-search matches).

Fix (applied):
    Both wrapper files now import all 14 tools from their real homes
    and expose them via __all__. The stub function definitions are gone.

This test asserts the FUNCTION IDENTITY of every formerly-stubbed name
when imported from each public entrypoint. If a stub is reintroduced,
the imported name will be a different function object from the one in
pinecone_tools.py / pinecone_strategies.py, and this test fails.

Also asserts the OLD stub signatures cannot reappear:
    - pinecone_query_namespaces must NOT just forward to pinecone_list_namespaces
    - pinecone_search_summaries must NOT just forward to pinecone_query_vectors
    - pinecone_get_vector_details must NOT just forward to pinecone_fetch_vectors
    - pinecone_search_and_retrieve must NOT just forward to pinecone_query_vectors
    - pinecone_fetch_by_metadata must NOT just hard-error
    - pinecone_explain_strategies must NOT just hard-error

Strategy:
    We import the public symbols and the source-of-truth symbols, then
    compare `__qualname__`, `__code__.co_filename`, and (for wrappers)
    `__wrapped__` chain. We don't execute the tools (no network).
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


# These are the formerly-stubbed names, grouped by their source-of-truth module.
SHADOWED_NAMES = [
    # (public name, source-of-truth module path, source-of-truth symbol)
    ("pinecone_query_namespaces",
     "tools.implementations.pinecone.pinecone_tools", "pinecone_query_namespaces"),
    ("pinecone_fetch_by_metadata",
     "tools.implementations.pinecone.pinecone_tools", "pinecone_fetch_by_metadata"),
    ("pinecone_search_summaries",
     "tools.implementations.pinecone.pinecone_tools", "pinecone_search_summaries"),
    ("pinecone_get_vector_details",
     "tools.implementations.pinecone.pinecone_tools", "pinecone_get_vector_details"),
    ("pinecone_search_and_retrieve",
     "tools.implementations.pinecone.pinecone_tools", "pinecone_search_and_retrieve"),
    ("pinecone_explain_strategies",
     "tools.implementations.pinecone.pinecone_strategies", "pinecone_explain_strategies"),
]


# Names whose real implementation lives in pinecone_tools.py.
# Used to assert the old forwarding stubs are gone.
PINECONE_TOOLS_NAMES = {
    "pinecone_query_namespaces",
    "pinecone_fetch_by_metadata",
    "pinecone_search_summaries",
    "pinecone_get_vector_details",
    "pinecone_search_and_retrieve",
}


class PineconeShadowingFixTests(unittest.TestCase):
    """Verify every formerly-stubbed Pinecone tool name resolves to its
    REAL implementation, not a stub that shadows it."""

    @classmethod
    def setUpClass(cls):
        # Force a clean import (in case other tests cached a broken version)
        for mod_name in (
            "tools.implementations.pinecone",
            "tools.implementations.pinecone.pinecone_tools",
            "tools.implementations.pinecone.pinecone_strategies",
        ):
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        cls.pinecone_pkg = importlib.import_module("tools.implementations.pinecone")
        cls.pinecone_mod = importlib.import_module(
            "tools.implementations.pinecone.pinecone_tools"
        )
        cls.pinecone_strategies = importlib.import_module(
            "tools.implementations.pinecone.pinecone_strategies"
        )

    # ------------------------------------------------------------------
    # Identity tests: public import must be the SAME function as source.
    # ------------------------------------------------------------------

    def test_pinecone_pkg_imports_all_six_real_implementations(self):
        """Each formerly-stubbed name must be importable from the top-level
        wrapper module AND must be the SAME function object as the real
        implementation in pinecone_tools.py / pinecone_strategies.py."""
        for public_name, source_module, source_name in SHADOWED_NAMES:
            with self.subTest(name=public_name):
                # 1. Importable from the public wrapper
                self.assertTrue(
                    hasattr(self.pinecone_pkg, public_name),
                    f"{public_name!r} is not exported from tools.implementations.pinecone",
                )
                public_fn = getattr(self.pinecone_pkg, public_name)

                # 2. Importable from the source-of-truth module
                source_mod = importlib.import_module(source_module)
                self.assertTrue(
                    hasattr(source_mod, source_name),
                    f"{source_name!r} not found in {source_module}",
                )
                source_fn = getattr(source_mod, source_name)

                # 3. SAME function object (the fix's load-bearing invariant)
                self.assertIs(
                    public_fn,
                    source_fn,
                    f"{public_name!r} is shadowed by a stub. "
                    f"Public identity: {public_fn!r}, "
                    f"source-of-truth identity: {source_fn!r}. "
                    f"A function defined later in tools/implementations/pinecone.py "
                    f"or tools/implementations/pinecone/__init__.py has overridden the "
                    f"real implementation.",
                )

    # ------------------------------------------------------------------
    # Old-stub signature tests: prove the forwarding stubs are gone.
    # ------------------------------------------------------------------

    def test_query_namespaces_is_not_a_list_namespaces_forward(self):
        """The old stub was:
            def pinecone_query_namespaces(**kwargs):
                return pinecone_list_namespaces(**kwargs)
        That's a different function object than the real
        pinecone_query_namespaces. After the fix, this assertion holds."""
        public_fn = getattr(self.pinecone_pkg, "pinecone_query_namespaces")
        real_fn = getattr(self.pinecone_mod, "pinecone_query_namespaces")
        list_namespaces_fn = getattr(self.pinecone_mod, "pinecone_list_namespaces")

        # The bug signature: public_fn would equal list_namespaces_fn's
        # forwarded behaviour. The fix's signature: public_fn IS real_fn,
        # which is a *different* function from list_namespaces_fn.
        self.assertIs(public_fn, real_fn)
        self.assertIsNot(public_fn, list_namespaces_fn)

    def test_search_summaries_is_not_a_query_vectors_forward(self):
        public_fn = getattr(self.pinecone_pkg, "pinecone_search_summaries")
        real_fn = getattr(self.pinecone_mod, "pinecone_search_summaries")
        query_vectors_fn = getattr(self.pinecone_mod, "pinecone_query_vectors")

        self.assertIs(public_fn, real_fn)
        self.assertIsNot(public_fn, query_vectors_fn)

    def test_get_vector_details_is_not_a_fetch_vectors_forward(self):
        public_fn = getattr(self.pinecone_pkg, "pinecone_get_vector_details")
        real_fn = getattr(self.pinecone_mod, "pinecone_get_vector_details")
        fetch_vectors_fn = getattr(self.pinecone_mod, "pinecone_fetch_vectors")

        self.assertIs(public_fn, real_fn)
        self.assertIsNot(public_fn, fetch_vectors_fn)

    def test_search_and_retrieve_is_not_a_query_vectors_forward(self):
        public_fn = getattr(self.pinecone_pkg, "pinecone_search_and_retrieve")
        real_fn = getattr(self.pinecone_mod, "pinecone_search_and_retrieve")
        query_vectors_fn = getattr(self.pinecone_mod, "pinecone_query_vectors")

        self.assertIs(public_fn, real_fn)
        self.assertIsNot(public_fn, query_vectors_fn)

    def test_fetch_by_metadata_does_not_return_hard_error(self):
        """The old stub returned {"success": False, "error": "DEPRECATED: ..."}.
        After the fix, the function is the real implementation. We assert
        this indirectly: the real function is NOT the stub, and its
        __code__ object is different from a tiny lambda-style stub."""
        public_fn = getattr(self.pinecone_pkg, "pinecone_fetch_by_metadata")
        real_fn = getattr(self.pinecone_mod, "pinecone_fetch_by_metadata")

        self.assertIs(public_fn, real_fn)
        # The real implementation should have a non-trivial bytecode size.
        # A stub `return {...}` is typically < 100 bytes of bytecode.
        self.assertGreater(
            len(public_fn.__code__.co_code),
            100,
            "pinecone_fetch_by_metadata looks like a stub (too few bytecode ops). "
            "The real implementation should be a 100+ line function.",
        )

    def test_explain_strategies_resolves_to_strategies_module(self):
        """The education tool lives in pinecone_strategies.py (NOT
        pinecone_tools.py). It must be re-exported from the wrapper."""
        public_fn = getattr(self.pinecone_pkg, "pinecone_explain_strategies")
        real_fn = getattr(self.pinecone_strategies, "pinecone_explain_strategies")

        self.assertIs(public_fn, real_fn)
        # The real implementation has the 1300+ line knowledge base dict;
        # bytecode should be substantial.
        self.assertGreater(
            len(public_fn.__code__.co_code),
            500,
            "pinecone_explain_strategies looks too small — "
            "the real implementation is a 1348-line education tool.",
        )

    # ------------------------------------------------------------------
    # Subpackage (__init__.py) identity tests — separate from the
    # top-level wrapper because registry discovery may go through
    # either path.
    # ------------------------------------------------------------------

    def test_subpackage_reexports_all_six_real_implementations(self):
        """The same identity invariant, checked against the subpackage
        entrypoint that some loaders use."""
        sub_pkg = importlib.import_module("tools.implementations.pinecone")
        for public_name, source_module, source_name in SHADOWED_NAMES:
            with self.subTest(name=public_name):
                self.assertTrue(
                    hasattr(sub_pkg, public_name),
                    f"{public_name!r} not in subpackage __init__.py exports",
                )
                public_fn = getattr(sub_pkg, public_name)
                source_mod = importlib.import_module(source_module)
                source_fn = getattr(source_mod, source_name)
                self.assertIs(
                    public_fn,
                    source_fn,
                    f"{public_name!r} shadowed in tools/implementations/pinecone/__init__.py",
                )

    # ------------------------------------------------------------------
    # __all__ regression — make sure the public name list is correct.
    # ------------------------------------------------------------------

    def test_top_level_all_contains_all_six(self):
        for public_name, _, _ in SHADOWED_NAMES:
            with self.subTest(name=public_name):
                self.assertIn(
                    public_name,
                    self.pinecone_pkg.__all__,
                    f"{public_name!r} missing from pinecone.py __all__",
                )

    def test_subpackage_all_contains_all_six(self):
        sub_pkg = importlib.import_module("tools.implementations.pinecone")
        for public_name, _, _ in SHADOWED_NAMES:
            with self.subTest(name=public_name):
                self.assertIn(
                    public_name,
                    sub_pkg.__all__,
                    f"{public_name!r} missing from pinecone/__init__.py __all__",
                )

    # ------------------------------------------------------------------
    # No stub return strings leak into docstrings or comments.
    # ------------------------------------------------------------------

    def test_no_deprecation_strings_in_source(self):
        """The old stubs had 'DEPRECATED:' baked into their return dicts
        and docstrings. After the fix, the public module's source should
        not contain that string (it was a fabrication, the tools were
        never actually deprecated)."""
        for path in (
            Path(REPO_ROOT) / "tools" / "implementations" / "pinecone.py",
            Path(REPO_ROOT) / "tools" / "implementations" / "pinecone" / "__init__.py",
        ):
            with self.subTest(path=str(path)):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(
                    '"DEPRECATED:', text,
                    f"{path.name} still contains a hard-coded DEPRECATED error "
                    "string — likely a residual stub.",
                )
                self.assertNotIn(
                    "DEPRECATED: Use pinecone", text,
                    f"{path.name} still contains a 'DEPRECATED: Use pinecone_*' "
                    "forwarding stub.",
                )


if __name__ == "__main__":
    unittest.main()
