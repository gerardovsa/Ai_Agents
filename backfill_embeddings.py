"""
Backfill Embeddings for Existing Database Records
Generates embeddings for threads and messages that don't have them yet.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.master
_env_file = Path(__file__).parent / '.env.master'
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()  # Try default .env

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.implementations.conversation_memory import generate_embedding

def get_connection():
    """Get database connection using Supabase URL from environment"""
    # Try Transaction Mode pooler first (port 6543) - optimal for batch operations
    db_url = os.getenv('SUPABASE_DB_URL_POOLER')
    
    if not db_url:
        # Fallback to Session Mode pooler (port 5432)
        db_url = os.getenv('SUPABASE_DB_URL_SESSION')
        print("⚠️  Using Session Mode pooler (Transaction Mode not configured)")
    
    if not db_url:
        raise ValueError(
            "No Supabase connection URL found. Set either:\n"
            "  - SUPABASE_DB_URL_POOLER (Transaction Mode, port 6543) - RECOMMENDED\n"
            "  - SUPABASE_DB_URL_SESSION (Session Mode, port 5432) - FALLBACK"
        )
    
    return psycopg2.connect(db_url)

def backfill_thread_embeddings(batch_size=100, max_threads=None):
    """
    Backfill name_embedding for threads that don't have it
    
    Args:
        batch_size: Number of threads to process per batch
        max_threads: Maximum number of threads to process (None = all)
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Count threads needing embeddings
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM sessions.threads 
        WHERE name_embedding IS NULL 
        AND name IS NOT NULL
    """)
    total = cur.fetchone()['count']
    
    print(f"\n🔍 Found {total} threads without embeddings")
    
    if total == 0:
        print("✅ All threads already have embeddings!")
        cur.close()
        conn.close()
        return
    
    if max_threads:
        total = min(total, max_threads)
        print(f"📊 Processing {total} threads (limited by max_threads)")
    
    processed = 0
    errors = 0
    skipped = 0
    
    try:
        # Fetch threads in batches
        limit = max_threads if max_threads else total
        cur.execute("""
            SELECT id, name, created_at
            FROM sessions.threads 
            WHERE name_embedding IS NULL 
            AND name IS NOT NULL
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        threads = cur.fetchall()
        
        print(f"\n⚙️  Processing {len(threads)} threads in batches of {batch_size}...")
        start_time = time.time()
        
        for i, thread in enumerate(threads):
            try:
                # Build text to embed (just thread name)
                embed_text = thread['name']
                
                # Generate embedding
                embedding = generate_embedding(embed_text[:2000])
                
                if embedding:
                    # Update database with immediate commit (avoid timeouts)
                    try:
                        cur.execute("""
                            UPDATE sessions.threads 
                            SET name_embedding = %s::vector
                            WHERE id = %s
                        """, (embedding, thread['id']))
                        conn.commit()  # Commit immediately per thread
                        
                        processed += 1
                        
                        # Progress update every batch_size
                        if processed % batch_size == 0:
                            elapsed = time.time() - start_time
                            rate = processed / elapsed if elapsed > 0 else 0
                            remaining = (total - processed) / rate if rate > 0 else 0
                            print(f"  ✓ {processed}/{total} threads ({int(rate)} threads/sec, ~{int(remaining)}s remaining)")
                    except Exception as update_error:
                        print(f"  ⚠️  Update failed for thread {thread['id']}: {update_error}")
                        conn.rollback()
                        errors += 1
                        continue
                else:
                    skipped += 1
                    print(f"  ⚠️  Skipped thread {thread['id']}: Empty embedding")
                    
            except Exception as e:
                errors += 1
                print(f"  ❌ Error processing thread {thread['id']}: {e}")
                # Rollback on error
                try:
                    conn.rollback()
                except:
                    pass
                continue
        
        # Final commit
        conn.commit()
        elapsed = time.time() - start_time
        
        print(f"\n✅ Thread Embedding Backfill Complete!")
        print(f"   Processed: {processed}")
        print(f"   Skipped: {skipped}")
        print(f"   Errors: {errors}")
        print(f"   Time: {elapsed:.1f}s ({processed/elapsed:.1f} threads/sec)")
        
    except Exception as e:
        print(f"\n❌ Fatal error during thread backfill: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def backfill_message_embeddings(batch_size=100, max_messages=None):
    """
    Backfill content_embedding for messages that don't have it
    
    Args:
        batch_size: Number of messages to process per batch
        max_messages: Maximum number of messages to process (None = all)
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Count messages needing embeddings (only substantive content)
    # Note: content is JSONB, extract text content
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM sessions.messages 
        WHERE content_embedding IS NULL 
        AND content IS NOT NULL
        AND LENGTH(TRIM(COALESCE(content->>'text', content::text))) > 20
    """)
    total = cur.fetchone()['count']
    
    print(f"\n🔍 Found {total} messages without embeddings")
    
    if total == 0:
        print("✅ All messages already have embeddings!")
        cur.close()
        conn.close()
        return
    
    if max_messages:
        total = min(total, max_messages)
        print(f"📊 Processing {total} messages (limited by max_messages)")
    
    processed = 0
    errors = 0
    skipped = 0
    
    try:
        # Fetch messages in batches
        limit = max_messages if max_messages else total
        cur.execute("""
            SELECT id, content, created_at
            FROM sessions.messages 
            WHERE content_embedding IS NULL 
            AND content IS NOT NULL
            AND LENGTH(TRIM(COALESCE(content->>'text', content::text))) > 20
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        messages = cur.fetchall()
        
        print(f"\n⚙️  Processing {len(messages)} messages in batches of {batch_size}...")
        start_time = time.time()
        
        for i, message in enumerate(messages):
            try:
                # Extract text from JSONB content
                content_obj = message['content']
                if isinstance(content_obj, dict):
                    content_text = content_obj.get('text', str(content_obj))
                else:
                    content_text = str(content_obj)
                
                # Generate embedding (limit to 8K chars)
                content_text = content_text[:8000]
                embedding = generate_embedding(content_text)
                
                if embedding:
                    # Update database with immediate commit (avoid timeouts)
                    try:
                        cur.execute("""
                            UPDATE sessions.messages 
                            SET content_embedding = %s::vector
                            WHERE id = %s
                        """, (embedding, message['id']))
                        conn.commit()  # Commit immediately per message
                        
                        processed += 1
                        
                        # Progress update every batch_size
                        if processed % batch_size == 0:
                            elapsed = time.time() - start_time
                            rate = processed / elapsed if elapsed > 0 else 0
                            remaining = (total - processed) / rate if rate > 0 else 0
                            print(f"  ✓ {processed}/{total} messages ({int(rate)} msgs/sec, ~{int(remaining)}s remaining)")
                    except Exception as update_error:
                        print(f"  ⚠️  Update failed for message {message['id']}: {update_error}")
                        conn.rollback()
                        errors += 1
                        continue
                else:
                    skipped += 1
                    print(f"  ⚠️  Skipped message {message['id']}: Empty embedding")
                    
            except Exception as e:
                errors += 1
                print(f"  ❌ Error processing message {message['id']}: {e}")
                # Rollback on error and reconnect
                try:
                    conn.rollback()
                except:
                    pass
                continue
        
        # Final commit
        conn.commit()
        elapsed = time.time() - start_time
        
        print(f"\n✅ Message Embedding Backfill Complete!")
        print(f"   Processed: {processed}")
        print(f"   Skipped: {skipped}")
        print(f"   Errors: {errors}")
        print(f"   Time: {elapsed:.1f}s ({processed/elapsed:.1f} msgs/sec)")
        
    except Exception as e:
        print(f"\n❌ Fatal error during message backfill: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def check_embedding_coverage():
    """Check what percentage of records have embeddings"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n📊 Embedding Coverage Report")
    print("=" * 60)
    
    # Threads
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(name_embedding) as with_embedding,
            ROUND(100.0 * COUNT(name_embedding) / NULLIF(COUNT(*), 0), 1) as percent
        FROM sessions.threads
        WHERE name IS NOT NULL
    """)
    threads = cur.fetchone()
    print(f"\n📝 Threads:")
    print(f"   Total: {threads['total']}")
    print(f"   With Embeddings: {threads['with_embedding']} ({threads['percent']}%)")
    print(f"   Missing: {threads['total'] - threads['with_embedding']}")
    
    # Messages
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(content_embedding) as with_embedding,
            ROUND(100.0 * COUNT(content_embedding) / NULLIF(COUNT(*), 0), 1) as percent
        FROM sessions.messages
        WHERE content IS NOT NULL AND LENGTH(TRIM(COALESCE(content->>'text', content::text))) > 20
    """)
    messages = cur.fetchone()
    print(f"\n💬 Messages (>20 chars):")
    print(f"   Total: {messages['total']}")
    print(f"   With Embeddings: {messages['with_embedding']} ({messages['percent']}%)")
    print(f"   Missing: {messages['total'] - messages['with_embedding']}")
    
    print("\n" + "=" * 60)
    
    cur.close()
    conn.close()

