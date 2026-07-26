"""
test_tool_name_allowlist.py
============================
Smoke tests for the Jul 26, 2026 server-side tool-name allowlist.

Background (see AI_infrastructure/prompts/TOOL_SYSTEM_ROBUSTNESS_2026-07-26.md
§5, fix #1):

    Reasoning-amplified models (Anthropic extended thinking, MiniMax-M3)
    can fabricate tool names *inside* the thinking trace and emit them as
    legitimate tool_use blocks, even though the provider's server-side
    `input_schema` constraint should forbid it. Per AgentSentinel
    (arXiv 2509.07764) this has a 90-100% Attack Success Rate on Claude
    3.5/3.7 Sonnet and GPT-4/4o.

    The fix is a single, provider-agnostic allowlist gate at the
    dispatch boundary in `combined_agent_worker.py`, backed by a new
    `RegistryV3.is_tool_allowed(name)` helper.

What the tests cover:

  TA-1   is_tool_allowed returns True for a registered tool
  TA-2   is_tool_allowed returns True for the two meta-tools (fallback set)
  TA-3   is_tool_allowed returns False for hallucinated / random names
  TA-4   is_tool_allowed returns False for None, empty, and non-string input
  TA-5   list_tool_names returns a list of strings (no exceptions)
  TA-6   The constant `_ALLOWED_META_TOOL_NAMES` is exactly the expected set
  TA-7   Gate simulation: unknown tool_name raises ValueError with a
         structured message; meta-tools and registered tools pass
  TA-8   Gate simulation's error message includes a "did you mean" hint
         when a same-prefix registered tool exists
  TA-9   Gate simulation's error message omits the hint when no prefix match

Run:

    python AI_infrastructure/tests/test_tool_name_allowlist.py

Exit code 0 = all green.
"""

from __future__ import annotations

import os
import re
import sys
import types
import unittest


# ---------------------------------------------------------------------------
# Test infrastructure: mock registry + replay the production gate logic.
# ---------------------------------------------------------------------------

class _MockRegistry:
    """Minimal stand-in for RegistryV3 with the same public surface.

    We do NOT instantiate RegistryV3() here — the constructor loads every
    tool schema from disk and pulls in heavy dependencies (Anthropic SDK,
    pinecone, xero, etc.). For unit-level correctness we only need the
    `is_tool_allowed` method's logic, which is pure-Python and depends
    solely on `self.tools` and the `_ALLOWED_META_TOOL_NAMES` constant.
    """

    # MUST stay in sync with `tools/registry_v3.py:_ALLOWED_META_TOOL_NAMES`.
    # The production constant is a frozenset of the two meta-tools that
    # are routed through a special-case branch in the agentic loop and
    # therefore do not have entries in `self.tools`.
    _ALLOWED_META_TOOL_NAMES = frozenset({"get_tool_schema", "execute_tool"})

    def __init__(self, registered_tools=None):
        # Use a dict-of-empty-dicts shape — same as `RegistryV3.tools`.
        self.tools = dict(registered_tools or {})

    def is_tool_allowed(self, tool_name):
        """Exact replica of RegistryV3.is_tool_allowed (line 901-913 of
        tools/registry_v3.py). If production drifts, update both copies.
        """
        if not isinstance(tool_name, str) or not tool_name:
            return False
        if tool_name in self.tools:
            return True
        return tool_name in self._ALLOWED_META_TOOL_NAMES

    def list_tool_names(self):
        """Exact replica of RegistryV3.list_tool_names."""
        return sorted(self.tools.keys())


def _gate_decision(registry, tool_name):
    """Replica of the production gate's error-path formatting.

    Mirrors the code added to combined_agent_worker.py at line 2269+
    (the body of the `if not registry.is_tool_allowed(...)` block). We
    return the would-be ValueError message so the test can assert on it
    without swallowing a real exception.
    """
    if not registry.is_tool_allowed(tool_name):
        try:
            same_prefix = sorted({
                n for n in registry.tools.keys()
                if isinstance(n, str)
                and isinstance(tool_name, str)
                and len(n) > 0
                and len(tool_name) > 0
                and n.split('_', 1)[0] == tool_name.split('_', 1)[0]
            })[:5]
        except Exception:
            same_prefix = []
        hint = f" Did you mean one of: {same_prefix}?" if same_prefix else ""
        registered_count = len(registry.tools)
        return (
            f"Tool '{tool_name}' is not in the registered tool "
            f"registry ({registered_count} tools available).{hint}"
        )
    return None  # allowed


# ---------------------------------------------------------------------------
# TA-1 / TA-2 / TA-3 — is_tool_allowed: positive / meta / negative paths.
# ---------------------------------------------------------------------------

