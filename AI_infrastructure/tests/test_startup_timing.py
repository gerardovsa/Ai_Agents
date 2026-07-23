"""Test: Startup Phase Timing Helper

Verifies the AI_infrastructure/shared/startup_timing.py helper:
1. begin()/end() records monotonically increasing total_ms
2. snapshot() returns the documented JSON shape (ok, pid, phases, summary)
3. summary() correctly identifies the slowest phase and under_5s_target
4. ASCII coercion strips non-ASCII bytes from notes
5. STARTUP_TIMING=0 disables all output (records stay empty)
6. _reset_for_tests() returns the helper to a clean state

Run:
    cd AI_infrastructure
    python tests/test_startup_timing.py
"""
import json
import os
import sys
import unittest

# Allow `python tests/test_startup_timing.py` from the AI_infrastructure
# directory by adding the project root to sys.path.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from AI_infrastructure.shared import startup_timing as st  # noqa: E402


class TestStartupTiming(unittest.TestCase):

    def setUp(self):
        # Each test starts with a fresh module-level state.
        st._reset_for_tests()
        # Make sure STARTUP_TIMING is enabled regardless of shell env.
        os.environ.pop("STARTUP_TIMING", None)
        os.environ.pop("STARTUP_TIMING_QUIET", None)

    def tearDown(self):
        st._reset_for_tests()

    # ------------------------------------------------------------------ core
    def test_begin_end_records_monotonic_totals(self):
        st.begin("phase_a", note="first")
        st.end("phase_a", note="first done")
        st.begin("phase_b", note="second")
        st.end("phase_b", note="second done")

        snap = st.snapshot()
        self.assertTrue(snap["ok"])
        self.assertEqual(len(snap["phases"]), 2)
        totals = [r["total_ms"] for r in snap["phases"]]
        self.assertLessEqual(totals[0], totals[1],
                             "total_ms must be non-decreasing across phases")

    def test_snapshot_shape(self):
        st.begin("p1")
        st.end("p1")
        snap = st.snapshot()
        self.assertIn("ok", snap)
        self.assertIn("pid", snap)
        self.assertIn("boot_total_ms", snap)
        self.assertIn("phases", snap)
        self.assertIn("summary", snap)
        self.assertIn("render_mode", snap)
        self.assertIsInstance(snap["phases"], list)
        # Each record has the documented fields.
        r = snap["phases"][0]
        for k in ("id", "status", "dt_ms", "total_ms", "wall", "note"):
            self.assertIn(k, r)

    def test_summary_under_5s_target(self):
        st.begin("p1")
        st.end("p1")
        snap = st.snapshot()
        s = snap["summary"]
        self.assertIn("slowest_phase", s)
        self.assertIn("under_5s_target", s)
        self.assertIn("phases_over_1000ms", s)
        # Synthetic single tiny phase is well under 5s.
        self.assertTrue(s["under_5s_target"])
        self.assertEqual(s["phases_over_1000ms"], 0)
        self.assertEqual(s["slowest_phase"]["id"], "p1")

    def test_ascii_coercion_on_note(self):
        # Non-ASCII note must be sanitized. encode("ascii", "replace")
        # substitutes one "?" per non-ASCII *byte*, so the multi-byte "→"
        # arrow (3 bytes in UTF-8) becomes three "?" chars. The check is:
        # 1) the result is pure ASCII, and 2) the ASCII fragment is preserved.
        st.begin("emoji_phase", note="ok -> ready")  # arrow kept literal for assert
        # Now try with an actual non-ASCII arrow to confirm sanitization.
        st.end("emoji_phase", note="ok → ready")  # noqa: non-ASCII intentional
        snap = st.snapshot()
        note = snap["phases"][0]["note"]
        # Every character is now ASCII.
        self.assertTrue(all(ord(c) < 128 for c in note),
                        f"non-ASCII survived sanitization: {note!r}")
        # The "ok " prefix and " ready" suffix are preserved.
        self.assertTrue(note.startswith("ok "))
        self.assertTrue(note.endswith(" ready"))
        # The arrow is replaced by at least one '?'.
        self.assertIn("?", note)

    def test_note_truncation(self):
        long_note = "x" * 500
        st.begin("long", note=long_note)
        st.end("long", note=long_note)
        snap = st.snapshot()
        self.assertLessEqual(len(snap["phases"][0]["note"]), 80)

    def test_disable_via_env(self):
        os.environ["STARTUP_TIMING"] = "0"
        st.begin("should_not_record")
        st.end("should_not_record", note="invisible")
        snap = st.snapshot()
        # No records because the helper short-circuits.
        self.assertEqual(len(snap["phases"]), 0)
        del os.environ["STARTUP_TIMING"]

    def test_quiet_does_not_disable_records(self):
        # STARTUP_TIMING_QUIET=1 only silences stdout; records still populate.
        os.environ["STARTUP_TIMING_QUIET"] = "1"
        st.begin("quiet_phase")
        st.end("quiet_phase")
        snap = st.snapshot()
        self.assertEqual(len(snap["phases"]), 1)
        del os.environ["STARTUP_TIMING_QUIET"]

    def test_end_without_begin_falls_back_to_anchor(self):
        # Defensive: calling end() for a phase_id never begin()'d should
        # still record something, measured against _BOOT_T0.
        st.end("orphan")
        snap = st.snapshot()
        self.assertEqual(len(snap["phases"]), 1)
        self.assertGreaterEqual(snap["phases"][0]["total_ms"], 0.0)

    def test_render_text_contains_phases_and_total(self):
        st.begin("alpha")
        st.end("alpha")
        st.begin("beta")
        st.end("beta")
        text = st.render_text()
        self.assertIn("alpha", text)
        self.assertIn("beta", text)
        self.assertIn("TOTAL BOOT", text)
        self.assertIn("UNDER_5S_TARGET", text)

    def test_render_json_is_valid_json(self):
        st.begin("gamma")
        st.end("gamma")
        text = st.render_json()
        parsed = json.loads(text)
        self.assertTrue(parsed["ok"])
        self.assertEqual(len(parsed["phases"]), 1)


def main():
    print("=" * 70)
    print("STARTUP TIMING HELPER — UNIT TESTS")
    print("=" * 70)
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
