"""
Enable pgvector Extension and Populate Message Embeddings

This migration script:
1. Enables the pgvector extension on PostgreSQL
2. Converts embedding_vector column from TEXT to vector(1536)
3. Creates GIN index for fast similarity search
4. Generates embeddings for existing messages (batch processing)
5. Sets up trigger for auto-embedding new messages (optional)

REQUIREMENTS:
- PostgreSQL database with pgvector extension available
- OpenAI API key for generating embeddings
- psycopg2 library installed
- openai library installed (pip install openai)

COST ESTIMATE:
- ~$2-3 one-time for ~10,000 existing messages
- ~$1/month for ongoing embeddings (assuming 50,000 messages/month)

Author: AI Agent
Date: December 2025
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import time
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("❌ OpenAI library not installed. Run: pip install openai")
    sys.exit(1)


def get_database_connection():
    """Get Supabase PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("SUPABASE_HOST"),
            database=os.environ.get("SUPABASE_DATABASE", "postgres"),
            user=os.environ.get("SUPABASE_USER"),
            password=os.environ.get("SUPABASE_PASSWORD"),
            port=os.environ.get("SUPABASE_PORT", "5432")
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def generate_embedding(text: str, client: OpenAI) -> List[float]:
    """Generate OpenAI embedding for text"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Truncate to 8000 chars (~2000 tokens)
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"⚠️ Embedding generation failed: {e}")
        return None


def step1_enable_pgvector():
    """Step 1: Enable pgvector extension"""
    print("\n" + "="*70)
    print("STEP 1: Enable pgvector Extension")
    print("="*70)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if pgvector is available
        cursor.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector';")
        result = cursor.fetchone()
        
        if not result:
            print("❌ pgvector extension not available on this PostgreSQL instance")
            print("   Contact your database administrator or enable it in Supabase")
            conn.close()
            return False
        
        # Enable pgvector extension
        print("📦 Enabling pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        print("✅ pgvector extension enabled")
        
        # Verify installation
        cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
        version = cursor.fetchone()
        if version:
            print(f"✅ pgvector version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to enable pgvector: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def step2_convert_column_type():
    """Step 2: Convert embedding_vector from TEXT to vector(1536)"""
    print("\n" + "="*70)
    print("STEP 2: Convert embedding_vector Column to vector(1536)")
    print("="*70)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check current column type
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'workspace_chats' 
            AND table_name = 'messages' 
            AND column_name = 'embedding_vector';
        """)
        current_type = cursor.fetchone()
        
        if not current_type:
            print("❌ embedding_vector column not found in workspace_chats.messages")
            conn.close()
            return False
        
        print(f"📊 Current column type: {current_type[0]}")
        
        if current_type[0] == 'USER-DEFINED':
            print("✅ Column already using vector type - skipping conversion")
            cursor.close()
            conn.close()
            return True
        
        # Backup warning
        print("\n⚠️  WARNING: This will convert the column type")
        print("   Current data (if any) will be cleared")
        print("   Make sure you have a database backup!")
        
        response = input("\n   Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled by user")
            conn.close()
            return False
        
        # Convert column type
        print("\n🔄 Converting column type to vector(1536)...")
        cursor.execute("""
            ALTER TABLE workspace_chats.messages 
            ALTER COLUMN embedding_vector TYPE vector(1536) 
            USING NULL::vector(1536);
        """)
        conn.commit()
        print("✅ Column type converted to vector(1536)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to convert column: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def step3_create_index():
    """Step 3: Create GIN index for fast similarity search"""
    print("\n" + "="*70)
    print("STEP 3: Create Vector Similarity Index")
    print("="*70)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        print("📊 Creating ivfflat index for cosine similarity search...")
        print("   (This may take a few minutes for large tables)")
        
        # Create index using ivfflat algorithm (good for cosine distance)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_embedding_vector
            ON workspace_chats.messages 
            USING ivfflat (embedding_vector vector_cosine_ops)
            WITH (lists = 100);
        """)
        conn.commit()
        print("✅ Vector similarity index created")
        
        # Verify index
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'messages' 
            AND indexname = 'idx_messages_embedding_vector';
        """)
        index_info = cursor.fetchone()
        if index_info:
            print(f"✅ Index verified: {index_info[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create index: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def step4_populate_embeddings(batch_size=100, max_messages=None, skip_existing=True):
    """Step 4: Generate embeddings for existing messages"""
    print("\n" + "="*70)
    print("STEP 4: Generate Embeddings for Existing Messages")
    print("="*70)
    
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='sk-...'")
        return False
    
    client = OpenAI(api_key=api_key)
    conn = get_database_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Count messages needing embeddings
        if skip_existing:
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM workspace_chats.messages 
                WHERE embedding_vector IS NULL AND content IS NOT NULL;
            """)
        else:
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM workspace_chats.messages 
                WHERE content IS NOT NULL;
            """)
        
        total_count = cursor.fetchone()['count']
        
        if max_messages:
            total_count = min(total_count, max_messages)
        
        print(f"\n📊 Messages to process: {total_count:,}")
        
        if total_count == 0:
            print("✅ No messages need embeddings - all done!")
            cursor.close()
            conn.close()
            return True
        
        # Estimate cost
        estimated_tokens = total_count * 500  # Average ~500 tokens per message
        estimated_cost = (estimated_tokens / 1_000_000) * 0.02  # $0.02 per 1M tokens
        print(f"💰 Estimated cost: ${estimated_cost:.2f}")
        print(f"⏱️  Estimated time: {(total_count / batch_size) * 1.5:.1f} minutes")
        
        response = input("\n   Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Embedding generation cancelled by user")
            conn.close()
            return False
        
        # Process in batches
        print(f"\n🔄 Processing in batches of {batch_size}...")
        processed = 0
        failed = 0
        start_time = time.time()
        
        while processed < total_count:
            # Get batch of messages
            if skip_existing:
                cursor.execute(f"""
                    SELECT id, content 
                    FROM workspace_chats.messages 
                    WHERE embedding_vector IS NULL AND content IS NOT NULL
                    LIMIT {batch_size};
                """)
            else:
                cursor.execute(f"""
                    SELECT id, content 
                    FROM workspace_chats.messages 
                    WHERE content IS NOT NULL
                    LIMIT {batch_size} OFFSET {processed};
                """)
            
            messages = cursor.fetchall()
            
            if not messages:
                break
            
            # Generate embeddings for batch
            for msg in messages:
                embedding = generate_embedding(msg['content'], client)
                
                if embedding:
                    # Update message with embedding
                    cursor.execute("""
                        UPDATE workspace_chats.messages 
                        SET embedding_vector = %s::vector 
                        WHERE id = %s;
                    """, (embedding, msg['id']))
                    processed += 1
                else:
                    failed += 1
            
            conn.commit()
            
            # Progress update
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = (total_count - processed) / rate if rate > 0 else 0
            
            print(f"   Progress: {processed:,}/{total_count:,} ({(processed/total_count*100):.1f}%) | "
                  f"Rate: {rate:.1f} msg/s | "
                  f"ETA: {remaining/60:.1f} min | "
                  f"Failed: {failed}")
            
            # Rate limiting (max 3000 requests/min = 50/sec)
            time.sleep(batch_size / 50)
        
        total_time = time.time() - start_time
        print(f"\n✅ Embedding generation complete!")
        print(f"   Processed: {processed:,} messages")
        print(f"   Failed: {failed}")
        print(f"   Total time: {total_time/60:.1f} minutes")
        print(f"   Average rate: {processed/total_time:.1f} messages/second")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to populate embeddings: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def step5_create_trigger():
    """Step 5: Create trigger to auto-generate embeddings for new messages (optional)"""
    print("\n" + "="*70)
    print("STEP 5: Create Auto-Embedding Trigger (Optional)")
    print("="*70)
    
    print("\n⚠️  NOTE: Auto-embedding trigger is optional")
    print("   Pros: Automatic embedding generation for new messages")
    print("   Cons: Requires application-level implementation (not DB trigger)")
    print("\n   Recommendation: Implement in application code instead")
    print("   Add embedding generation to message creation endpoint")
    
    response = input("\n   Skip this step? (yes/no): ")
    if response.lower() == 'yes':
        print("⏭️  Skipped - implement auto-embedding in application code")
        return True
    
    print("\n❌ Database triggers for OpenAI API calls are not recommended")
    print("   Implement auto-embedding in your Flask API endpoint instead:")
    print("""
    # Example implementation in chat endpoint:
    from tools.implementations.workspace_search import generate_embedding
    
    @app.route('/api/chat/message', methods=['POST'])
    def create_message():
        # ... save message ...
        
        # Generate embedding asynchronously
        embedding = generate_embedding(message_content)
        
        # Update message with embedding
        cursor.execute(
            "UPDATE messages SET embedding_vector = %s WHERE id = %s",
            (embedding, message_id)
        )
    """)
    
    return True


