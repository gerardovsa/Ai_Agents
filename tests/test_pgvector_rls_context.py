"""
REGRESSION TEST: pgvector tools must satisfy the org_id RLS policy
=================================================================

REGRESSION: 2026-06-17 — Document upload to pgvector failed with:
    "Query execution failed: new row violates row-level security policy
     for table 'org_vector_documents'"

ROOT CAUSE:
    Migration 044 adds RLS policies that check
    `current_setting('app.current_org_id')` against the inserted/queried
    `org_id`.  `pgvector_upsert_vectors` (and the other pgvector_* tools)
    were calling `execute_query()` for the DML/DQL directly, WITHOUT
    setting `app.current_org_id` first.

    A `_run_in_org_context()` helper existed but was:
      (a) never called from the upsert path, AND
      (b) broken: it ran the SET and the DML as two separate
          `execute_query()` calls, which on a pooled connection land on
          DIFFERENT connections — so the SET was discarded before the
          INSERT ran.  The author's comment claiming "no session leakage
          between requests" was self-defeating: if the SET didn't leak,
          it also couldn't reach the INSERT.

FIX:
    `_run_in_org_context()` now combines the SET, the DML, and a trailing
    RESET into a SINGLE multi-statement `execute_query()` call — so all
    three statements share one pooled connection, the GUC is set
    immediately before the DML, and the RESET prevents cross-request
    leakage.  All four pgvector data tools (upsert, query, delete, list,
    stats) now route through the helper.

THIS TEST:
    Stubs `database_utils.execute_query` and asserts that every pgvector
    DML/DQL call goes through `_run_in_org_context` — i.e. the SQL handed
    to `execute_query` BEGINS with `SET app.current_org_id = '...'` and
    ENDS with `RESET app.current_org_id;`.  No DB or model load needed.

RUN:
    python tests/test_pgvector_rls_context.py
"""

import sys
import uuid as _uuid
from pathlib import Path
from unittest.mock import patch

# Repo root on path so we can import the tool module directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.implementations.pgvector import pgvector_tools
from AI_infrastructure.shared import database_utils


PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    status = PASS if condition else FAIL
    print(f"  {status}  {label}{(' — ' + detail) if detail else ''}")
    if not condition:
        failures.append(f"{label} {detail}".strip())


def _capture_executor():
    """Build a fake execute_query that records (sql, params, fetch_mode) tuples."""
    captured: list[tuple] = []

    def fake_execute_query(sql, params=(), fetch_mode=None):
        captured.append((str(sql), tuple(params) if params else (), fetch_mode))
        # SELECT-style responses return a row; DELETE/INSERT return None
        if fetch_mode == "one":
            return {"doc_count": 0, "vector_count": 0}
        if fetch_mode == "all":
            return []
        return None

    return fake_execute_query, captured


def _sql_has_rls_wrap(sql: str, org_id: int) -> bool:
    """
    The fixed _run_in_org_context combines:
        SET app.current_org_id = '<org_id>';
        <original SQL>;
        RESET app.current_org_id;
    into a single multi-statement string.  Assert both the SET and the
    RESET are present, and the org id matches.
    """
    has_set    = f"SET app.current_org_id = '{int(org_id)}';" in sql
    has_reset  = "RESET app.current_org_id;" in sql
    return has_set and has_reset


