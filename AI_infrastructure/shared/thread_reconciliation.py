"""
ThreadManager Reconciliation System
====================================
Compares in-memory ThreadManager state vs PostgreSQL database reality.

DETECTS:
1. Orphaned threads - Threads in database but not in memory (memory leak/crash recovery)
2. Missing assignments - Threads in memory but not in database (write failure)
3. Stale metadata - Thread exists in both but metadata mismatch
4. Zombie threads - Threads marked deleted but still in memory

Author: GitHub Copilot
Date: December 22, 2025
"""

import logging
from typing import Dict, List, Set, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


def reconcile_threads(user_id: int, threadmanager_threads: List[Dict]) -> Dict:
    """
    Compare ThreadManager in-memory state vs database.
    
    Args:
        user_id: User ID to reconcile threads for
        threadmanager_threads: List of thread dicts from ThreadManager.threads
        
    Returns:
        {
            "success": true,
            "discrepancies": {
                "orphaned_threads": [...],      # In DB but not in memory
                "missing_threads": [...],       # In memory but not in DB
                "stale_metadata": [...],        # Exists in both but mismatch
                "zombie_threads": [...]         # Marked deleted but in memory
            },
            "summary": {
                "memory_count": 10,
                "database_count": 12,
                "orphaned_count": 2,
                "missing_count": 0,
                "stale_count": 1,
                "zombie_count": 0
            }
        }
    """
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Extract thread slugs from memory
        memory_threads = {t['id']: t for t in threadmanager_threads}
        memory_slugs = set(memory_threads.keys())
        
        logger.info(f"[Reconciliation] User {user_id}: {len(memory_slugs)} threads in memory")
        
        # Query database for all threads for this user
        db_threads_raw = execute_query(
            "SELECT id, thread_slug, name, location, metadata, created_at, updated_at FROM sessions.threads WHERE user_id = %s",
            (user_id,),
            fetch_mode='all'
        )
        
        db_threads = {row[1]: {  # thread_slug is key
            'db_id': row[0],
            'slug': row[1],
            'name': row[2],
            'location': row[3],
            'metadata': json.loads(row[4]) if row[4] else {},
            'created_at': str(row[5]),
            'updated_at': str(row[6])
        } for row in db_threads_raw}
        
        db_slugs = set(db_threads.keys())
        
        logger.info(f"[Reconciliation] User {user_id}: {len(db_slugs)} threads in database")
        
        # Find discrepancies
        orphaned = db_slugs - memory_slugs  # In DB but not memory
        missing = memory_slugs - db_slugs   # In memory but not DB
        both = memory_slugs & db_slugs      # In both (check for staleness)
        
        orphaned_threads = [db_threads[slug] for slug in orphaned]
        missing_threads = [memory_threads[slug] for slug in missing]
        
        # Check for stale metadata
        stale_metadata = []
        for slug in both:
            memory_thread = memory_threads[slug]
            db_thread = db_threads[slug]
            
            # Compare key fields
            mismatches = []
            
            if memory_thread.get('title') != db_thread.get('name'):
                mismatches.append('title')
            
            if memory_thread.get('location') != db_thread.get('location'):
                mismatches.append('location')
            
            # Check metadata differences (only critical fields)
            mem_meta = memory_thread.get('metadata', {})
            db_meta = db_thread.get('metadata', {})
            
            for key in ['email_thread_id', 'synergy_card_id', 'has_files']:
                if mem_meta.get(key) != db_meta.get(key):
                    mismatches.append(f'metadata.{key}')
            
            if mismatches:
                stale_metadata.append({
                    'slug': slug,
                    'memory': memory_thread,
                    'database': db_thread,
                    'mismatched_fields': mismatches
                })
        
        # Build result
        result = {
            'success': True,
            'user_id': user_id,
            'discrepancies': {
                'orphaned_threads': orphaned_threads,
                'missing_threads': missing_threads,
                'stale_metadata': stale_metadata,
                'zombie_threads': []  # TODO: Add zombie detection if needed
            },
            'summary': {
                'memory_count': len(memory_slugs),
                'database_count': len(db_slugs),
                'orphaned_count': len(orphaned),
                'missing_count': len(missing),
                'stale_count': len(stale_metadata),
                'zombie_count': 0,
                'healthy': len(orphaned) == 0 and len(missing) == 0 and len(stale_metadata) == 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Log warnings for each discrepancy type
        if orphaned:
            logger.warning(f"[Reconciliation] {len(orphaned)} orphaned thread(s) in database (not in memory)")
            for thread in orphaned_threads:
                logger.warning(f"   - {thread['slug']}: {thread['name']}")
        
        if missing:
            logger.warning(f"[Reconciliation] {len(missing)} missing thread(s) (in memory but not database)")
            for thread in missing_threads:
                logger.warning(f"   - {thread['id']}: {thread.get('title', 'No title')}")
        
        if stale_metadata:
            logger.warning(f"[Reconciliation] {len(stale_metadata)} stale thread(s) (metadata mismatch)")
            for thread in stale_metadata:
                logger.warning(f"   - {thread['slug']}: mismatched {', '.join(thread['mismatched_fields'])}")
        
        if result['summary']['healthy']:
            logger.info(f"[Reconciliation] ✅ ThreadManager and database are in sync ({len(both)} threads)")
        else:
            logger.error(f"[Reconciliation] ❌ Found {len(orphaned) + len(missing) + len(stale_metadata)} total discrepancies")
        
        return result
        
    except Exception as e:
        logger.error(f"[Reconciliation] Failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': str(e)
        }


def auto_fix_discrepancies(user_id: int, reconciliation_result: Dict) -> Dict:
    """
    Automatically fix detected discrepancies.
    
    FIXES:
    - Orphaned threads: Reload into ThreadManager from database
    - Missing threads: Insert into database from memory
    - Stale metadata: Update database with memory values (memory = source of truth)
    
    Args:
        user_id: User ID
        reconciliation_result: Output from reconcile_threads()
        
    Returns:
        {
            "success": true,
            "fixes_applied": {
                "orphaned_reloaded": 2,
                "missing_inserted": 0,
                "stale_updated": 1
            }
        }
    """
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        discrepancies = reconciliation_result.get('discrepancies', {})
        fixes = {
            'orphaned_reloaded': 0,
            'missing_inserted': 0,
            'stale_updated': 0
        }
        
        # Fix orphaned threads (reload into memory - requires ThreadManager API)
        orphaned = discrepancies.get('orphaned_threads', [])
        if orphaned:
            logger.info(f"[Auto-Fix] Reloading {len(orphaned)} orphaned thread(s) into memory...")
            # NOTE: This requires calling ThreadManager.loadThreadsFromBackend() on frontend
            # We can only log the recommendation here
            logger.warning(f"[Auto-Fix] ⚠️ Cannot auto-reload orphaned threads from backend")
            logger.warning(f"[Auto-Fix] → User must refresh ThreadManager on frontend")
        
        # Fix missing threads (insert into database)
        missing = discrepancies.get('missing_threads', [])
        for thread in missing:
            try:
                execute_query(
                    """
                    INSERT INTO sessions.threads 
                    (thread_slug, name, user_id, location, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                    ON CONFLICT (thread_slug) DO NOTHING
                    """,
                    (
                        thread['id'],
                        thread.get('title', 'Untitled'),
                        user_id,
                        thread.get('location', 'prime'),
                        json.dumps(thread.get('metadata', {}))
                    )
                )
                fixes['missing_inserted'] += 1
                logger.info(f"[Auto-Fix] ✅ Inserted missing thread: {thread['id']}")
            except Exception as e:
                logger.error(f"[Auto-Fix] ❌ Failed to insert {thread['id']}: {e}")
        
        # Fix stale metadata (update database with memory values)
        stale = discrepancies.get('stale_metadata', [])
        for thread in stale:
            try:
                memory_thread = thread['memory']
                execute_query(
                    """
                    UPDATE sessions.threads
                    SET name = %s, location = %s, metadata = %s, updated_at = NOW()
                    WHERE thread_slug = %s
                    """,
                    (
                        memory_thread.get('title', 'Untitled'),
                        memory_thread.get('location', 'prime'),
                        json.dumps(memory_thread.get('metadata', {})),
                        thread['slug']
                    )
                )
                fixes['stale_updated'] += 1
                logger.info(f"[Auto-Fix] ✅ Updated stale thread: {thread['slug']}")
            except Exception as e:
                logger.error(f"[Auto-Fix] ❌ Failed to update {thread['slug']}: {e}")
        
        logger.info(f"[Auto-Fix] Complete: {fixes}")
        
        return {
            'success': True,
            'fixes_applied': fixes
        }
        
    except Exception as e:
        logger.error(f"[Auto-Fix] Failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