class TestIsToolAllowed(unittest.TestCase):

    def test_registered_tool_is_allowed(self):
        """TA-1: any name that exists in registry.tools passes."""
        reg = _MockRegistry({
            "list_inhouse_print_orders": {},
            "execute_tool": {},
            "search_products": {},
        })
        self.assertTrue(reg.is_tool_allowed("list_inhouse_print_orders"))
        self.assertTrue(reg.is_tool_allowed("search_products"))

    def test_meta_tools_are_allowed_via_fallback(self):
        """TA-2: the two meta-tools are allowed via the constant set even
        when not present in registry.tools. This is critical because the
        meta-tool branch in the agentic loop imports them directly from
        `tools.implementations.meta_tools` and bypasses `self.implementations`."""
        reg = _MockRegistry({})  # empty registry
        self.assertTrue(reg.is_tool_allowed("get_tool_schema"))
        self.assertTrue(reg.is_tool_allowed("execute_tool"))

    def test_hallucinated_tool_is_rejected(self):
        """TA-3: any name not in tools and not in the meta-tool set is False."""
        reg = _MockRegistry({
            "list_inhouse_print_orders": {},
            "search_products": {},
        })
        # These are fabricated names that a reasoning-amplified model
        # might emit — server-side gate must reject all of them.
        self.assertFalse(reg.is_tool_allowed("send_email_to_user"))
        self.assertFalse(reg.is_tool_allowed("lookup_weather"))
        self.assertFalse(reg.is_tool_allowed("list_orders_for_me"))
        # A name that's close-but-not-equal to a registered one
        self.assertFalse(reg.is_tool_allowed("list_inhouse_print_order"))  # singular
        self.assertFalse(reg.is_tool_allowed("search_product"))  # singular

    def test_non_string_inputs_rejected(self):
        """TA-4: None, empty string, ints, lists, dicts — all rejected.

        Catches the bug where `tool_use.get('name')` returns a non-string
        (e.g. None for malformed tool_use blocks, or an int if the model
        emits a number) and the gate would otherwise raise TypeError on
        `tool_name in self.tools`.
        """
        reg = _MockRegistry({"anything": {}})
        for bad in (None, "", 0, 1, 42, [], {}, ["x"], {"name": "x"}):
            with self.subTest(bad=bad):
                self.assertFalse(reg.is_tool_allowed(bad))


# ---------------------------------------------------------------------------
# TA-5 — list_tool_names is well-formed.
# ---------------------------------------------------------------------------

class TestListToolNames(unittest.TestCase):

    def test_returns_list_of_strings(self):
        reg = _MockRegistry({"a": {}, "b": {}, "c": {}})
        names = reg.list_tool_names()
        self.assertIsInstance(names, list)
        self.assertEqual(set(names), {"a", "b", "c"})
        for n in names:
            self.assertIsInstance(n, str)

    def test_empty_registry_returns_empty_list(self):
        reg = _MockRegistry({})
        self.assertEqual(reg.list_tool_names(), [])

    def test_returns_sorted(self):
        """Per docstring: 'cheap O(N log N)' and sorted. We rely on this
        for deterministic error messages in production."""
        reg = _MockRegistry({"zeta": {}, "alpha": {}, "mu": {}})
        self.assertEqual(reg.list_tool_names(), ["alpha", "mu", "zeta"])


# ---------------------------------------------------------------------------
# TA-6 — constant invariant. If somebody widens the meta-tool set, this
# test forces them to also update the production code AND the comment in
# CLAUDE.md / TOOL_SYSTEM_ROBUSTNESS_2026-07-26.md.
# ---------------------------------------------------------------------------

class TestMetaToolConstant(unittest.TestCase):

    def test_exactly_two_meta_tools(self):
        self.assertEqual(
            _MockRegistry._ALLOWED_META_TOOL_NAMES,
            frozenset({"get_tool_schema", "execute_tool"}),
        )

    def test_meta_tools_are_strings(self):
        for name in _MockRegistry._ALLOWED_META_TOOL_NAMES:
            self.assertIsInstance(name, str)
            self.assertTrue(name)


# ---------------------------------------------------------------------------
# TA-7 / TA-8 / TA-9 — gate decision produces structured error messages.
# ---------------------------------------------------------------------------

