"""Run migration 037 - AI Model Catalog"""
import sys, os, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

import psycopg2
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv("SUPABASE_DB_URL")
if not db_url:
    print("ERROR: SUPABASE_DB_URL not set in .env")
    sys.exit(1)

sql_path = pathlib.Path(__file__).parent / "AI_infrastructure" / "migrations" / "037_ai_model_catalog.sql"
sql = sql_path.read_text(encoding="utf-8")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute(sql)
    print("Migration 037 applied successfully.")
except Exception as e:
    print(f"Migration error: {e}")
finally:
    try:
        cur.execute(
            "SELECT provider, model_id, is_recommended FROM ai_infrastructure.ai_model_catalog ORDER BY sort_order"
        )
        rows = cur.fetchall()
        for provider, model_id, rec in rows:
            tag = "  RECOMMENDED" if rec else ""
            print(f"  {provider:12} {model_id}{tag}")
        print(f"\nTotal: {len(rows)} models in catalog.")
    except Exception as e2:
        print(f"Could not verify: {e2}")
    cur.close()
    conn.close()
