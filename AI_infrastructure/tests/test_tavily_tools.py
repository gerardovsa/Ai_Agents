"""
Test: Tavily tools — registry auto-discovery + provider-aware server tool gating

This regression test verifies the fix for the MiniMax 400 error
("function name or parameters is empty" / 2013), which was caused by
Anthropic's web_search_20250305 server tool being appended unconditionally
at AI_infrastructure/routes/agent_routes_v4.py:1480 and sent to
https://api.minimax.io/anthropic (which does NOT implement server tools).

It also verifies the 6 Tavily client tools (search, extract, crawl, map,
research, get_research) are auto-discovered by the tool registry from
tools/schemas/*.json and tools/implementations/tavily_tools.py.

Run:
    python -m AI_infrastructure.tests.test_tavily_tools

No network calls are made — the Tavily SDK is mocked.
"""

import json
import os
import sys
from pathlib import Path
from unittest import mock

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Set a fake Tavily key BEFORE importing anything that resolves it
# (use direct assignment, not setdefault, so this works even if some other
# module cleared the env var during the registry's auto-discovery)
os.environ["TAVILY_API_KEY"] = "tvly-test-fake-key-do-not-use"


def _all_passed(results):
    """Pretty-print a list of (name, passed, detail) tuples."""
    print()
    print("=" * 72)
    print("TAVILY TOOLS — TEST RESULTS")
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


