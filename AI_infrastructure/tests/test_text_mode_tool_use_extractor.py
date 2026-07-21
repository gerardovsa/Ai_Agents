"""
Test: Text-mode tool_use extractor — regression for MiniMax-M3 fence-strip crash

Bug (July 2026):
    MiniMax-M3 (and other M-series chat-completion-tuned models) imitate
    markdown structure and emit Anthropic-style `tool_use` JSON objects
    wrapped in ```json ... ``` fences *inside* a text block. The dispatch
    loop in `combined_agent_worker.execute_streaming_request` only listens
    for native `content_block_start(block.type='tool_use')` events, so the
    fenced JSON landed as dead text — `stop_reason` stayed `end_turn`, the
    chat appeared to "crash" silently, and the tool never ran.

Fix:
    `_extract_text_mode_tool_uses(text)` walks every `"type":"tool_use"`
    marker in the assistant's text content, walks back to the opening
    brace, parses a balanced-JSON object via `json.JSONDecoder.raw_decode`,
    and returns a list of synthetic Anthropic-shaped tool_use dicts with
    IDs prefixed `toolu_textmode_<hex>`. The dispatcher then overrides
    `stop_reason` from `end_turn` to `tool_use` and the tool loop kicks
    in.

This test pins the 7 behaviours that the extractor must get right:
    1. fenced   - ```json ... ``` wrapper is stripped
    2. raw      - bare native tool_use JSON also recovered
    3. plain    - natural-prose text containing no tool_use returns []
    4. multi    - two tool_uses in one response both recovered
    5. dedupe   - identical (name, input) emitted twice → deduped to one
    6. wrapped  - tool_use JSON embedded inside an outer message envelope
    7. broken   - malformed JSON around a `"type":"tool_use"` marker → []
                  (must NOT crash the turn)

Run:
    python -m AI_infrastructure.tests.test_text_mode_tool_use_extractor

No network calls. No Flask app context. Imports only `_extract_text_mode_tool_uses`
from the core worker module (which has stdlib + tiktoken top-level deps only).
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable, List, Tuple

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import the helper under test. combined_agent_worker has stdlib + tiktoken at
# module level; no Flask / no DB / no network. Safe to import in isolation.
from AI_infrastructure.core.combined_agent_worker import (  # noqa: E402
    _extract_text_mode_tool_uses,
)


def _all_passed(results: List[Tuple[str, bool, str]]) -> bool:
    """Pretty-print a list of (name, passed, detail) tuples."""
    print()
    print("=" * 72)
    print("TEXT-MODE TOOL_USE EXTRACTOR — TEST RESULTS")
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
# The M3 bug case the fix is anchored on
# -----------------------------------------------------------------------------

M3_FENCED_TOOL_USE = (
    "Sure, I'll list the available chart types for you.\n\n"
    "```json\n"
    "{\n"
    '  "type": "tool_use",\n'
    '  "name": "list_visualization_types",\n'
    '  "input": {\n'
    '    "filter_by": "charts"\n'
    '  }\n'
    "}\n"
    "```\n"
)


def test_fenced_minimax_m3_case():
    """The exact M3 failure shape must be recovered to a native tool_use dict."""
    found = _extract_text_mode_tool_uses(M3_FENCED_TOOL_USE)
    ok = (
        len(found) == 1
        and found[0]["name"] == "list_visualization_types"
        and found[0]["input"] == {"filter_by": "charts"}
        and found[0]["id"].startswith("toolu_textmode_")
        and found[0]["_source"] == "text_mode_extractor"
    )
    return ok, f"recovered: {found!r}" if ok else f"got {found!r} (expected 1 tool_use)"


# -----------------------------------------------------------------------------
# Defensive coverage for adjacent shapes
# -----------------------------------------------------------------------------

RAW_NATIVE_JSON = (
    '{"type":"tool_use","name":"tavily_search","input":{"query":"python 3.13"}}'
)


def test_raw_native_json_also_works():
    """Fence-less native JSON should also be recovered (defence in depth)."""
    found = _extract_text_mode_tool_uses(RAW_NATIVE_JSON)
    ok = (
        len(found) == 1
        and found[0]["name"] == "tavily_search"
        and found[0]["input"] == {"query": "python 3.13"}
    )
    return ok, f"recovered: {found!r}"


PLAIN_PROSE = (
    "The capital of France is Paris. Let me know if you'd like more details."
)


def test_plain_prose_returns_empty():
    """Natural prose with no tool_use marker must not be misparsed."""
    found = _extract_text_mode_tool_uses(PLAIN_PROSE)
    ok = found == []
    return ok, f"got {found!r}"


TWO_DISTINCT_CALLS = (
    '```json\n'
    '{"type":"tool_use","name":"tavily_search","input":{"query":"a"}}\n'
    '```\n'
    '```json\n'
    '{"type":"tool_use","name":"tavily_extract","input":{"urls":["https://example.com"]}}\n'
    '```\n'
)


def test_multiple_tool_uses_in_one_response():
    """Two distinct tool_uses in one assistant turn must both be recovered."""
    found = _extract_text_mode_tool_uses(TWO_DISTINCT_CALLS)
    names = sorted(t["name"] for t in found)
    ok = (
        len(found) == 2
        and names == ["tavily_extract", "tavily_search"]
        and found[0]["id"] != found[1]["id"]   # IDs are unique
    )
    return ok, f"names={names}, ids_unique={found[0]['id'] != found[1]['id'] if len(found)==2 else False}"


DUPLICATE_CALLS = (
    '```json\n'
    '{"type":"tool_use","name":"tavily_search","input":{"query":"x"}}\n'
    '```\n'
    '```json\n'
    '{"type":"tool_use","name":"tavily_search","input":{"query":"x"}}\n'
    '```\n'
)


def test_duplicate_tool_uses_deduped():
    """Identical (name, input) emitted twice → only one tool_use dispatched."""
    found = _extract_text_mode_tool_uses(DUPLICATE_CALLS)
    ok = len(found) == 1
    return ok, f"got {len(found)} (expected 1 after dedupe)"


# JSON envelope around the tool_use block, e.g. an outbound assistant
# message shape that wraps tool_use in a larger structured response.
WRAPPED_ENVELOPE = (
    'I will fetch that.\n'
    '{\n'
    '  "role": "assistant",\n'
    '  "content": {\n'
    '    "type": "tool_use",\n'
    '    "name": "tavily_map",\n'
    '    "input": { "url": "https://example.com", "limit": 10 }\n'
    '  }\n'
    '}\n'
)


def test_wrapped_envelope_recovers_inner_tool_use():
    """Tool_use JSON inside a larger outer envelope must still be recovered."""
    found = _extract_text_mode_tool_uses(WRAPPED_ENVELOPE)
    ok = (
        len(found) == 1
        and found[0]["name"] == "tavily_map"
        and found[0]["input"] == {"url": "https://example.com", "limit": 10}
    )
    return ok, f"recovered: {found!r}"


# A `"type":"tool_use"` substring that is NOT inside valid JSON, with broken
# braces around it. The extractor must NOT raise — it must return [].
BROKEN_NEAR_MARKER = (
    "Here is what I tried: { \"type\": \"tool_use\", \"name\": "
    # truncated / unbalanced
)


def test_broken_json_returns_empty_no_crash():
    """Broken JSON around a marker must NOT crash; must return []."""
    try:
        found = _extract_text_mode_tool_uses(BROKEN_NEAR_MARKER)
    except Exception as exc:  # noqa: BLE001
        return False, f"raised {type(exc).__name__}: {exc}"
    return found == [], f"got {found!r} (expected [])"


def main() -> int:
    """Run every check and exit 0 / 1 based on aggregate result."""
    checks: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
        ("fenced — M3 fence-strip case (the bug)",
         test_fenced_minimax_m3_case),
        ("raw   — fence-less native JSON also recovered",
         test_raw_native_json_also_works),
        ("plain — natural prose returns empty",
         test_plain_prose_returns_empty),
        ("multi — two distinct tool_uses both recovered",
         test_multiple_tool_uses_in_one_response),
        ("dedupe — identical calls collapsed to one",
         test_duplicate_tool_uses_deduped),
        ("wrapped — tool_use inside outer envelope recovered",
         test_wrapped_envelope_recovers_inner_tool_use),
        ("broken — malformed JSON returns [] and does not crash",
         test_broken_json_returns_empty_no_crash),
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
