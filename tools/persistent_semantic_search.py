"""
FILE: tools/persistent_semantic_search.py
PURPOSE: Supabase-backed persistent tool embeddings with smart caching

FEATURES:
- Store tool embeddings in Supabase PostgreSQL
- Load embeddings from database (instant startup)
- Regenerate only if tools changed (version hash check)
- Fallback to in-memory if database unavailable

SCHEMA:
    CREATE TABLE IF NOT EXISTS ai_infrastructure.tool_embeddings (
        tool_name TEXT PRIMARY KEY,
        embedding vector(384),
        tool_metadata JSONB,
        version_hash TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS ai_infrastructure.tool_embedding_cache (
        cache_key TEXT PRIMARY KEY,
        version_hash TEXT,
        total_tools INTEGER,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

USAGE:
    from tools.persistent_semantic_search import PersistentSemanticToolSearch
    
    search = PersistentSemanticToolSearch(registry)
    # Loads from Supabase if available, regenerates only if tools changed
    
    results = search.search("send email")

AUTHOR: System Integration Architect
DATE: 2026-01-02
"""

import json
import hashlib
import os
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class PersistentSemanticToolSearch:
    """
    Supabase-backed semantic search with intelligent caching.
    
    Initialization Strategy:
    1. Check if embeddings exist in Supabase
    2. Compare version hash (tool registry checksum)
    3. If match: Load from database (instant)
    4. If mismatch: Regenerate and store
    5. Fallback: In-memory only if database unavailable
    """
    
    def __init__(self, registry, force_regenerate: bool = False):
        """
        Initialize semantic search with Supabase persistence.
        
        Args:
            registry: RegistryV3 instance
            force_regenerate: Force regeneration even if cache exists
        """
        self.registry = registry
        self.available = False
        self.model = None
        self.tool_embeddings = {}
        self.tool_metadata = {}
        self.version_hash = None
        self.db_available = False
        
        # Try to initialize with Supabase persistence
        self._initialize_with_persistence(force_regenerate)
    
    def _initialize_with_persistence(self, force_regenerate: bool):
        """Main initialization logic with database fallback"""
        try:
            # Step 1: Load sentence-transformers model
            from sentence_transformers import SentenceTransformer
            # FIX (June 11, 2026): Load from local snapshot path to skip
            # HuggingFace network calls. The previous code used
            # `SentenceTransformer('all-MiniLM-L6-v2')` (load-by-name), which
            # made ~15 HEAD requests on every cold start and caused 60+ s
            # delays → Render 502s. Pattern mirrored from
            # tools/implementations/pgvector/pgvector_tools.py:127 (the fix
            # from commit a62b8f36). Model stays `all-MiniLM-L6-v2` (384 dim)
            # because the tool_embedding_cache table is `vector(384)` —
            # switching models would invalidate the Supabase cache and force
            # a full re-embed of every tool.
            #
            # FIX (July 23, 2026): Use fully-qualified model id
            # `sentence-transformers/all-MiniLM-L6-v2` instead of the bare
            # short name. The hub stores downloaded models at
            # `models--sentence-transformers--all-MiniLM-L6-v2/snapshots/...`,
            # not `models--all-MiniLM-L6-v2/...`. The original lookup built
            # `models--all-MiniLM-L6-v2/snapshots` (from `_safe_name =
            # _model_name.replace('/', '--')`) and never matched the real
            # cache directory, so every init fell through to
            # `SentenceTransformer(_model_name, cache_folder=...)` — which
            # means a fresh HuggingFace download on EVERY chat request,
            # not just on cold start. Symptom: 30-60 s embedding download
            # before every model reply. Mirrors the working pattern in
            # tools/implementations/pgvector/pgvector_tools.py:116 which
            # already uses `BAAI/bge-base-en-v1.5` (fully-qualified).
            _model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            # /data is the Render persistent disk (~10 GB). Falls back to
            # ~/.cache on local dev so unit tests don't require /data to
            # be mounted.
            _cache_dir = '/data/vdb_models' if os.path.isdir('/data') else os.path.join(
                os.path.expanduser('~'), '.cache', 'vdb_models'
            )
            # huggingface_hub stores: models--<safe_name>/snapshots/<hash>/
            # With the fully-qualified name, `_safe_name` becomes
            # `sentence-transformers--all-MiniLM-L6-v2` — matching the real
            # cache directory left by either prior download path.
            _safe_name = _model_name.replace('/', '--')
            _hub_dir = os.path.join(_cache_dir, f'models--{_safe_name}')
            _snap_dir = os.path.join(_hub_dir, 'snapshots')
            _local_path = None
            if os.path.isdir(_snap_dir):
                for _snap in sorted(os.listdir(_snap_dir)):
                    _candidate = os.path.join(_snap_dir, _snap)
                    if os.path.isfile(os.path.join(_candidate, 'config.json')):
                        _local_path = _candidate
                        break
            # Legacy fallback: an instance that previously downloaded via the
            # bare short name still has a working cache under the *correct*
            # directory (because SentenceTransformer auto-prefixed the
            # `sentence-transformers/` namespace before storing). Nothing
            # to migrate here — the path above now matches.
            if _local_path:
                print(
                    f'[SEMANTIC_SEARCH] Loading local embedding model from '
                    f'disk path (no HF network calls) → {_local_path}'
                )
                self.model = SentenceTransformer(_local_path)
            else:
                print(
                    f'[SEMANTIC_SEARCH] Downloading embedding model '
                    f'{_model_name} from HuggingFace (first-time only, '
                    f'~30-60 s) → {_cache_dir}'
                )
                self.model = SentenceTransformer(
                    _model_name, cache_folder=_cache_dir
                )
            self.available = True
            
            # Step 2: Calculate version hash (checksum of all tool definitions)
            self.version_hash = self._calculate_version_hash()
            print(f"[Persistent Semantic] Tool registry version: {self.version_hash[:8]}")
            
            # Step 3: Try to load from Supabase
            if not force_regenerate:
                if self._load_from_supabase():
                    print(f"[Persistent Semantic] ✅ Loaded {len(self.tool_embeddings)} embeddings from Supabase")
                    return
            
            # Step 4: Generate embeddings (cache miss or force regenerate)
            print(f"[Persistent Semantic] 🔄 Generating embeddings for {len(self.registry.tools)} tools...")
            self._generate_embeddings()
            
            # Step 5: Store in Supabase
            if self._store_to_supabase():
                print(f"[Persistent Semantic] 💾 Stored {len(self.tool_embeddings)} embeddings to Supabase")
                self.db_available = True
            else:
                print(f"[Persistent Semantic] ⚠️ Database storage failed, using in-memory only")
            
        except ImportError as e:
            print(f"[Persistent Semantic] ❌ sentence-transformers not installed: {e}")
            self.available = False
        except Exception as e:
            print(f"[Persistent Semantic] ❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.available = False
    
    def _calculate_version_hash(self) -> str:
        """
        Calculate SHA256 hash of all tool definitions.
        Used to detect when tools have changed.
        """
        tool_data = []
        for tool_name in sorted(self.registry.tools.keys()):
            tool = self.registry.tools[tool_name]
            # Include name, description, platform in hash
            tool_data.append(json.dumps({
                'name': tool_name,
                'description': tool.get('description', ''),
                'platform': tool.get('platform', ''),
                'short_description': tool.get('short_description', '')
            }, sort_keys=True))
        
        combined = '||'.join(tool_data)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _load_from_supabase(self) -> bool:
        """
        Load embeddings from Supabase if they exist and are up-to-date.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            from AI_infrastructure.shared.database_utils import execute_query
            
            # Check if cache metadata exists and matches version
            cache_info = execute_query(
                """
                SELECT version_hash, total_tools, created_at
                FROM ai_infrastructure.tool_embedding_cache
                WHERE cache_key = 'semantic_tool_search'
                """,
                fetch_mode='one'
            )
            
            if not cache_info:
                print("[Persistent Semantic] 📭 No cache found in database - will generate fresh embeddings")
                return False
            
            if cache_info['version_hash'] != self.version_hash:
                print(f"[Persistent Semantic] 🔄 Cache outdated - tools have changed!")
                print(f"[Persistent Semantic]    Expected: {self.version_hash[:16]}...")
                print(f"[Persistent Semantic]    Found:    {cache_info['version_hash'][:16]}...")
                print(f"[Persistent Semantic]    🔄 Will regenerate embeddings for {len(self.registry.tools)} tools")
                return False
            
            print(f"[Persistent Semantic] ✅ Cache is VALID! Loading {cache_info['total_tools']} embeddings from Supabase...")
            print(f"[Persistent Semantic]    Version: {cache_info['version_hash'][:16]}...")
            print(f"[Persistent Semantic]    Created: {cache_info['created_at']}")
            
            # Load embeddings
            rows = execute_query(
                """
                SELECT tool_name, embedding, tool_metadata
                FROM ai_infrastructure.tool_embeddings
                WHERE version_hash = %s
                """,
                (self.version_hash,),
                fetch_mode='all'
            )
            
            if not rows:
                print("[Persistent Semantic] No embeddings found")
                return False
            
            # Reconstruct embeddings dictionary
            for row in rows:
                tool_name = row['tool_name']
                # Convert pgvector to numpy array
                embedding_str = row['embedding']
                if isinstance(embedding_str, str):
                    # Parse vector string format: "[0.1,0.2,0.3,...]"
                    embedding_list = json.loads(embedding_str.replace('[', '[').replace(']', ']'))
                    embedding = np.array(embedding_list, dtype=np.float32)
                else:
                    embedding = np.array(embedding_str, dtype=np.float32)
                
                self.tool_embeddings[tool_name] = embedding
                self.tool_metadata[tool_name] = row['tool_metadata']
            
            self.db_available = True
            return True
            
        except Exception as e:
            print(f"[Persistent Semantic] Failed to load from Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_embeddings(self):
        """Generate embeddings for all tools (same as original implementation)"""
        for tool_name, tool_data in self.registry.tools.items():
            # Create rich text representation
            short_desc = tool_data.get('short_description', '')
            long_desc = tool_data.get('description', '')
            platform = tool_data.get('platform', '')
            category = tool_data.get('category', '')
            
            # Combine all text for embedding
            text = f"{tool_name} {short_desc} {long_desc} {platform} {category}"
            
            # Compute embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            self.tool_embeddings[tool_name] = embedding
            self.tool_metadata[tool_name] = {
                'platform': platform if platform else 'unknown',
                'description': long_desc,
                'short_description': short_desc,
                'category': category,
                'is_virtual_tool': tool_data.get('is_virtual_tool', False),
                'query_id': tool_data.get('query_id', None)
            }
    
    def _store_to_supabase(self) -> bool:
        """
        Store embeddings to Supabase.
        
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            from AI_infrastructure.shared.database_utils import execute_query
            
            # Ensure schema exists
            execute_query("""
                CREATE SCHEMA IF NOT EXISTS ai_infrastructure
            """, fetch_mode=None)
            
            # Ensure pgvector extension exists
            execute_query("""
                CREATE EXTENSION IF NOT EXISTS vector
            """, fetch_mode=None)
            
            # Create tables if not exist
            execute_query("""
                CREATE TABLE IF NOT EXISTS ai_infrastructure.tool_embeddings (
                    tool_name TEXT PRIMARY KEY,
                    embedding vector(384),
                    tool_metadata JSONB,
                    version_hash TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """, fetch_mode=None)
            
            execute_query("""
                CREATE TABLE IF NOT EXISTS ai_infrastructure.tool_embedding_cache (
                    cache_key TEXT PRIMARY KEY,
                    version_hash TEXT,
                    total_tools INTEGER,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """, fetch_mode=None)
            
            # Delete old embeddings (if version changed)
            execute_query("""
                DELETE FROM ai_infrastructure.tool_embeddings
                WHERE version_hash != %s
            """, (self.version_hash,), fetch_mode=None)
            
            # Insert embeddings in TRUE batches (much faster - single query per batch)
            from AI_infrastructure.shared.database_utils import get_database_connection
            
            batch_size = 200  # Increased from 100 for better performance
            tool_names = list(self.tool_embeddings.keys())
            total_batches = (len(tool_names) + batch_size - 1) // batch_size
            
            print(f"[Persistent Semantic] Storing {len(tool_names)} embeddings in {total_batches} optimized batches...")
            
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            try:
                for i in range(0, len(tool_names), batch_size):
                    batch = tool_names[i:i+batch_size]
                    
                    # Build batch insert with executemany (10-20x faster)
                    values = []
                    for tool_name in batch:
                        embedding = self.tool_embeddings[tool_name]
                        metadata = self.tool_metadata[tool_name]
                        embedding_list = embedding.tolist()
                        values.append((
                            tool_name,
                            str(embedding_list),
                            json.dumps(metadata),
                            self.version_hash
                        ))
                    
                    # Single query for entire batch
                    cursor.executemany("""
                        INSERT INTO ai_infrastructure.tool_embeddings 
                        (tool_name, embedding, tool_metadata, version_hash, updated_at)
                        VALUES (%s, %s::vector, %s, %s, NOW())
                        ON CONFLICT (tool_name) 
                        DO UPDATE SET 
                            embedding = EXCLUDED.embedding,
                            tool_metadata = EXCLUDED.tool_metadata,
                            version_hash = EXCLUDED.version_hash,
                            updated_at = NOW()
                    """, values)
                    
                    conn.commit()
                    batch_num = i//batch_size + 1
                    print(f"[Persistent Semantic] ⚡ Batch {batch_num}/{total_batches} complete ({len(batch)} tools)")
                
            finally:
                cursor.close()
                conn.close()
            
            # Update cache metadata
            execute_query("""
                INSERT INTO ai_infrastructure.tool_embedding_cache
                (cache_key, version_hash, total_tools, updated_at)
                VALUES ('semantic_tool_search', %s, %s, NOW())
                ON CONFLICT (cache_key)
                DO UPDATE SET
                    version_hash = EXCLUDED.version_hash,
                    total_tools = EXCLUDED.total_tools,
                    updated_at = NOW()
            """, (self.version_hash, len(self.tool_embeddings)), fetch_mode=None)
            
            return True
            
        except Exception as e:
            print(f"[Persistent Semantic] Failed to store to Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search(self, query: str, top_k: int = 20, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search tools using semantic similarity (same API as original).
        
        Args:
            query: Natural language query
            top_k: Maximum results to return
            similarity_threshold: Minimum cosine similarity (0.0-1.0)
        
        Returns:
            List of dicts with tool_name, similarity, platform, description, confidence
        """
        if not self.available:
            return []
        
        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        # Calculate cosine similarity with all tools
        similarities = {}
        for tool_name, tool_embedding in self.tool_embeddings.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, tool_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(tool_embedding)
            )
            
            if similarity >= similarity_threshold:
                similarities[tool_name] = float(similarity)
        
        # Sort by similarity descending
        sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Format results
        results = []
        for tool_name, similarity in sorted_results:
            metadata = self.tool_metadata.get(tool_name, {})
            
            # Determine confidence level
            if similarity >= 0.7:
                confidence = 'high'
            elif similarity >= 0.5:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            results.append({
                'tool_name': tool_name,
                'similarity': similarity,
                'platform': metadata.get('platform', 'unknown'),
                'description': metadata.get('description', ''),
                'short_description': metadata.get('short_description', ''),
                'category': metadata.get('category', ''),
                'confidence': confidence
            })
        
        return results
    
    def invalidate_cache(self):
        """Force cache invalidation (useful after adding new tools)"""
        try:
            from AI_infrastructure.shared.database_utils import execute_query
            
            execute_query("""
                DELETE FROM ai_infrastructure.tool_embedding_cache
                WHERE cache_key = 'semantic_tool_search'
            """, fetch_mode=None)
            
            execute_query("""
                DELETE FROM ai_infrastructure.tool_embeddings
            """, fetch_mode=None)
            
            print("[Persistent Semantic] ✅ Cache invalidated")
            return True
        except Exception as e:
            print(f"[Persistent Semantic] ❌ Cache invalidation failed: {e}")
            return False


# Convenience function for backward compatibility
def get_persistent_semantic_search(registry, force_regenerate: bool = False):
    """
    Get or create persistent semantic search instance.
    
    Args:
        registry: RegistryV3 instance
        force_regenerate: Force regeneration even if cache exists
    
    Returns:
        PersistentSemanticToolSearch instance
    """
    return PersistentSemanticToolSearch(registry, force_regenerate)