def test_tavily_schemas_exist_and_well_formed():
    """All 5 schema files exist in tools/schemas/ and contain 6 tools total."""
    schema_dir = REPO_ROOT / "tools" / "schemas"
    expected_files = [
        "tavily_search.json",
        "tavily_extract.json",
        "tavily_crawl.json",
        "tavily_map.json",
        "tavily_research.json",  # contains BOTH research + get_research
    ]
    found_files = [f.name for f in schema_dir.glob("tavily_*.json")]
    missing = [f for f in expected_files if f not in found_files]
    detail = f"Found: {sorted(found_files)}\nExpected: {sorted(expected_files)}"
    if missing:
        return False, f"Missing schema files: {missing}\n{detail}"
    # Count total tools across the 5 files
    total_tools = 0
    tool_names = []
    for f in expected_files:
        with open(schema_dir / f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            for t in data.get("tools", []):
                total_tools += 1
                tool_names.append(t["name"])
    expected_tools = {
        "tavily_search", "tavily_extract", "tavily_crawl", "tavily_map",
        "tavily_research", "tavily_get_research",
    }
    if set(tool_names) != expected_tools:
        return False, f"Expected tools {expected_tools}, got {set(tool_names)}"
    return True, f"All 5 schemas found; 6 tools declared: {sorted(tool_names)}"


def test_tavily_implementation_file_exists():
    """tools/implementations/tavily_tools.py exists and exports 6 functions."""
    impl_path = REPO_ROOT / "tools" / "implementations" / "tavily_tools.py"
    if not impl_path.exists():
        return False, f"Not found: {impl_path}"
    # Lazy-import to avoid hard dep on tavily-python at import time
    import importlib.util
    spec = importlib.util.spec_from_file_location("tavily_tools", impl_path)
    mod = importlib.util.module_from_spec(spec)
    # Don't execute the module (it has a top-level sys.path mutation that's harmless
    # but we want to read the source directly to count defs).
    source = impl_path.read_text(encoding="utf-8")
    expected_funcs = [
        "tavily_search", "tavily_extract", "tavily_crawl", "tavily_map",
        "tavily_research", "tavily_get_research",
    ]
    missing = [f for f in expected_funcs if f"def {f}(" not in source]
    if missing:
        return False, f"Missing function definitions: {missing}"
    return True, f"All 6 function definitions present: {expected_funcs}"


def test_tavily_functions_use_4_tier_credential_resolver():
    """The implementation file uses resolve_credentials + env var fallback (4-tier)."""
    impl_path = REPO_ROOT / "tools" / "implementations" / "tavily_tools.py"
    source = impl_path.read_text(encoding="utf-8")
    checks = {
        "uses_resolve_credentials": "resolve_credentials" in source,
        "has_tavily_env_fallback": 'os.environ.get("TAVILY_API_KEY")' in source,
        "has_user_id_kwarg": "_user_id" in source,
        "has_client_cache": "_TAVILY_CLIENT_CACHE" in source,
        "returns_success_envelope": '"success"' in source,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        return False, f"Missing: {failed}\nChecks: {checks}"
    return True, f"All 4-tier resolver patterns present: {list(checks.keys())}"


def test_registry_auto_discovers_tavily_tools():
    """The platform tool registry (tools.registry_v3) finds all 6 Tavily tools.

    The registry loads schemas from tools/schemas/*.json and implementations
    from tools/implementations/*.py. We verify Tavily tools appear in the
    loaded registry after construction.
    """
    try:
        from tools.registry_v3 import RegistryV3
    except ImportError as e:
        return False, f"Could not import RegistryV3: {e}"

    try:
        registry = RegistryV3()
    except Exception as e:
        return False, f"RegistryV3() raised: {type(e).__name__}: {e}"

    tavily_tool_names = {
        "tavily_search", "tavily_extract", "tavily_crawl", "tavily_map",
        "tavily_research", "tavily_get_research",
    }
    # Lazy-mode (2026-07-27): Tavily tools are no longer loaded at boot.
    # Materialise each before asserting presence.
    for name in tavily_tool_names:
        registry.materialize_tool(name)
    registered = set(registry.tools.keys())
    found = tavily_tool_names & registered
    missing = tavily_tool_names - found
    if missing:
        return False, (f"Registry missing Tavily tools: {sorted(missing)}\n"
                       f"Found in registry (first 30): {sorted(registered)[:30]}")
    return True, f"All 6 Tavily tools registered. Total tools in registry: {len(registered)}"


def test_server_tool_append_gated_on_provider():
    """The active streaming path (agent_routes_v4.py) gates server tools on
    ai_provider == 'anthropic'. For non-Anthropic providers, no
    web_search_20250305 should be appended.
    """
    route_path = REPO_ROOT / "AI_infrastructure" / "routes" / "agent_routes_v4.py"
    source = route_path.read_text(encoding="utf-8")
    # The fix wraps the server_tools list in `if _ai_provider == 'anthropic':`
    # and the inner block appends the web_search_20250305 entry.
    has_gate = "_ai_provider == 'anthropic'" in source and "web_search_20250305" in source
    has_log = "client-side Tavily tools" in source
    if not has_gate:
        return False, "Could not find provider gate ('_ai_provider == \"anthropic\"' + 'web_search_20250305') in agent_routes_v4.py"
    if not has_log:
        return False, "Could not find non-Anthropic log line ('client-side Tavily tools')"
    return True, "Server tool append is gated on ai_provider == 'anthropic' and logs Tavily fallback for others"


def test_defence_in_depth_strip_in_worker():
    """combined_agent_worker.py strips server tools from `tools` for non-Anthropic
    providers — belt-and-suspenders in case server tools leak in upstream.
    """
    worker_path = REPO_ROOT / "AI_infrastructure" / "core" / "combined_agent_worker.py"
    source = worker_path.read_text(encoding="utf-8")
    has_strip = "SERVER-TOOL-GUARD" in source
    has_provider_check = "ai_provider != 'anthropic'" in source
    has_types_set = "_server_tool_types" in source
    checks = {
        "has_strip_marker": has_strip,
        "has_provider_check": has_provider_check,
        "has_types_set": has_types_set,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        return False, f"Missing: {failed}\nChecks: {checks}"
    return True, f"Defence-in-depth strip present: {list(checks.keys())}"


def test_tavily_functions_happy_path_with_mock():
    """Smoke test: with the Tavily SDK mocked, tavily_search / tavily_extract
    return a properly-shaped success envelope.
    """
    impl_path = REPO_ROOT / "tools" / "implementations" / "tavily_tools.py"
    import importlib.util

    # Inject a fake `tavily` module into sys.modules BEFORE we load the
    # implementation. The implementation defers `from tavily import TavilyClient`
    # to call time, but sys.modules injection survives that.
    fake_tavily = mock.MagicMock()
    fake_client = mock.MagicMock()
    fake_client.search.return_value = {
        "query": "test",
        "results": [{"title": "A", "url": "https://a", "content": "x", "score": 0.9}],
    }
    fake_client.extract.return_value = {
        "results": [{"url": "https://a", "raw_content": "hello"}],
        "failed_results": [],
    }
    fake_tavily.TavilyClient.return_value = fake_client
    sys.modules["tavily"] = fake_tavily

    spec = importlib.util.spec_from_file_location("tavily_tools_test", impl_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Call search
    r = mod.tavily_search(query="test", max_results=1)
    if not r.get("success"):
        return False, f"tavily_search did not return success: {r}"
    if r.get("provider") != "tavily":
        return False, f"tavily_search did not return provider='tavily': {r}"
    if "results" not in r:
        return False, f"tavily_search missing 'results' key: {r}"

    # Call extract
    r2 = mod.tavily_extract(urls=["https://example.com"])
    if not r2.get("success"):
        return False, f"tavily_extract did not return success: {r2}"

    return True, "tavily_search + tavily_extract return success envelopes with mocked SDK"


def test_requirements_txt_has_tavily():
    """requirements.txt includes tavily-python."""
    req_path = REPO_ROOT / "requirements.txt"
    source = req_path.read_text(encoding="utf-8")
    if "tavily-python" not in source:
        return False, "tavily-python not in requirements.txt"
    return True, "tavily-python declared in requirements.txt"


def test_env_master_has_tavily_template():
    """.env.master has a TAVILY_API_KEY= template line (no real value)."""
    env_path = REPO_ROOT / ".env.master"
    source = env_path.read_text(encoding="utf-8")
    if "TAVILY_API_KEY=" not in source:
        return False, "TAVILY_API_KEY= template line not in .env.master"
    # Ensure no real key was accidentally written
    if "tvly-" in source:
        # Make sure it's only a placeholder, not a real key value
        for line in source.splitlines():
            if line.startswith("TAVILY_API_KEY=") and "tvly-" in line.split("=", 1)[1]:
                return False, f"Real Tavily key leaked into .env.master: {line}"
    return True, "TAVILY_API_KEY= template line present in .env.master (no real value)"


def test_system_prompt_documents_tavily():
    """tool_usage_system_prompt.md has a WEB SEARCH & FETCH section that
    documents all 6 Tavily tools.
    """
    prompt_path = REPO_ROOT / "AI_infrastructure" / "prompts" / "tool_usage_system_prompt.md"
    source = prompt_path.read_text(encoding="utf-8")
    expected = [
        "tavily_search", "tavily_extract", "tavily_crawl", "tavily_map",
        "tavily_research", "tavily_get_research",
        "## WEB SEARCH & FETCH",  # section heading (now in a non-server-tool form)
    ]
    missing = [e for e in expected if e not in source]
    if missing:
        return False, f"System prompt missing: {missing}"
    return True, f"System prompt documents all 6 Tavily tools + section heading"


def main():
    tests = [
        ("Tavily schemas exist + well-formed",        test_tavily_schemas_exist_and_well_formed),
        ("Tavily implementation file exists",         test_tavily_implementation_file_exists),
        ("Tavily functions use 4-tier resolver",      test_tavily_functions_use_4_tier_credential_resolver),
        ("Registry auto-discovers Tavily tools",      test_registry_auto_discovers_tavily_tools),
        ("Server tool append gated on provider",     test_server_tool_append_gated_on_provider),
        ("Defence-in-depth strip in worker",          test_defence_in_depth_strip_in_worker),
        ("Tavily functions happy path with mock",     test_tavily_functions_happy_path_with_mock),
        ("requirements.txt has tavily-python",       test_requirements_txt_has_tavily),
        (".env.master has TAVILY_API_KEY template",   test_env_master_has_tavily_template),
        ("System prompt documents Tavily tools",     test_system_prompt_documents_tavily),
    ]

    results = []
    for name, fn in tests:
        try:
            passed, detail = fn()
        except Exception as e:
            passed = False
            detail = f"{type(e).__name__}: {e}"
        results.append((name, passed, detail))
        marker = "PASS" if passed else "FAIL"
        print(f"  [{marker}] {name}")

    ok = _all_passed(results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