def verify_setup():
    """Verify the complete setup"""
    print("\n" + "="*70)
    print("VERIFICATION: Checking Setup")
    print("="*70)
    
    conn = get_database_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check extension
        cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
        ext_version = cursor.fetchone()
        if ext_version:
            print(f"✅ pgvector extension: v{ext_version['extversion']}")
        else:
            print("❌ pgvector extension not installed")
        
        # Check column type
        cursor.execute("""
            SELECT data_type, udt_name
            FROM information_schema.columns 
            WHERE table_schema = 'workspace_chats' 
            AND table_name = 'messages' 
            AND column_name = 'embedding_vector';
        """)
        col_type = cursor.fetchone()
        if col_type:
            print(f"✅ Column type: {col_type['data_type']} ({col_type['udt_name']})")
        else:
            print("❌ embedding_vector column not found")
        
        # Check index
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'messages' 
            AND indexname = 'idx_messages_embedding_vector';
        """)
        index = cursor.fetchone()
        if index:
            print(f"✅ Vector index: {index['indexname']}")
        else:
            print("⚠️  Vector index not found (may impact performance)")
        
        # Count embedded messages
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(embedding_vector) as embedded,
                COUNT(*) - COUNT(embedding_vector) as missing
            FROM workspace_chats.messages
            WHERE content IS NOT NULL;
        """)
        counts = cursor.fetchone()
        print(f"\n📊 Message Statistics:")
        print(f"   Total messages: {counts['total']:,}")
        print(f"   With embeddings: {counts['embedded']:,} ({counts['embedded']/counts['total']*100:.1f}%)")
        print(f"   Missing embeddings: {counts['missing']:,}")
        
        cursor.close()
        conn.close()
        
        if counts['embedded'] > 0:
            print(f"\n✅ Setup complete! Semantic search is ready to use")
            return True
        else:
            print(f"\n⚠️  Setup incomplete - no messages have embeddings yet")
            print(f"   Run step 4 to generate embeddings")
            return False
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        cursor.close()
        conn.close()
        return False


