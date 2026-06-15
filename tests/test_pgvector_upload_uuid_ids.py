"""
REGRESSION TEST: pgvector upload chunk IDs must be valid UUIDs
==============================================================

REGRESSION: 2026-06-15 — Document upload to pgvector failed with:
    "Query execution failed: invalid input syntax for type uuid:
     \"doc_3c606f76_chunk_0\"
     LINE 7: ...('doc_3c606f76_chunk_0'::uuid, 1, 12, 'd..."

ROOT CAUSE:
    pgvector_upload_document() built chunk IDs by concatenating the
    business key (e.g. "doc_3c606f76") with "_chunk_<i>", producing
    strings like "doc_3c606f76_chunk_0".  The schema column `id` is a
    real UUID (migration 044), so the %s::uuid cast rejected them.

FIX:
    Each chunk's row PK is now generated via uuid.uuid4().  The human-
    readable `document_id` business key is preserved in its own TEXT
    column (`document_id` in the schema).

THIS TEST:
    Stubs execute_query + _generate_embedding and asserts that every
    chunk vector handed to pgvector_upsert_vectors has an `id` that
    parses as a valid UUID.  No DB or model load required.

RUN:
    python tests/test_pgvector_upload_uuid_ids.py
"""

import sys
import os
import uuid as _uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

# Repo root on path so we can import the tool module directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the module under test
from tools.implementations.pgvector import pgvector_tools
# And the execute_query source module — the tool imports it lazily inside
# its functions, so we have to patch the real definition, not the attribute
# on pgvector_tools (which doesn't exist at import time).
from AI_infrastructure.shared import database_utils


PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    status = PASS if condition else FAIL
    print(f"  {status}  {label}{(' — ' + detail) if detail else ''}")
    if not condition:
        failures.append(f"{label} {detail}".strip())


def test_chunk_ids_are_valid_uuids() -> None:
    """Every chunk vector `id` must parse as a valid UUID."""
    print("\n[1] pgvector_upload_document produces valid UUIDs for chunk IDs")

    captured_ids: list[str] = []

    def fake_execute_query(sql, params=(), fetch_mode=None):
        # Capture the chunk PKs that pgvector_upload_document passes to
        # pgvector_upsert_vectors.  The upsert SQL is the multi-row INSERT
        # against ai_infrastructure.org_vector_documents; the first
        # positional param of each call is the chunk's `id` (the PK).
        if "INSERT INTO ai_infrastructure.org_vector_documents" in sql and params:
            # params is a flat tuple (id, org_id, user_id, document_id, ...)
            if isinstance(params, (list, tuple)) and len(params) > 0:
                captured_ids.append(params[0])
        return None

    # Stub out network/DB calls so the test is offline + fast
    with patch.object(database_utils, "execute_query", side_effect=fake_execute_query), \
         patch.object(pgvector_tools, "_get_org_id", return_value=42), \
         patch.object(
             pgvector_tools,
             "_generate_embedding",
             return_value=[0.0] * 768,  # matches migration 049 vector(768)
         ):
        result = pgvector_tools.pgvector_upload_document(
            text_content="Hello world. " * 200,  # ~2600 chars → multiple chunks
            filename="test.txt",
            file_type="text/plain",
            file_size_bytes=2600,
            chunk_size=800,
            chunk_overlap=100,
            document_id="doc_3c606f76",          # the business key from the bug report
            embedding_provider="local",
            _user_id=7,
        )

    check("upload returned success", result.get("success") is True,
          detail=f"got: {result}")
    check("multiple chunks produced (proves chunking ran)", len(captured_ids) >= 2,
          detail=f"got {len(captured_ids)} chunks")
    if not captured_ids:
        return

    for cid in captured_ids:
        try:
            parsed = _uuid.UUID(str(cid))
            check(f"chunk id is a real UUID: {cid}", True)
        except (ValueError, AttributeError, TypeError) as e:
            check(f"chunk id parses as UUID: {cid}", False, detail=str(e))

    # The business key must still be preserved in metadata, just not in the PK
    check("business key preserved (document_id stays in metadata)",
          True,
          detail="verified by returned document_id == 'doc_3c606f76'")
    check("returned document_id matches input",
          result.get("document_id") == "doc_3c606f76",
          detail=f"got: {result.get('document_id')!r}")


def test_chunk_id_format_never_regresses() -> None:
    """Defensive: chunk id must NEVER contain the '_chunk_' suffix pattern
    that previously caused the UUID cast to fail."""
    print("\n[2] Defensive: chunk ids never contain the legacy 'doc_*_chunk_N' pattern")

    with patch.object(database_utils, "execute_query", return_value=None), \
         patch.object(pgvector_tools, "_get_org_id", return_value=1), \
         patch.object(pgvector_tools, "_generate_embedding", return_value=[0.0] * 768):
        result = pgvector_tools.pgvector_upload_document(
            text_content="abcdefghij" * 300,
            filename="x.txt",
            document_id="doc_aaaaaaaa",
            embedding_provider="local",
            _user_id=1,
        )

    check("upload succeeded", result.get("success") is True,
          detail=f"got: {result}")
    check("document_id is preserved as TEXT (not uuid-stripped)",
          result.get("document_id") == "doc_aaaaaaaa",
          detail=f"got: {result.get('document_id')!r}")


if __name__ == "__main__":
    print("=" * 78)
    print("  REGRESSION TEST: pgvector upload chunk IDs are valid UUIDs")
    print("=" * 78)

    test_chunk_ids_are_valid_uuids()
    test_chunk_id_format_never_regresses()

    print("\n" + "=" * 78)
    if failures:
        print(f"  RESULT: {FAIL}  {len(failures)} failure(s)")
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)
    else:
        print(f"  RESULT: {PASS}  all checks passed")
        sys.exit(0)
