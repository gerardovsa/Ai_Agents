"""
Test script for document count optimization
Tests the SQL COUNT(*) optimization in synergy_routes.py
"""
import sys
import os

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

def test_document_count():
    """Test the document count optimization"""
    print("\n" + "="*80)
    print("TESTING DOCUMENT COUNT OPTIMIZATION")
    print("="*80 + "\n")
    
    try:
        # Test 1: Get synergy sessions count
        print("Test 1: Getting synergy sessions...")
        sessions = execute_query(
            "SELECT session_id, title FROM synergy_sessions.synergy_sessions LIMIT 5",
            fetch_mode='all'
        )
        print(f"✅ Found {len(sessions)} sessions")
        
        if not sessions:
            print("⚠️  No sessions found - cannot test document counts")
            return
        
        # Test 2: Old method - load all docs then count
        session_ids = [s['session_id'] for s in sessions]
        placeholders = ','.join('%s' for _ in session_ids)
        
        print(f"\nTest 2: Old method (load all documents then count)...")
        old_query = f"""
            SELECT session_id, doc_id, title
            FROM synergy_sessions.synergy_internal_docs
            WHERE session_id IN ({placeholders})
        """
        docs = execute_query(old_query, tuple(session_ids), fetch_mode='all')
        
        # Count by session (old way)
        old_counts = {}
        for doc in docs:
            sess_id = doc['session_id']
            old_counts[sess_id] = old_counts.get(sess_id, 0) + 1
        
        print(f"✅ Loaded {len(docs)} documents, counted per session")
        
        # Test 3: New method - SQL COUNT(*)
        print(f"\nTest 3: New method (SQL COUNT(*) aggregation)...")
        new_query = f"""
            SELECT session_id, COUNT(*) as count
            FROM synergy_sessions.synergy_internal_docs
            WHERE session_id IN ({placeholders})
            GROUP BY session_id
        """
        count_rows = execute_query(new_query, tuple(session_ids), fetch_mode='all')
        
        new_counts = {row['session_id']: row['count'] for row in count_rows}
        print(f"✅ Got counts for {len(new_counts)} sessions")
        
        # Test 4: Compare results
        print(f"\nTest 4: Comparing methods...")
        print("\n{:<40} {:<15} {:<15} {:<10}".format(
            "Session ID", "Old Method", "New Method", "Match?"
        ))
        print("-" * 80)
        
        all_match = True
        for sess_id in session_ids:
            old_count = old_counts.get(sess_id, 0)
            new_count = new_counts.get(sess_id, 0)
            match = "✅" if old_count == new_count else "❌"
            
            if old_count != new_count:
                all_match = False
            
            print("{:<40} {:<15} {:<15} {:<10}".format(
                sess_id[:36] + "...",
                old_count,
                new_count,
                match
            ))
        
        # Test 5: Performance comparison (rough estimate)
        print(f"\nTest 5: Data transfer comparison...")
        old_data_size = len(docs) * 3  # Approximate: 3 fields per doc
        new_data_size = len(count_rows) * 2  # Only session_id + count
        savings = ((old_data_size - new_data_size) / old_data_size * 100) if old_data_size > 0 else 0
        
        print(f"Old method: {len(docs)} rows × 3 fields = {old_data_size} data points")
        print(f"New method: {len(count_rows)} rows × 2 fields = {new_data_size} data points")
        print(f"Data reduction: {savings:.1f}%")
        
        # Final verdict
        print("\n" + "="*80)
        if all_match:
            print("✅ SUCCESS: Both methods produce identical results")
            print(f"✅ OPTIMIZATION: {savings:.1f}% reduction in data transfer")
        else:
            print("❌ FAILURE: Methods produce different results")
        print("="*80 + "\n")
        
        return all_match
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_document_count()
    sys.exit(0 if success else 1)
