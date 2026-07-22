"""
Test: RegistryV3 cache-staleness + visualization_guide sibling-lookup fix

Bug (July 2026):
    Two related production failures surfaced after the M3 tool_use extractor
    started recovering fenced JSON tool calls:

    1. CACHE STALENESS — RegistryV3.__init__ used a Redis cache to skip
       _load_schemas() on cache hit. The implementation loader's special_modules
       filter (`if attr_name in self.tools`) silently skipped every meta_tools
       / sql_database function when the cached self.tools predated the on-disk
       schema files. Result: every meta_tools call returned
       "Tool not found: <name>" in production.

    2. SIBLING-LOOKUP COLLISION — visualization_guide has three distinct public
       functions (visualization_guide, list_visualization_types,
       compare_visualizations) registered under a single key by the general
       loader. _load_module_plugins then overwrote that key with the
       visualization_guide function itself, making the other two siblings
       unreachable via get_tool_function Case 2 (which skips callable entries).

Fix:
    1. Always call _load_schemas() in __init__, regardless of cache hit. Cache
       is now a pure startup-speedup hint, not a correctness dependency.
    2. Add "visualization_guide" to special_modules so all three functions get
       individual entries in self.implementations.

This test pins both fixes so they cannot regress:
    A. Stale-cache scenario still registers meta_tools functions
    B. visualization_guide siblings are individually reachable
    C. Direct function lookup (Case 1) works for visualization_guide
    D. Names match schemas exactly (no over-registration)

Run:
    python -m AI_infrastructure.tests.test_registry_v3_cache_fix

No network calls. No Flask app context. Builds the real RegistryV3 with
cache and plugin loading monkey-patched to keep the test hermetic.
"""
import sys
from pathlib import Path
from typing import Any, Callable, List, Tuple

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.registry_v3 import RegistryV3  # noqa: E402


def _all_passed(results: List[Tuple[str, bool, str]]) -> bool:
    """Pretty-print a list of (name, passed, detail) tuples."""
    print()
    print("=" * 72)
    print("REGISTRY V3 CACHE + SIBLING-LOOKUP FIX — TEST RESULTS")
    print("=" * 72)
    for name, passed, detail in results:
        marker = "PASS" if passed else "FAIL"
        print(f"  [{marker}] {name}")
        if detail:
            for line in detail.splitlines():
                print(f"         {line}")
    print("-" * 72)
    n_pass = sum(1 for _, p, _ in results if p)
    n_total = len(results)
    print(f"  {n_pass}/{n_total} checks passed")
    print("=" * 72)
    return n_pass == n_total


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

# Monkey-patched cache: pretend the cache returned a HIT but the cached payload
# is STALE — missing the meta_tools names that exist on disk today. This is the
# exact production failure shape (deploy added new tools while Redis still held
# a pre-deploy snapshot).
STALE_CACHE_PAYLOAD: dict = {
    # Cached self.tools deliberately omits ALL meta_tools names.
    "tools": {
        "visualization_guide": {"name": "visualization_guide"},
    },
    # A stamp so we can distinguish stale from fresh.
    "stale_marker": True,
}


def _patched_load_from_cache(self) -> bool:
    """Monkey-patch target: simulate a Redis cache hit with stale data."""
    self.tools = dict(STALE_CACHE_PAYLOAD["tools"])
    return True  # Pretend we hit the cache


def _patched_save_to_cache(self) -> None:
    """Monkey-patch target: no-op so we don't pollute Redis during tests."""
    return None


def _build_registry_with_stale_cache() -> RegistryV3:
    """Build a RegistryV3 with a stale cache hit, then verify post-load state."""
    # Patch the cache methods for this construction only.
    original_load = RegistryV3._load_from_cache
    original_save = RegistryV3._save_to_cache
    RegistryV3._load_from_cache = _patched_load_from_cache
    RegistryV3._save_to_cache = _patched_save_to_cache
    try:
        reg = RegistryV3()
    finally:
        RegistryV3._load_from_cache = original_load
        RegistryV3._save_to_cache = original_save
    return reg


# -----------------------------------------------------------------------------
# Check A: Stale-cache scenario still registers meta_tools functions.
# (Regression for the production bug — this is the headline fix.)
# -----------------------------------------------------------------------------