def main():
    """Run complete migration"""
    print("="*70)
    print("🚀 PGVECTOR SETUP & EMBEDDING POPULATION")
    print("="*70)
    
    print("\nThis script will:")
    print("1. Enable pgvector extension")
    print("2. Convert embedding_vector column to vector(1536)")
    print("3. Create similarity search index")
    print("4. Generate embeddings for existing messages")
    print("5. (Optional) Set up auto-embedding trigger")
    
    print("\n⚠️  IMPORTANT:")
    print("- Make sure you have a database backup")
    print("- OpenAI API key must be set: export OPENAI_API_KEY='sk-...'")
    print("- This will cost ~$2-3 for ~10,000 messages")
    
    response = input("\nContinue with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("\n❌ Migration cancelled")
        return
    
    # Run migration steps
    success = True
    
    success = step1_enable_pgvector() and success
    if not success:
        print("\n❌ Migration failed at step 1")
        return
    
    success = step2_convert_column_type() and success
    if not success:
        print("\n❌ Migration failed at step 2")
        return
    
    success = step3_create_index() and success
    if not success:
        print("\n⚠️  Migration continued without index (performance may be impacted)")
    
    # Ask about batch size and limits
    print("\n📋 Embedding Generation Options:")
    print("   Batch size: Number of messages to process at once (default: 100)")
    print("   Max messages: Limit total messages (default: all)")
    
    batch_size = input("\n   Batch size (press Enter for 100): ")
    batch_size = int(batch_size) if batch_size else 100
    
    max_messages = input("   Max messages (press Enter for all): ")
    max_messages = int(max_messages) if max_messages else None
    
    success = step4_populate_embeddings(batch_size, max_messages) and success
    if not success:
        print("\n❌ Migration failed at step 4")
        return
    
    step5_create_trigger()
    
    # Final verification
    print("\n" + "="*70)
    verify_setup()
    print("="*70)
    
    print("\n🎉 Migration complete!")
    print("\n📚 Next steps:")
    print("   1. Test semantic search with workspace_semantic_search()")
    print("   2. Implement auto-embedding in your chat endpoint")
    print("   3. Monitor embedding generation costs")
    print(f"\n   See: tools/schemas/workspace_search_tools.json for usage examples")


if __name__ == "__main__":
    main()
