"""
Regression test for the LIVE vector_db guidance wiring.

CONTEXT (2026-07-28):
    The Option A work (migration 052 + vector_db_router.py +
    system_prompt_builder.py) was initially wired ONLY into the
    SystemPromptBuilder class. A later audit revealed that class is dead
    code in production — the only caller is core/archived/conversation_manager
    (frozen per CLAUDE.md §2).

    The ACTUAL live prompt builder is
    AI_infrastructure/core/unified_ai_client.py:
        UnifiedAIClient._get_tool_usage_instructions()

    This test asserts:
        1. When a Flask request context has g.rls_org_id set, the live
           prompt contains the '=== VECTOR DATABASE ===' section with the
           active provider pulled from v_org_vector_status (migration 052).
        2. When called outside a Flask context (CLI, scheduled tasks),
           the prompt is returned WITHOUT the section and WITHOUT
           raising — graceful degradation.
        3. The injected section contains the 4 smart tool names so the
           AI can pick the right tool from the prompt alone.

STRATEGY:
    These tests construct a real UnifiedAIClient (it needs config_path to
    load), then drive _get_tool_usage_instructions under two different
    context conditions. The Flask-context test uses app.test_request_context
    to populate flask.g.rls_org_id the same way set_rls_context_from_jwt
    does in production. The non-Flask test runs the method bare.

    The vector_db_router makes a real DB read for the active provider,
    so this test exercises the full chain end-to-end against the live
    production DB (ryoicrdifiqhqpsnjmdo). Org 1 is the seed org.
"""

import importlib
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Suppress emoji-encoding crashes on Windows cp1252 stdout (UnifiedAIClient
# __init__ prints a warning emoji at line ~161). The init is otherwise OK.
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

CONFIG_PATH = str(REPO_ROOT / "config" / "database-config.json")


class UnifiedAIVectorDBGuidanceTests(unittest.TestCase):
    """The live prompt builder must inject the vector_db section when an
    authenticated request is in flight (g.rls_org_id is set), and must
    silently omit it otherwise."""

    @classmethod
    def setUpClass(cls):
        from flask import Flask
        from AI_infrastructure.core.unified_ai_client import UnifiedAIClient

        cls.app = Flask(__name__)
        cls.client = UnifiedAIClient(CONFIG_PATH)

    def test_prompt_includes_vector_db_section_under_flask_context(self):
        from flask import g

        with self.app.test_request_context("/"):
            # Simulate the JWT decode hook in flask_app.py:
            #   set_rls_context_from_jwt sets g.rls_user_id + g.rls_org_id
            g.rls_user_id = 1
            g.rls_org_id = 1

            prompt = self.client._get_tool_usage_instructions()

        self.assertIn(
            "=== VECTOR DATABASE ===",
            prompt,
            "Live prompt is missing the vector_db section under Flask context",
        )
        # The active provider is read from v_org_vector_status. Org 1 was
        # backfilled to 'pgvector' by migration 052.
        self.assertIn("pgvector", prompt)
        # All four smart tool names should be mentioned so the AI can pick.
        for tool_name in (
            "pgvector_query_vectors",
            "pgvector_search_summaries",
            "pgvector_fetch_by_metadata",
            "pgvector_get_vector_details",
        ):
            with self.subTest(tool=tool_name):
                self.assertIn(tool_name, prompt)

    def test_prompt_omits_section_outside_flask_context(self):
        """Outside a Flask request context (CLI, scheduled task), the
        section must be silently absent and the call must NOT raise."""
        prompt = self.client._get_tool_usage_instructions()
        self.assertNotIn("=== VECTOR DATABASE ===", prompt)
        # The base prompt must still be there (file or fallback path).
        self.assertGreater(len(prompt), 100)


if __name__ == "__main__":
    unittest.main()