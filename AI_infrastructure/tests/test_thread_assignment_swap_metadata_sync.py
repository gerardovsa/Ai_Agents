"""Regression tests for thread-assignment swap metadata sync.

Background
----------
``enforce_thread_assignment_rules`` in
``AI_infrastructure/routes/thread_assignment_routes.py`` writes each
thread's location into TWO places:

1. ``sessions.threads.location`` (current single source of truth)
2. ``ai_infrastructure.users.metadata->>'thread_assignments'`` (legacy map)

RULE 1 of the assignment algorithm — used to compute
``previous_location`` for a swapping thread — still iterates the legacy
map, not ``sessions.threads``. The displaced-thread branch of the swap
path updated ``sessions.threads.location`` but *not* the legacy map, so
the displaced thread effectively disappeared from RULE 1's view.

Reproduction (T1 in agent-19, T2 in agent-20 initially, fully consistent
metadata ``{"agent-19": "T1", "agent-20": "T2"}``):

  Swap 1 — drag T2 onto agent-19:
    RULE 1 finds T2 → previous_location="agent-20"
    RULE 2 finds T1 in target → displaced_thread=T1
    Assign T2 to agent-19; move T1 to agent-20.
    ❌ OLD: metadata becomes ``{"agent-19": "T2"}`` — T1 is GONE.
    ✅ NEW: metadata becomes ``{"agent-19": "T2", "agent-20": "T1"}``.

  Swap 2 — drag T1 (now in agent-20) onto agent-19:
    ❌ OLD: RULE 1 cannot find T1 in metadata → previous_location=None
            → displaced_new_location forced to ``"unassigned"`` instead
            of ``"agent-20"``. UI reverts the source column to empty.
    ✅ NEW: RULE 1 finds T1 in metadata → previous_location="agent-20"
            → displaced_new_location="agent-20". Source column receives
            the displaced thread on second swap.

These tests pin the new contract.

NOTE — these tests stub the DB behind ``get_db_connection`` and
``convert_sql_placeholders`` so they run offline. They do not exercise
``cursor.fetchone()`` returning a dict-like row from psycopg2; the fake
cursor returns a plain ``dict`` because the production code uses
``row['metadata']`` subscripting which works for both. ``convert_sql_placeholders``
is patched to a pass-through that ignores the placeholder dialect (production
converts ``%s`` to whatever the active driver wants; tests don't care).
"""

import importlib
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import routes.thread_assignment_routes as tar  # noqa: E402

# ``convert_sql_placeholders`` normalises dialect-specific placeholders
# (e.g. ``%s`` → ``?`` for SQLite). The fake connection doesn't speak
# either dialect; we just want the SQL and params to round-trip.
IDENTITY_CONVERT = lambda sql, params: (sql, params)


class _FakeRow(dict):
    """Dict that also supports subscript access — psycopg2 row contract."""


class _FakeCursor:
    """Records ``execute`` calls; ``fetchone`` returns the last metadata
    that was written via ``UPDATE ai_infrastructure.users SET metadata``.

    The function we're testing writes metadata twice on the swap path:
      - once in the RULE 3 block (line 178)
      - once in the displaced-mirror block added by this fix (line 226)
    The fake cursor serves SELECTs from the latest ``UPDATE`` so a second
    call to ``enforce_thread_assignment_rules`` sees the post-swap state
    — matching real production behaviour.
    """

    USER_METADATA_SELECT = (
        "SELECT metadata FROM ai_infrastructure.users WHERE id = %s"
    )
    USER_EXISTS_SELECT = "SELECT id FROM ai_infrastructure.users WHERE id = %s"

    def __init__(self, initial_metadata):
        self.executed = []  # list of (sql, params_or_None)
        self._user_metadata_writes = []  # history of metadata strings written
        self._initial_metadata = initial_metadata
        self._last_user_row = None
        self._users_table_exists = True  # user row considered pre-existing

    # psycopg2 cursor API we exercise
    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        if "UPDATE ai_infrastructure.users" in sql and "metadata" in sql:
            # Production passes json.dumps(metadata) as the first param.
            self._user_metadata_writes.append(params[0])
            self._last_user_row = _FakeRow({"metadata": params[0]})

    def fetchone(self):
        # Order matters: production code does user-exists check FIRST,
        # THEN metadata SELECT. Match that call order.
        last_sql, _ = self.executed[-1]
        if self.USER_EXISTS_SELECT in last_sql:
            # Pretend the user always exists for these tests.
            return _FakeRow({"id": 1})
        if self.USER_METADATA_SELECT in last_sql:
            if self._last_user_row is not None:
                # Re-emit the latest write so the next call sees post-swap metadata.
                return self._last_user_row
            return _FakeRow({"metadata": json.dumps(self._initial_metadata)})
        return None

    def close(self):
        pass