# ---------------------------------------------------------------------------
# Test 1: pgvector_upsert_vectors
# ---------------------------------------------------------------------------
def test_upsert_wraps_insert_with_rls_context() -> None:
    print("\n[1] pgvector_upsert_vectors wraps every INSERT in SET+RESET")
    fake, captured = _capture_executor()

    vectors = [
        {
            "id": str(_uuid.uuid4()),
            "values": [0.1] * 768,
            "metadata": {
                "document_id": "doc_abc123",
                "filename": "test.txt",
                "chunk_index": 0,
                "total_chunks": 1,
                "text": "hello world",
            },
        },
        {
            "id": str(_uuid.uuid4()),
            "values": [0.2] * 768,
            "metadata": {
                "document_id": "doc_abc123",
                "filename": "test.txt",
                "chunk_index": 1,
                "total_chunks": 2,
                "text": "second chunk",
            },
        },
    ]

    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42):
        result = pgvector_tools.pgvector_upsert_vectors(vectors, _user_id=7)

    check("upsert succeeded", result.get("success") is True,
          detail=f"got: {result}")
    check("two execute_query calls (one per vector)",
          len(captured) == 2, detail=f"got {len(captured)}")

    for i, (sql, params, fetch_mode) in enumerate(captured):
        check(f"call #{i+1} SQL wraps INSERT with SET+RESET for org 42",
              _sql_has_rls_wrap(sql, 42),
              detail=f"sql starts: {sql[:80]!r}")
        check(f"call #{i+1} uses fetch_mode=None (DML)",
              fetch_mode is None, detail=f"got: {fetch_mode}")
        check(f"call #{i+1} params carry the org_id",
              42 in params, detail=f"params: {params[:5]!r}")


# ---------------------------------------------------------------------------
# Test 2: pgvector_query_vectors
# ---------------------------------------------------------------------------
def test_query_wraps_select_with_rls_context() -> None:
    print("\n[2] pgvector_query_vectors wraps the SELECT in SET+RESET")
    fake, captured = _capture_executor()

    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42), \
         patch.object(pgvector_tools, "_generate_embedding",
                      return_value=[0.1] * 768):
        result = pgvector_tools.pgvector_query_vectors(
            query_text="hello", top_k=3, _user_id=7
        )

    check("query succeeded", result.get("success") is True, detail=f"got: {result}")
    check("exactly one execute_query call", len(captured) == 1,
          detail=f"got {len(captured)}")
    sql = captured[0][0]
    check("SQL wrapped in SET+RESET for org 42",
          _sql_has_rls_wrap(sql, 42), detail=f"sql starts: {sql[:80]!r}")


# ---------------------------------------------------------------------------
# Test 3: pgvector_delete_vectors
# ---------------------------------------------------------------------------
def test_delete_wraps_delete_with_rls_context() -> None:
    print("\n[3] pgvector_delete_vectors wraps the DELETE in SET+RESET")
    fake, captured = _capture_executor()

    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42):
        result = pgvector_tools.pgvector_delete_vectors(
            document_id="doc_abc123", _user_id=7
        )

    check("delete succeeded", result.get("success") is True, detail=f"got: {result}")
    check("exactly one execute_query call", len(captured) == 1,
          detail=f"got {len(captured)}")
    sql = captured[0][0]
    check("SQL wrapped in SET+RESET for org 42",
          _sql_has_rls_wrap(sql, 42), detail=f"sql starts: {sql[:80]!r}")
    check("fetch_mode=None (DML)",
          captured[0][2] is None, detail=f"got: {captured[0][2]}")


# ---------------------------------------------------------------------------
# Test 4: pgvector_list_documents
# ---------------------------------------------------------------------------
def test_list_wraps_select_with_rls_context() -> None:
    print("\n[4] pgvector_list_documents wraps the SELECT in SET+RESET")
    fake, captured = _capture_executor()

    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42):
        result = pgvector_tools.pgvector_list_documents(_user_id=7)

    check("list succeeded", result.get("success") is True, detail=f"got: {result}")
    check("exactly one execute_query call", len(captured) == 1,
          detail=f"got {len(captured)}")
    sql = captured[0][0]
    check("SQL wrapped in SET+RESET for org 42",
          _sql_has_rls_wrap(sql, 42), detail=f"sql starts: {sql[:80]!r}")


# ---------------------------------------------------------------------------
# Test 5: pgvector_describe_stats
# ---------------------------------------------------------------------------
def test_stats_wraps_select_with_rls_context() -> None:
    print("\n[5] pgvector_describe_stats wraps the SELECT in SET+RESET")
    fake, captured = _capture_executor()

    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42):
        result = pgvector_tools.pgvector_describe_stats(_user_id=7)

    check("describe succeeded", result.get("success") is True,
          detail=f"got: {result}")
    check("exactly one execute_query call", len(captured) == 1,
          detail=f"got {len(captured)}")
    sql = captured[0][0]
    check("SQL wrapped in SET+RESET for org 42",
          _sql_has_rls_wrap(sql, 42), detail=f"sql starts: {sql[:80]!r}")


