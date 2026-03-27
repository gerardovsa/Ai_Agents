"""
fix_model_catalog_ids.py
========================
Corrects model IDs in ai_infrastructure.ai_model_catalog that were seeded with
fabricated/incorrect values in the initial run of migration 037.

Changes applied:
  Anthropic:
    - claude-sonnet-4-6-20260213  →  claude-sonnet-4-6  (fake date; real ID has no suffix)
    - INSERT claude-opus-4-6                              (was missing from initial seed)

  OpenAI:
    - DELETE gpt-4.5-preview                             (not a real API model ID)
    - INSERT gpt-5.4, gpt-5.1, gpt-5-mini               (current frontier models)
    - INSERT o4-mini                                      (was missing)

  DeepSeek:
    - DeepSeek Reasoner display updated to V3.2          (minor label fix)

Sources:
  Anthropic: https://docs.anthropic.com/en/docs/about-claude/models/overview
  OpenAI:    https://developers.openai.com/api/docs/models
  DeepSeek:  https://api-docs.deepseek.com/quick_start/pricing
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    print("ERROR: SUPABASE_DB_URL is not set in .env")
    sys.exit(1)

SQL = """
-- ── 1. Fix wrong Anthropic Sonnet 4.6 ID ────────────────────────────────────
UPDATE ai_infrastructure.ai_model_catalog
SET model_id = 'claude-sonnet-4-6',
    context_window = 1000000,
    updated_at = NOW()
WHERE provider = 'anthropic' AND model_id = 'claude-sonnet-4-6-20260213';

-- ── 2. Remove fake Claude Sonnet 4 (claude-sonnet-4-20250514 unverified) ────
-- (optional: comment this out if you want to keep it as-is)
-- DELETE FROM ai_infrastructure.ai_model_catalog
-- WHERE provider = 'anthropic' AND model_id = 'claude-sonnet-4-20250514';

-- ── 3. Add Claude Opus 4.6 (was missing) ────────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision, supports_thinking, sort_order)
VALUES
    ('anthropic', 'claude-opus-4-6',
     'Claude Opus 4.6',
     'Most intelligent Claude model. Best for complex coding, agents, and research tasks.',
     'powerful', 1000000, FALSE, TRUE, TRUE, TRUE, 5)
ON CONFLICT (provider, model_id) DO NOTHING;

-- ── 4. Remove fake GPT-4.5 Preview ──────────────────────────────────────────
DELETE FROM ai_infrastructure.ai_model_catalog
WHERE provider = 'openai' AND model_id = 'gpt-4.5-preview';

-- ── 5. Remove o1-mini (unconfirmed current availability) ────────────────────
-- DELETE FROM ai_infrastructure.ai_model_catalog
-- WHERE provider = 'openai' AND model_id = 'o1-mini';

-- ── 6. Add current OpenAI frontier models ───────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision, supports_thinking, sort_order)
VALUES
    ('openai', 'gpt-5.4',
     'GPT-5.4',
     'OpenAI frontier model. Best intelligence at scale for agentic, coding, and professional work.',
     'powerful', 1050000, FALSE, TRUE, TRUE, TRUE, 100),
    ('openai', 'gpt-5.1',
     'GPT-5.1',
     'Best model for coding and agentic tasks. Configurable reasoning effort.',
     'powerful', 400000, FALSE, TRUE, TRUE, TRUE, 105),
    ('openai', 'gpt-5-mini',
     'GPT-5 Mini',
     'Near-frontier intelligence for cost-sensitive, low-latency, high-volume workloads.',
     'fast', 400000, FALSE, TRUE, TRUE, FALSE, 108),
    ('openai', 'o4-mini',
     'OpenAI o4-mini',
     'Fast, cost-efficient reasoning. Optimised for coding and visual tasks.',
     'reasoning', 200000, FALSE, TRUE, TRUE, TRUE, 135)
ON CONFLICT (provider, model_id) DO NOTHING;

-- ── 7. Fix sort_order for existing OpenAI models ────────────────────────────
UPDATE ai_infrastructure.ai_model_catalog SET sort_order = 110 WHERE provider = 'openai' AND model_id = 'gpt-4o';
UPDATE ai_infrastructure.ai_model_catalog SET sort_order = 120 WHERE provider = 'openai' AND model_id = 'gpt-4o-mini';
UPDATE ai_infrastructure.ai_model_catalog SET sort_order = 130 WHERE provider = 'openai' AND model_id = 'o3';
UPDATE ai_infrastructure.ai_model_catalog SET sort_order = 140 WHERE provider = 'openai' AND model_id = 'o3-mini';
UPDATE ai_infrastructure.ai_model_catalog SET sort_order = 150 WHERE provider = 'openai' AND model_id = 'o1';

-- ── 8. Fix DeepSeek display names ────────────────────────────────────────────
UPDATE ai_infrastructure.ai_model_catalog
SET display_name = 'DeepSeek Chat (V3.2)', updated_at = NOW()
WHERE provider = 'deepseek' AND model_id = 'deepseek-chat';

UPDATE ai_infrastructure.ai_model_catalog
SET display_name = 'DeepSeek Reasoner (V3.2)', updated_at = NOW()
WHERE provider = 'deepseek' AND model_id = 'deepseek-reasoner';
"""


def run():
    print("Connecting to Supabase...")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("Running model catalog corrections...")
    try:
        cur.execute(SQL)
        print("Corrections applied successfully.")
    except Exception as e:
        print(f"ERROR: {e}")
        conn.close()
        sys.exit(1)

    # Verify final state
    cur.execute("""
        SELECT provider, model_id, display_name, is_recommended, sort_order
        FROM ai_infrastructure.ai_model_catalog
        WHERE is_active = TRUE
        ORDER BY sort_order, provider
    """)
    rows = cur.fetchall()
    print(f"\n{'='*70}")
    print(f"  ai_model_catalog — {len(rows)} active models")
    print(f"{'='*70}")
    for r in rows:
        star = " ★" if r['is_recommended'] else "  "
        print(f"{star} [{r['provider']:10s}] {r['model_id']:40s}  {r['display_name']}")
    print(f"{'='*70}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    run()