class TestGateDecision(unittest.TestCase):

    def test_known_tool_returns_none(self):
        """TA-7: a known tool_name returns None (allowed)."""
        reg = _MockRegistry({"list_orders": {}})
        self.assertIsNone(_gate_decision(reg, "list_orders"))

    def test_meta_tool_returns_none(self):
        reg = _MockRegistry({})
        self.assertIsNone(_gate_decision(reg, "get_tool_schema"))
        self.assertIsNone(_gate_decision(reg, "execute_tool"))

    def test_unknown_tool_returns_error_message(self):
        """TA-7: an unknown tool_name returns a structured error message
        that the agentic loop will wrap in a ValueError."""
        reg = _MockRegistry({"list_orders": {}, "search_products": {}})
        msg = _gate_decision(reg, "send_email_to_user")
        self.assertIsNotNone(msg)
        self.assertIn("send_email_to_user", msg)
        self.assertIn("not in the registered tool registry", msg)
        self.assertIn("2 tools available", msg)

    def test_hint_when_same_prefix_exists(self):
        """TA-8: when the hallucinated name shares a prefix with a
        real tool, the error message includes a 'Did you mean' hint.
        Example: model emits 'list_order' (missing trailing s),
        the hint suggests 'list_orders'."""
        reg = _MockRegistry({
            "list_orders": {},
            "list_users": {},
            "search_products": {},
        })
        msg = _gate_decision(reg, "list_order")
        self.assertIsNotNone(msg)
        self.assertIn("Did you mean one of:", msg)
        # Both list_* should appear in the hint (shared prefix 'list').
        self.assertIn("list_orders", msg)
        self.assertIn("list_users", msg)
        # The non-matching tool should NOT appear in the hint.
        self.assertNotIn("search_products", msg)

    def test_no_hint_when_no_prefix_match(self):
        """TA-9: when no registered tool shares a prefix, the error
        message omits the 'Did you mean' hint (it would be empty)."""
        reg = _MockRegistry({"search_products": {}, "calculate": {}})
        msg = _gate_decision(reg, "totally_unrelated_xyz")
        self.assertIsNotNone(msg)
        self.assertNotIn("Did you mean", msg)

    def test_hint_capped_at_five(self):
        """TA-8 follow-up: if more than 5 tools share a prefix, the
        hint should list at most 5 (sliced in the production code)."""
        reg = _MockRegistry({
            f"list_{i}": {} for i in range(20)
        })
        msg = _gate_decision(reg, "list_x")
        self.assertIsNotNone(msg)
        # Count comma-separated names in the hint section.
        m = re.search(r"Did you mean one of: \[(.*?)\]\?", msg)
        self.assertIsNotNone(m)
        names = [n.strip().strip("'") for n in m.group(1).split(",")]
        self.assertLessEqual(len(names), 5)

    def test_empty_string_rejected(self):
        """TA-4 follow-up: at the gate level, an empty tool_name also
        produces an error message (it doesn't crash on the split())."""
        reg = _MockRegistry({"x": {}})
        msg = _gate_decision(reg, "")
        self.assertIsNotNone(msg)

    def test_non_string_does_not_crash(self):
        """TA-4 follow-up: a non-string tool_name must not raise — it
        must produce a structured error message. This catches a bug
        where the prefix-split would crash on a non-string."""
        reg = _MockRegistry({"x": {}})
        # None: should not raise
        msg = _gate_decision(reg, None)
        self.assertIsNotNone(msg)
        self.assertIn("None", msg)
        # int: should not raise
        msg = _gate_decision(reg, 42)
        self.assertIsNotNone(msg)
        self.assertIn("42", msg)


# ---------------------------------------------------------------------------
# TA-10 — integration sanity check: the source file we edited actually
# contains the gate. This protects against accidental deletion by a
# future agent or by a sloppy git revert.
# ---------------------------------------------------------------------------

class TestSourceInvariants(unittest.TestCase):

    def _worker_path(self):
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(
            os.path.join(here, "..", "core", "combined_agent_worker.py")
        )

    def _registry_path(self):
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(
            os.path.join(here, "..", "..", "tools", "registry_v3.py")
        )

    def test_worker_contains_gate(self):
        path = self._worker_path()
        self.assertTrue(os.path.isfile(path), f"missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        # The gate comment + the call must be present.
        self.assertIn("registry.is_tool_allowed(tool_name)", src)
        self.assertIn("TOOL-ALLOWLIST", src)

    def test_registry_contains_helper(self):
        path = self._registry_path()
        self.assertTrue(os.path.isfile(path), f"missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        self.assertIn("def is_tool_allowed(", src)
        self.assertIn("def list_tool_names(", src)
        self.assertIn(
            '_ALLOWED_META_TOOL_NAMES = frozenset({"get_tool_schema", "execute_tool"})',
            src,
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Make sure the AI_agents root is on sys.path for any future test
    # that imports production modules. Currently we mock everything we
    # need, but keeping the path setup makes this file robust to future
    # additions (e.g. integration tests against the real RegistryV3).
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    unittest.main(verbosity=2)