class _FakeConn:
    def __init__(self, cursor):
        self._cursor = cursor
        self.commits = 0

    def cursor(self):
        return self._cursor

    def commit(self):
        self.commits += 1

    # Production uses ``with get_db_connection() as conn:`` — the
    # context-manager protocol must work for real.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class SwapMetadataSyncTests(unittest.TestCase):
    """The fix must keep the legacy metadata map in sync during a swap so
    that the *next* swap can locate the displaced thread's previous slot.
    """

    USER_ID = 42

    def setUp(self):
        self._convert_patch = mock.patch.object(
            tar, 'convert_sql_placeholders', side_effect=IDENTITY_CONVERT
        )
        self._convert_patch.start()
        self.addCleanup(self._convert_patch.stop)

    def _run_swap(self, initial_metadata, session_id, new_location):
        """Invoke ``enforce_thread_assignment_rules`` with the given starting
        state and return ``(result, cursor)``.
        """
        cursor = _FakeCursor(initial_metadata)
        conn = _FakeConn(cursor)
        # The user-exists SELECT needs to find something so the function
        # doesn't try to INSERT a new user row.
        with mock.patch.object(tar, 'get_db_connection', return_value=conn):
            result = tar.enforce_thread_assignment_rules(
                self.USER_ID, session_id, new_location, swap=True
            )
        return result, cursor

    # ------------------------------------------------------------------
    # The headline regression: second swap must recover previous_location.
    # ------------------------------------------------------------------
    def test_second_swap_recovers_previous_location_after_fix(self):
        """Two consecutive swaps with the SAME pair of threads must both
        return ``displaced_new_location=<source location>`` on the second
        call. Pre-fix the second call returned ``"unassigned"`` because the
        metadata map lost track of T1 after the first swap.
        """
        initial = {
            "thread_assignments": {
                "agent-19": "T1",
                "agent-20": "T2",
            }
        }

        # First swap: drag T2 onto agent-19 (which holds T1).
        first_result, first_cursor = self._run_swap(
            initial, session_id="T2", new_location="agent-19"
        )

        # Post-conditions for swap 1.
        self.assertEqual(first_result["displaced_thread"], "T1")
        self.assertEqual(first_result["displaced_new_location"], "agent-20")
        # The final write to users.metadata must mirror the displaced thread.
        final_metadata_first = json.loads(first_cursor._user_metadata_writes[-1])
        self.assertEqual(
            final_metadata_first["thread_assignments"]["agent-20"], "T1",
            "After swap 1, T1 must be tracked in metadata so swap 2 can find it"
        )

        # Second swap: drag T1 onto agent-19 (which now holds T2).
        second_result, _ = self._run_swap(
            final_metadata_first,
            session_id="T1",
            new_location="agent-19",
        )

        # Post-conditions for swap 2 — the actual bug regression.
        self.assertEqual(
            second_result["previous_location"], "agent-20",
            "Without the fix, previous_location is None and the displaced "
            "thread ends up in 'unassigned'. The fix mirrors displaced "
            "threads into metadata so RULE 1 can find them."
        )
        self.assertEqual(second_result["displaced_thread"], "T2")
        self.assertEqual(
            second_result["displaced_new_location"], "agent-20",
            "T2 must swap back to agent-20 — not be stranded in 'unassigned'"
        )

    # ------------------------------------------------------------------
    # Pin the unit-level guarantee: the displaced-mirror UPDATE runs
    # only when displaced_new_location != 'unassigned'.
    # ------------------------------------------------------------------
    def test_displaced_thread_to_unassigned_does_not_touch_metadata(self):
        """When the displaced thread falls back to 'unassigned' (because
        previous_location was missing), we must NOT write a stale entry
        into metadata.thread_assignments['unassigned'].

        Scenario:
            - T1 has no metadata entry (simulates a thread wiped by a
              previous buggy swap).
            - T2 sits in agent-19.
            - T3 sits in agent-20.

        Drag T1 onto agent-19:
            - RULE 1: T1 not in metadata → previous_location=None.
            - RULE 2: agent-19 has T2 → displaced_thread=T2.
            - displaced_new_location = "unassigned" (swap=True but
              previous_location missing).
        """
        initial = {
            "thread_assignments": {
                "agent-19": "T2",
                "agent-20": "T3",
            }
        }

        result, cursor = self._run_swap(
            initial, session_id="T1", new_location="agent-19"
        )

        self.assertIsNone(result["previous_location"])
        self.assertEqual(result["displaced_thread"], "T2")
        self.assertEqual(result["displaced_new_location"], "unassigned")

        # Inspect the LAST metadata write. It must NOT contain
        # 'thread_assignments'['unassigned'] == 'T2'.
        last_metadata = json.loads(cursor._user_metadata_writes[-1])
        self.assertNotIn(
            "unassigned", last_metadata.get("thread_assignments", {}),
            "Guard: 'unassigned' must never appear as a key in "
            "metadata.thread_assignments (unassigned is implicit)."
        )

    # ------------------------------------------------------------------
    # Sanity: the displaced-mirror UPDATE uses the production schema
    # ('ai_infrastructure.users') so the fix doesn't silently miss if
    # the table is renamed later.
    # ------------------------------------------------------------------
    def test_fix_emits_metadata_update_against_ai_infrastructure_users(self):
        """The displaced-mirror UPDATE must target the same table the rest
        of the function writes to. Otherwise swap 1 looks fine but RULE 1
        on swap 2 reads a stale metadata snapshot.
        """
        initial = {
            "thread_assignments": {"agent-19": "T1", "agent-20": "T2"}
        }
        _, cursor = self._run_swap(
            initial, session_id="T2", new_location="agent-19"
        )

        updates_to_users = [
            sql for (sql, _) in cursor.executed
            if "UPDATE ai_infrastructure.users" in sql
        ]
        # Two such UPDATEs are expected: RULE 3 write + displaced-mirror.
        self.assertEqual(
            len(updates_to_users), 2,
            "Expected both the RULE 3 write and the displaced-mirror write "
            "against ai_infrastructure.users. Found:\n"
            + "\n".join(updates_to_users)
        )


if __name__ == "__main__":
    unittest.main()
