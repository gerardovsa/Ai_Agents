"""
Migration: Create tool embeddings tables in Supabase

Purpose: Set up persistent storage for semantic tool search embeddings

Tables:
- ai_infrastructure.tool_embeddings (stores individual tool embeddings)
- ai_infrastructure.tool_embedding_cache (stores cache metadata)

Date: 2026-01-02
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from AI_infrastructure.shared.database_utils import execute_query


def run_migration():
    """Create tool embedding tables"""
    print("\n" + "=" * 80)
    print("MIGRATION: Create Tool Embeddings Tables")
    print("=" * 80)
    
    try:
        # Step 1: Create schema
        print("\n[1/5] Creating ai_infrastructure schema...")
        execute_query("""
            CREATE SCHEMA IF NOT EXISTS ai_infrastructure
        """)
        print("✅ Schema created")
        
        # Step 2: Enable pgvector extension
        print("\n[2/5] Enabling pgvector extension...")
        execute_query("""
            CREATE EXTENSION IF NOT EXISTS vector
        """)
        print("✅ pgvector enabled")
        
        # Step 3: Create tool_embeddings table
        print("\n[3/5] Creating tool_embeddings table...")
        execute_query("""
            CREATE TABLE IF NOT EXISTS ai_infrastructure.tool_embeddings (
                tool_name TEXT PRIMARY KEY,
                embedding vector(384),
                tool_metadata JSONB,
                version_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("✅ tool_embeddings table created")
        
        # Step 4: Create tool_embedding_cache table
        print("\n[4/5] Creating tool_embedding_cache table...")
        execute_query("""
            CREATE TABLE IF NOT EXISTS ai_infrastructure.tool_embedding_cache (
                cache_key TEXT PRIMARY KEY,
                version_hash TEXT NOT NULL,
                total_tools INTEGER NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("✅ tool_embedding_cache table created")
        
        # Step 5: Create indexes
        print("\n[5/5] Creating indexes...")
        
        # Index on version_hash for fast filtering
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_tool_embeddings_version_hash 
            ON ai_infrastructure.tool_embeddings(version_hash)
        """)
        
        # Vector similarity index (IVFFlat for fast nearest neighbor search)
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_tool_embeddings_vector 
            ON ai_infrastructure.tool_embeddings 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        
        print("✅ Indexes created")
        
        # Show table info
        print("\n" + "=" * 80)
        print("MIGRATION COMPLETE")
        print("=" * 80)
        
        # Verify tables exist
        tables = execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name LIKE 'tool_embedding%'
            ORDER BY table_name
        """, fetch_mode='all')
        
        print("\n📊 Created tables:")
        for table in tables:
            print(f"   ✅ {table['table_name']}")
        
        print("\n📝 Next Steps:")
        print("   1. Restart Flask server to generate embeddings")
        print("   2. Or run: python tools/manage_semantic_cache.py regenerate")
        print("   3. Check status: python tools/manage_semantic_cache.py status")
        print()
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_migration()
