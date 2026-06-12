"""
Populate pgvector embeddings for Supabase search system

This script generates OpenAI embeddings for existing records and populates
the vector columns created by supabase_search_core.sql

Tables processed:
- sessions.threads (name_embedding)
- sessions.messages (content_embedding)
- synergy_sessions.sessions (title_embedding)
- ai_infrastructure.internal_docs (content_embedding)

Usage:
    python populate_embeddings.py --batch-size 100 --user-id 14
    python populate_embeddings.py --table threads --limit 50
    python populate_embeddings.py --dry-run  # Test without writing
"""

import os
import sys
import json
import time
from typing import List, Dict, Optional
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import get_api_key_enhanced, OPENAI_API_KEYS
from AI_infrastructure.shared.database_utils import get_database_connection

try:
    import openai
except ImportError:
    print("ERROR: openai package not installed")
    print("Install with: pip install openai")
    sys.exit(1)


class EmbeddingPopulator:
    """Populate embeddings for search system"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.openai_client = None
        self.stats = {
            'threads': {'processed': 0, 'errors': 0, 'skipped': 0},
            'messages': {'processed': 0, 'errors': 0, 'skipped': 0},
            'synergy_sessions': {'processed': 0, 'errors': 0, 'skipped': 0},
            'internal_docs': {'processed': 0, 'errors': 0, 'skipped': 0}
        }
        
    def _init_openai(self):
        """Initialize OpenAI client"""
        if self.openai_client:
            return
            
        api_key = get_api_key_enhanced('openai')
        if not api_key:
            raise ValueError("No OpenAI API key found in config.py")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        print(f"✅ OpenAI client initialized")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI API"""
        if not text or not text.strip():
            return None
        
        try:
            self._init_openai()
            
            # Use text-embedding-3-small (1536 dimensions, same as pgvector columns)
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]  # Limit to 8000 chars for API
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None
    
    def populate_threads(self, user_id: Optional[int] = None, limit: Optional[int] = None, batch_size: int = 50):
        """Populate name_embedding for sessions.threads"""
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Populating threads embeddings...")
        
        conn = None
        try:
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            
            # Get threads without embeddings
            query = """
                SELECT id, name, thread_slug
                FROM sessions.threads
                WHERE name_embedding IS NULL
                  AND name IS NOT NULL
                  AND name != ''
            """
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            threads = cursor.fetchall()
            
            print(f"Found {len(threads)} threads to process")
            
            if len(threads) == 0:
                return
            
            # Process in batches
            for i in range(0, len(threads), batch_size):
                batch = threads[i:i+batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(threads)-1)//batch_size + 1}...")
                
                for thread in batch:
                    thread_id = thread['id'] if isinstance(thread, dict) else thread[0]
                    name = thread['name'] if isinstance(thread, dict) else thread[1]
                    
                    # Generate embedding
                    embedding = self.generate_embedding(name)
                    
                    if embedding:
                        if not self.dry_run:
                            cursor.execute("""
                                UPDATE sessions.threads
                                SET name_embedding = %s::vector
                                WHERE id = %s
                            """, (embedding, thread_id))
                        
                        self.stats['threads']['processed'] += 1
                        print(f"  ✅ Thread {thread_id}: {name[:50]}...")
                    else:
                        self.stats['threads']['errors'] += 1
                        print(f"  ⚠️  Thread {thread_id}: Failed to generate embedding")
                    
                    time.sleep(0.1)  # Rate limiting
                
                if not self.dry_run:
                    conn.commit()
                    print(f"  💾 Committed batch {i//batch_size + 1}")
            
            print(f"✅ Threads complete: {self.stats['threads']['processed']} processed")
            
        except Exception as e:
            print(f"❌ Error processing threads: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def populate_messages(self, user_id: Optional[int] = None, limit: Optional[int] = None, batch_size: int = 50):
        """Populate content_embedding for sessions.messages"""
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Populating messages embeddings...")
        
        conn = None
        try:
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            
            # Get messages without embeddings (user messages only, skip assistant)
            query = """
                SELECT m.message_id, m.content, m.role
                FROM sessions.messages m
                JOIN sessions.threads t ON m.thread_id = t.id
                WHERE m.content_embedding IS NULL
                  AND m.content IS NOT NULL
                  AND m.content != ''
                  AND m.role = 'user'
            """
            params = []
            
            if user_id:
                query += " AND t.user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY m.created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
            
            print(f"Found {len(messages)} messages to process")
            
            if len(messages) == 0:
                return
            
            # Process in batches
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i+batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(messages)-1)//batch_size + 1}...")
                
                for msg in batch:
                    msg_id = msg['message_id'] if isinstance(msg, dict) else msg[0]
                    content = msg['content'] if isinstance(msg, dict) else msg[1]
                    
                    # Generate embedding
                    embedding = self.generate_embedding(content)
                    
                    if embedding:
                        if not self.dry_run:
                            cursor.execute("""
                                UPDATE sessions.messages
                                SET content_embedding = %s::vector
                                WHERE message_id = %s
                            """, (embedding, msg_id))
                        
                        self.stats['messages']['processed'] += 1
                        print(f"  ✅ Message {msg_id}: {content[:50]}...")
                    else:
                        self.stats['messages']['errors'] += 1
                        print(f"  ⚠️  Message {msg_id}: Failed to generate embedding")
                    
                    time.sleep(0.1)  # Rate limiting
                
                if not self.dry_run:
                    conn.commit()
                    print(f"  💾 Committed batch {i//batch_size + 1}")
            
            print(f"✅ Messages complete: {self.stats['messages']['processed']} processed")
            
        except Exception as e:
            print(f"❌ Error processing messages: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def populate_synergy_sessions(self, user_id: Optional[int] = None, limit: Optional[int] = None, batch_size: int = 50):
        """Populate title_embedding for synergy_sessions.sessions"""
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Populating synergy sessions embeddings...")
        
        conn = None
        try:
            conn = get_database_connection('synergy_sessions')
            cursor = conn.cursor()
            
            # Get sessions without embeddings
            query = """
                SELECT session_id, session_title, description
                FROM synergy_sessions.sessions
                WHERE title_embedding IS NULL
                  AND session_title IS NOT NULL
                  AND session_title != ''
            """
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            sessions = cursor.fetchall()
            
            print(f"Found {len(sessions)} sessions to process")
            
            if len(sessions) == 0:
                return
            
            # Process in batches
            for i in range(0, len(sessions), batch_size):
                batch = sessions[i:i+batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(sessions)-1)//batch_size + 1}...")
                
                for session in batch:
                    session_id = session['session_id'] if isinstance(session, dict) else session[0]
                    title = session['session_title'] if isinstance(session, dict) else session[1]
                    
                    # Generate embedding
                    embedding = self.generate_embedding(title)
                    
                    if embedding:
                        if not self.dry_run:
                            cursor.execute("""
                                UPDATE synergy_sessions.sessions
                                SET title_embedding = %s::vector
                                WHERE session_id = %s
                            """, (embedding, session_id))
                        
                        self.stats['synergy_sessions']['processed'] += 1
                        print(f"  ✅ Session {session_id}: {title[:50]}...")
                    else:
                        self.stats['synergy_sessions']['errors'] += 1
                        print(f"  ⚠️  Session {session_id}: Failed to generate embedding")
                    
                    time.sleep(0.1)  # Rate limiting
                
                if not self.dry_run:
                    conn.commit()
                    print(f"  💾 Committed batch {i//batch_size + 1}")
            
            print(f"✅ Synergy sessions complete: {self.stats['synergy_sessions']['processed']} processed")
            
        except Exception as e:
            print(f"❌ Error processing synergy sessions: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def populate_internal_docs(self, limit: Optional[int] = None, batch_size: int = 50):
        """Populate content_embedding for ai_infrastructure.internal_docs"""
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Populating internal docs embeddings...")
        
        conn = None
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Get docs without embeddings
            query = """
                SELECT doc_id, title, content
                FROM ai_infrastructure.internal_docs
                WHERE content_embedding IS NULL
                  AND content IS NOT NULL
                  AND content != ''
                ORDER BY created_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            docs = cursor.fetchall()
            
            print(f"Found {len(docs)} docs to process")
            
            if len(docs) == 0:
                return
            
            # Process in batches
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i+batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(docs)-1)//batch_size + 1}...")
                
                for doc in batch:
                    doc_id = doc['doc_id'] if isinstance(doc, dict) else doc[0]
                    title = doc['title'] if isinstance(doc, dict) else doc[1]
                    content = doc['content'] if isinstance(doc, dict) else doc[2]
                    
                    # Combine title and content for embedding
                    text = f"{title}\n\n{content}"
                    
                    # Generate embedding
                    embedding = self.generate_embedding(text)
                    
                    if embedding:
                        if not self.dry_run:
                            cursor.execute("""
                                UPDATE ai_infrastructure.internal_docs
                                SET content_embedding = %s::vector
                                WHERE doc_id = %s
                            """, (embedding, doc_id))
                        
                        self.stats['internal_docs']['processed'] += 1
                        print(f"  ✅ Doc {doc_id}: {title[:50]}...")
                    else:
                        self.stats['internal_docs']['errors'] += 1
                        print(f"  ⚠️  Doc {doc_id}: Failed to generate embedding")
                    
                    time.sleep(0.1)  # Rate limiting
                
                if not self.dry_run:
                    conn.commit()
                    print(f"  💾 Committed batch {i//batch_size + 1}")
            
            print(f"✅ Internal docs complete: {self.stats['internal_docs']['processed']} processed")
            
        except Exception as e:
            print(f"❌ Error processing internal docs: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def print_stats(self):
        """Print final statistics"""
        print("\n" + "="*60)
        print("📊 EMBEDDING GENERATION STATISTICS")
        print("="*60)
        
        total_processed = 0
        total_errors = 0
        
        for table, stats in self.stats.items():
            print(f"\n{table.upper()}:")
            print(f"  Processed: {stats['processed']}")
            print(f"  Errors: {stats['errors']}")
            print(f"  Skipped: {stats['skipped']}")
            
            total_processed += stats['processed']
            total_errors += stats['errors']
        
        print(f"\nTOTAL:")
        print(f"  Processed: {total_processed}")
        print(f"  Errors: {total_errors}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Populate embeddings for Supabase search')
    parser.add_argument('--table', choices=['threads', 'messages', 'synergy', 'docs', 'all'],
                       default='all', help='Which table to process')
    parser.add_argument('--user-id', type=int, help='Filter by user ID')
    parser.add_argument('--limit', type=int, help='Limit number of records per table')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--dry-run', action='store_true', help='Test without writing to database')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 EMBEDDING POPULATION SCRIPT")
    print("="*60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")
    print(f"Table: {args.table}")
    if args.user_id:
        print(f"User ID: {args.user_id}")
    if args.limit:
        print(f"Limit: {args.limit} per table")
    print(f"Batch size: {args.batch_size}")
    print("="*60)
    
    populator = EmbeddingPopulator(dry_run=args.dry_run)
    
    try:
        if args.table in ['threads', 'all']:
            populator.populate_threads(args.user_id, args.limit, args.batch_size)
        
        if args.table in ['messages', 'all']:
            populator.populate_messages(args.user_id, args.limit, args.batch_size)
        
        if args.table in ['synergy', 'all']:
            populator.populate_synergy_sessions(args.user_id, args.limit, args.batch_size)
        
        if args.table in ['docs', 'all']:
            populator.populate_internal_docs(args.limit, args.batch_size)
        
        populator.print_stats()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        populator.print_stats()
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        populator.print_stats()


if __name__ == '__main__':
    main()