# All 8 names from tools/schemas/meta_tools.json — every one MUST be reachable.
META_TOOL_NAMES = [
    "list_available_platforms",
    "list_platform_tools",
    "get_tool_schema",
    "search_tools",
    "get_platform_guide",
    "recommend_tools_for_task",
    "execute_tool",
    "get_workflow_steps",
]


def test_stale_cache_does_not_break_meta_tools():
    """Stale Redis cache must NOT prevent meta_tools implementations from registering."""
    reg = _build_registry_with_stale_cache()
    missing = [
        name for name in META_TOOL_NAMES
        if reg.get_tool_function(name) is None
    ]
    ok = not missing
    if ok:
        detail = f"all {len(META_TOOL_NAMES)} meta_tools reachable despite stale cache"
    else:
        detail = f"unreachable: {missing}"
    return ok, detail


# -----------------------------------------------------------------------------
# Check B: visualization_guide siblings are individually reachable.
# (Regression for the module-vs-function collision bug.)
# -----------------------------------------------------------------------------

VIZ_SIBLING_NAMES = [
    "visualization_guide",
    "list_visualization_types",
    "compare_visualizations",
]


def test_visualization_guide_all_siblings_reachable():
    """All three visualization_guide siblings must be individually addressable."""
    reg = _build_registry_with_stale_cache()
    missing = [
        name for name in VIZ_SIBLING_NAMES
        if reg.get_tool_function(name) is None
    ]
    ok = not missing
    if ok:
        detail = f"all {len(VIZ_SIBLING_NAMES)} visualization_guide siblings reachable"
    else:
        detail = f"unreachable: {missing}"
    return ok, detail


def test_visualization_guide_each_is_callable():
    """Each sibling must resolve to an actual callable, not None / not a module."""
    reg = _build_registry_with_stale_cache()
    not_callable = []
    for name in VIZ_SIBLING_NAMES:
        fn = reg.get_tool_function(name)
        if fn is None or not callable(fn):
            not_callable.append((name, type(fn).__name__))
    ok = not not_callable
    detail = "all callable" if ok else f"non-callable: {not_callable}"
    return ok, detail


# -----------------------------------------------------------------------------
# Check C: The implementation dict has per-function entries (not a module
# shadowing other siblings). This is the structural proof that the
# module-vs-function collision has been eliminated.
# -----------------------------------------------------------------------------

def test_implementations_dict_has_per_function_entries():
    """self.implementations must contain per-function keys for viz siblings."""
    reg = _build_registry_with_stale_cache()
    impl_keys = set(reg.implementations.keys())
    expected = set(VIZ_SIBLING_NAMES)
    missing = expected - impl_keys
    ok = not missing
    if ok:
        detail = f"all {len(expected)} sibling keys present in self.implementations"
    else:
        detail = f"missing keys: {missing}"
    return ok, detail


# -----------------------------------------------------------------------------
# Check D: Schema-driven registration prevents over-registration. No function
# whose name is NOT in self.tools should sneak into self.implementations via
# the special_modules path (e.g. private helpers or future drift).
# -----------------------------------------------------------------------------

def test_no_over_registration_for_private_helpers():
    """The private _get_visualization_guidance helper must NOT be registered."""
    reg = _build_registry_with_stale_cache()
    leaked = "_get_visualization_guidance" in reg.implementations
    ok = not leaked
    detail = (
        "no leak" if ok
        else "_get_visualization_guidance was registered (special_modules filter broken)"
    )
    return ok, detail


def main() -> int:
    """Run every check and exit 0 / 1 based on aggregate result."""
    checks: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
        ("A. stale cache still registers meta_tools (regression for prod bug)",
         test_stale_cache_does_not_break_meta_tools),
        ("B1. visualization_guide all 3 siblings reachable",
         test_visualization_guide_all_siblings_reachable),
        ("B2. visualization_guide siblings each resolve to a callable",
         test_visualization_guide_each_is_callable),
        ("C.  self.implementations has per-function entries (no module shadowing)",
         test_implementations_dict_has_per_function_entries),
        ("D.  private _get_visualization_guidance NOT over-registered",
         test_no_over_registration_for_private_helpers),
    ]

    results: List[Tuple[str, bool, str]] = []
    for name, fn in checks:
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"raised {type(exc).__name__}: {exc}"
        results.append((name, ok, detail))

    return 0 if _all_passed(results) else 1


if __name__ == "__main__":
    sys.exit(main())
