"""
Simple One-at-a-Time Embedding Backfill
Avoids Supabase statement timeouts by processing individually
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment
_env_file = Path(__file__).parent / '.env.master'
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.implementations.conversation_memory import generate_embedding

def get_connection():
    """Get fresh connection"""
    db_url = os.getenv('SUPABASE_DB_URL_POOLER') or os.getenv('SUPABASE_DB_URL_SESSION')
    if not db_url:
        raise ValueError("No Supabase connection URL found")
    return psycopg2.connect(db_url)

def backfill_messages(limit=None):
    """Backfill messages one at a time"""
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Get count
    cur.execute("""
        SELECT COUNT(*) 
        FROM sessions.messages 
        WHERE content_embedding IS NULL 
        AND content IS NOT NULL
        AND LENGTH(TRIM(COALESCE(content->>'text', content::text))) > 20
    """)
    total = cur.fetchone()[0]
    
    print(f"\n🔍 Found {total} messages without embeddings")
    
    if total == 0:
        print("✅ All messages have embeddings!")
        return
    
    if limit:
        total = min(total, limit)
        print(f"📊 Processing {total} messages (limited)")
    
    processed = 0
    errors = 0
    start_time = time.time()
    
    # Track failed IDs to skip
    failed_ids = set()
    
    try:
        while processed < total:
            # Get one message (skip known failures)
            if failed_ids:
                placeholders = ','.join(['%s'] * len(failed_ids))
                cur.execute(f"""
                    SELECT id, content
                    FROM sessions.messages 
                    WHERE content_embedding IS NULL 
                    AND content IS NOT NULL
                    AND LENGTH(TRIM(COALESCE(content->>'text', content::text))) > 20
                    AND id NOT IN ({placeholders})
                    ORDER BY created_at DESC
                    LIMIT 1
                """, tuple(failed_ids))
            else:
                cur.execute("""
                    SELECT id, content
                    FROM sessions.messages 
                    WHERE content_embedding IS NULL 
                    AND content IS NOT NULL
                    AND LENGTH(TRIM(COALESCE(content->>'text', content::text))) > 20
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
            
            row = cur.fetchone()
            if not row:
                break
                
            msg_id, content = row
            
            try:
                # Extract text from JSONB
                if isinstance(content, dict):
                    content_text = content.get('text', str(content))
                elif isinstance(content, str):
                    content_text = content
                else:
                    content_text = str(content)
                
                # Generate embedding
                embedding = generate_embedding(content_text[:8000])
                
                if embedding:
                    # Update with new connection per update
                    update_conn = get_connection()
                    update_cur = update_conn.cursor()
                    
                    update_cur.execute("""
                        UPDATE sessions.messages 
                        SET content_embedding = %s::vector
                        WHERE id = %s
                    """, (embedding, msg_id))
                    
                    update_conn.commit()
                    update_cur.close()
                    update_conn.close()
                    
                    processed += 1
                    
                    if processed % 10 == 0:
                        elapsed = time.time() - start_time
                        rate = processed / elapsed if elapsed > 0 else 0
                        remaining = (total - processed) / rate if rate > 0 else 0
                        print(f"  ✓ {processed}/{total} ({rate:.1f} msgs/sec, ~{int(remaining)}s remaining)")
                        
            except Exception as e:
                errors += 1
                failed_ids.add(msg_id)  # Skip this one next time
                print(f"  ❌ Error on message {msg_id}: {str(e)[:100]}... (skipping)")
                time.sleep(0.5)  # Brief pause on error
                continue
                
    finally:
        cur.close()
        conn.close()
    
    elapsed = time.time() - start_time
    print(f"\n✅ Complete! Processed: {processed}, Errors: {errors}, Time: {elapsed:.1f}s")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, help='Max messages to process')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 SIMPLE EMBEDDING BACKFILL (One-at-a-time)")
    print("=" * 60)
    
    backfill_messages(limit=args.limit)
