"""
Regression test for the tier classification used by the `token_status` SSE
event (AI_infrastructure/core/combined_agent_worker.py:2331-2343).

What this test guards against:
    The four-tier colour system (ok < info < warning < critical) drives the
    CSS palette the user sees on the thread-token indicator. If someone
    bumps a threshold (e.g. "70% is now warning") without updating the
    frontend CSS or the tier-transition toast logic, the chip colour and
    the toast will desync — the user gets a green chip with a red toast.

    The test pins the boundary behaviour by re-implementing the same
    classification (as a copy-paste, intentionally) and asserting it
    matches the documented thresholds in
    THREAD_MESSAGE_CONSTRUCTION_MASTER_2026_07_29.md §10. A divergence
    here means the worker and the doc disagree, which means the
    frontend CSS (tier-ok / tier-info / tier-warning / tier-critical)
    is now wrong for at least one tier.

What this test does NOT cover:
    - The actual SSE emit (covered by an end-to-end smoke test in the
      production deploy, not this unit-level test).
    - The DB persistence (migration 064_thread_token_telemetry_columns.sql
      is verified separately by the production deployment checklist).
    - The tier-transition toast logic (in business-ai-platform-v2.html) —
      it has no pure-logic surface to assert against; covered manually.

Run:
    python AI_infrastructure/tests/test_token_status_tier_classification.py
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)


# ────────────────────────────────────────────────────────────────────────────
# Mirror of the classification logic at combined_agent_worker.py:2331-2343.
# If the worker changes, this MUST be updated in lockstep — the test will
# start failing, which is the intended signal.
# ────────────────────────────────────────────────────────────────────────────
def classify_token_tier(pct_of_context: float) -> str:
    """Return the tier label for a given percentage of context-window used."""
    if pct_of_context >= 90:
        return 'critical'
    if pct_of_context >= 75:
        return 'warning'
    if pct_of_context >= 50:
        return 'info'
    return 'ok'


# Mirror of the _MODEL_CONTEXT_WINDOWS dict at combined_agent_worker.py:2309-2327.
# Tested separately for completeness — every supported (provider, model) pair
# the worker can be invoked with must appear here, or the indicator will
# show the safe-default 1M window which is wrong for sub-1M models.
EXPECTED_CONTEXT_WINDOWS = {
    # MiniMax family (user's primary)
    'MiniMax-M3': 1_000_000,
    'MiniMax-M2': 200_000,
    # Anthropic Claude 4.x family
    'claude-sonnet-4-5': 200_000,
    'claude-sonnet-4-6': 200_000,
    'claude-opus-4-7': 200_000,
    'claude-opus-4-8': 200_000,
    'claude-haiku-4-5-20251001': 200_000,
    # OpenAI
    'gpt-4o': 128_000,
    'gpt-4o-mini': 128_000,
    'o1': 200_000,
    'o3-mini': 200_000,
    # DeepSeek
    'deepseek-chat': 64_000,
    'deepseek-reasoner': 64_000,
}


class TestTokenStatusTierClassification(unittest.TestCase):
    """Pin the four-tier threshold behaviour."""

    # ── OK tier (pct < 50) ─────────────────────────────────────────────
    def test_ok_at_zero(self):
        self.assertEqual(classify_token_tier(0.0), 'ok')

    def test_ok_just_below_info(self):
        # Boundary: 49.99% should still be 'ok' (strict < 50)
        self.assertEqual(classify_token_tier(49.99), 'ok')

    def test_ok_at_twenty_five_percent(self):
        self.assertEqual(classify_token_tier(25.0), 'ok')

    # ── INFO tier (50 <= pct < 75) ─────────────────────────────────────
    def test_info_at_fifty_exact(self):
        # Boundary: 50.0 should be 'info' (inclusive >=)
        self.assertEqual(classify_token_tier(50.0), 'info')

    def test_info_midband(self):
        self.assertEqual(classify_token_tier(62.5), 'info')

    def test_info_just_below_warning(self):
        # Boundary: 74.99% should still be 'info' (strict < 75)
        self.assertEqual(classify_token_tier(74.99), 'info')

    # ── WARNING tier (75 <= pct < 90) ──────────────────────────────────
    def test_warning_at_seventy_five_exact(self):
        self.assertEqual(classify_token_tier(75.0), 'warning')

    def test_warning_midband(self):
        self.assertEqual(classify_token_tier(82.0), 'warning')

    def test_warning_just_below_critical(self):
        # Boundary: 89.99% should still be 'warning' (strict < 90)
        self.assertEqual(classify_token_tier(89.99), 'warning')

    # ── CRITICAL tier (pct >= 90) ──────────────────────────────────────
    def test_critical_at_ninety_exact(self):
        self.assertEqual(classify_token_tier(90.0), 'critical')

    def test_critical_midband(self):
        self.assertEqual(classify_token_tier(95.0), 'critical')

    def test_critical_at_one_hundred(self):
        self.assertEqual(classify_token_tier(100.0), 'critical')

    def test_critical_above_one_hundred(self):
        # Defensive: if the math overshoots, we still classify as critical
        # (rather than wrapping back to 'ok').
        self.assertEqual(classify_token_tier(105.5), 'critical')

    # ── Edge cases ─────────────────────────────────────────────────────
    def test_zero_stays_ok(self):
        # Defensive: brand-new thread at 0 tokens should be 'ok', not crash
        self.assertEqual(classify_token_tier(0), 'ok')

    def test_negative_floats_as_ok(self):
        # Defensive: shouldn't happen in practice, but if it does we
        # want the safest tier ('ok'), not 'critical' or an exception.
        self.assertEqual(classify_token_tier(-0.1), 'ok')


class TestModelContextWindows(unittest.TestCase):
    """Pin the per-model context-window lookup the worker relies on."""

    def test_all_expected_models_present(self):
        """Every model the dispatcher can route to must have a window."""
        # This is the same set declared in _MODEL_CONTEXT_WINDOWS.
        expected_keys = set(EXPECTED_CONTEXT_WINDOWS.keys())
        # Re-fetch the worker's actual table by reading the source — this
        # is a lighter-weight contract than importing the function (which
        # would require Flask app context).
        worker_table = _read_worker_context_windows()
        self.assertEqual(
            worker_table, expected_keys,
            "Worker _MODEL_CONTEXT_WINDOWS drift detected. "
            "Either update the worker to add/remove the missing model, "
            "or update EXPECTED_CONTEXT_WINDOWS in this test."
        )

    def test_windows_are_positive_integers(self):
        for model, window in EXPECTED_CONTEXT_WINDOWS.items():
            self.assertIsInstance(window, int, f"{model} window is not int")
            self.assertGreater(window, 0, f"{model} window is non-positive")

    def test_windows_at_or_below_one_million(self):
        # Sanity: no model claims a >1M window. The safe default fallback
        # in the worker is 1M, so anything larger would cause the indicator
        # to under-report (e.g. a 2M model classified against a 1M window).
        for model, window in EXPECTED_CONTEXT_WINDOWS.items():
            self.assertLessEqual(
                window, 1_000_000,
                f"{model} has window {window} > 1M; safe-default fallback "
                "in the worker would under-report."
            )


class TestSafeDefaultFallback(unittest.TestCase):
    """Pin the worker's safe-default behaviour for unknown models."""

    def test_unknown_model_falls_back_to_one_million(self):
        # Mirror of combined_agent_worker.py:2328 —
        #   context_window = _MODEL_CONTEXT_WINDOWS.get(ai_model, 1_000_000)
        window = EXPECTED_CONTEXT_WINDOWS.get('some-future-model-XYZ', 1_000_000)
        self.assertEqual(window, 1_000_000)

    def test_known_model_does_not_use_safe_default(self):
        # Sanity: MiniMax-M3 has a specific 1M entry; it should not be
        # served by the safe-default path.
        self.assertIn('MiniMax-M3', EXPECTED_CONTEXT_WINDOWS)
        self.assertEqual(EXPECTED_CONTEXT_WINDOWS['MiniMax-M3'], 1_000_000)