def main():
    """Main backfill script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill embeddings for database records')
    parser.add_argument('--threads', type=int, help='Max threads to process (default: all)')
    parser.add_argument('--messages', type=int, help='Max messages to process (default: all)')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size (default: 100)')
    parser.add_argument('--check-only', action='store_true', help='Only check coverage, no backfill')
    parser.add_argument('--threads-only', action='store_true', help='Only process threads')
    parser.add_argument('--messages-only', action='store_true', help='Only process messages')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 DATABASE EMBEDDING BACKFILL")
    print("=" * 60)
    
    # Check coverage first
    check_embedding_coverage()
    
    if args.check_only:
        print("\n✅ Coverage check complete (--check-only flag)")
        return
    
    # Auto-proceed without confirmation
    print("\n⚙️  Starting backfill process...")
    print("   Estimated cost: $0.00001 per embedding")
    
    # Process threads
    if not args.messages_only:
        backfill_thread_embeddings(
            batch_size=args.batch_size,
            max_threads=args.threads
        )
    
    # Process messages
    if not args.threads_only:
        backfill_message_embeddings(
            batch_size=args.batch_size,
            max_messages=args.messages
        )
    
    # Final coverage check
    check_embedding_coverage()
    
    print("\n✅ Backfill Complete!")

if __name__ == '__main__':
    main()