# ---------------------------------------------------------------------------
# Test 6: org_id is interpolated as a quoted integer (defense in depth)
# ---------------------------------------------------------------------------
def test_org_id_is_interpolated_as_integer() -> None:
    """
    _get_org_id() always returns an integer (DB column organisations.id
    is INTEGER).  The fix passes it through int() before formatting, so
    any future caller that hands us a different numeric type (numpy int,
    Decimal, string-of-digits) still produces a safe SQL string.
    """
    print("\n[6] org_id is integer-cast before being interpolated into SQL")
    fake, captured = _capture_executor()

    # Realistic input — a real integer from organisations.id
    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=12345):
        result = pgvector_tools.pgvector_list_documents(_user_id=7)

    check("list succeeded", result.get("success") is True,
          detail=f"got: {result}")
    sql = captured[0][0]
    check("SET line has the org id as a quoted integer",
          "SET app.current_org_id = '12345';" in sql,
          detail=f"sql starts: {sql[:80]!r}")
    check("no Python-repr leakage (e.g. 'np.int64(12345)')",
          "np.int64" not in sql and "Decimal" not in sql,
          detail=f"sql: {sql[:120]!r}")


# ---------------------------------------------------------------------------
# Test 7: regression — the broken pre-fix pattern would NOT pass this
# ---------------------------------------------------------------------------
def test_set_and_dml_are_in_a_single_execute_query_call() -> None:
    """
    The pre-fix _run_in_org_context did:
        execute_query("SET app.current_org_id = '42'")
        execute_query("INSERT INTO ...")
    as TWO separate calls.  That meant the SET was on one pooled
    connection and the INSERT on another — so the INSERT was rejected
    by RLS.  After the fix, SET+INSERT+RESET are in ONE call.
    """
    print("\n[7] SET, DML, and RESET are combined in a single execute_query call")
    fake, captured = _capture_executor()

    with patch.object(database_utils, "execute_query", side_effect=fake), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42):
        pgvector_tools.pgvector_list_documents(_user_id=7)

    check("only ONE execute_query call (not two)",
          len(captured) == 1, detail=f"got {len(captured)}")
    sql = captured[0][0]
    # All three statements must be in the same string.
    # Note: searching for the bare substring "SET app.current_org_id"
    # also matches inside "RESET app.current_org_id", so we use the
    # assignment form to count only the genuine SET statements.
    set_assignment = f"SET app.current_org_id = '"
    check("exactly one real SET (assignment form)",
          sql.count(set_assignment) == 1,
          detail=f"count={sql.count(set_assignment)}")
    check("DML present in same string", "org_vector_documents" in sql)
    check("RESET present in same string", "RESET app.current_org_id;" in sql)
    # And the SET must come BEFORE the DML in the same string
    check("SET precedes DML in the combined SQL",
          sql.find(set_assignment) < sql.find("org_vector_documents")
          < sql.find("RESET app.current_org_id;"))


if __name__ == "__main__":
    print("=" * 78)
    print("  REGRESSION TEST: pgvector tools satisfy the org_id RLS policy")
    print("=" * 78)

    test_upsert_wraps_insert_with_rls_context()
    test_query_wraps_select_with_rls_context()
    test_delete_wraps_delete_with_rls_context()
    test_list_wraps_select_with_rls_context()
    test_stats_wraps_select_with_rls_context()
    test_org_id_is_interpolated_as_integer()
    test_set_and_dml_are_in_a_single_execute_query_call()

    print("\n" + "=" * 78)
    if failures:
        print(f"  RESULT: {FAIL}  {len(failures)} failure(s)")
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)
    else:
        print(f"  RESULT: {PASS}  all checks passed")
        sys.exit(0)