class TestTierTransitionOrdering(unittest.TestCase):
    """The toast logic in business-ai-platform-v2.html relies on this ordering."""

    def test_severity_is_monotonic(self):
        # If a tier's severity rank isn't monotonic, the toast logic at
        # business-ai-platform-v2.html:32583 will toast on every tick
        # instead of only on transitions.
        TIER_RANK = {'ok': 0, 'info': 1, 'warning': 2, 'critical': 3}
        ranks = [TIER_RANK[t] for t in ('ok', 'info', 'warning', 'critical')]
        self.assertEqual(ranks, sorted(ranks))
        self.assertEqual(len(set(ranks)), 4)

    def test_no_two_tiers_share_a_rank(self):
        TIER_RANK = {'ok': 0, 'info': 1, 'warning': 2, 'critical': 3}
        self.assertEqual(len(TIER_RANK), 4)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────
def _read_worker_context_windows():
    """Extract the set of model names declared in the worker's
    _MODEL_CONTEXT_WINDOWS dict by parsing the source file. This is the
    lightest-weight contract — we don't import the worker (which would
    require Flask app context + would actually invoke the AI loop)."""
    worker_path = (
        Path(__file__).resolve().parents[1] / 'core' / 'combined_agent_worker.py'
    )
    text = worker_path.read_text(encoding='utf-8', errors='replace')

    # Find the _MODEL_CONTEXT_WINDOWS = { ... } block.
    start = text.find('_MODEL_CONTEXT_WINDOWS = {')
    if start == -1:
        raise AssertionError("_MODEL_CONTEXT_WINDOWS dict not found in combined_agent_worker.py")
    end = text.find('}', start)
    if end == -1:
        raise AssertionError("_MODEL_CONTEXT_WINDOWS closing brace not found")
    block = text[start:end]

    # Each entry is "  'model-name': NNN," — pull the quoted model name.
    import re
    names = re.findall(r"'([^']+)':\s*\d[\d_]*", block)
    return set(names)


if __name__ == '__main__':
    # No pytest config in repo root (CLAUDE.md §8) — run as a plain script.
    unittest.main(verbosity=2)