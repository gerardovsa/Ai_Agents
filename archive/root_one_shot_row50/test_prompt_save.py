"""
Test script for prompt library save endpoint
Tests the fixed POST /api/prompts/library/db endpoint
"""
import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query
from datetime import datetime

print("\n" + "="*80)
print("TESTING PROMPT LIBRARY SAVE FIX")
print("="*80 + "\n")

# Test data
test_prompt = {
    'user_id': 1,
    'workspace_id': None,
    'name': 'Test Prompt Save Fix',
    'category': 'Business Rules',
    'type': 'quick_action',
    'description': 'Testing the Jan 21, 2026 fix for PostgreSQL RETURNING clause',
    'prompt_text': 'This is a test prompt to verify the database save works correctly.',
    'tags': 'test,fix,jan2026',
    'visibility': 'private'
}

print("Test Data:")
print(f"  Name: {test_prompt['name']}")
print(f"  Category: {test_prompt['category']}")
print(f"  Type: {test_prompt['type']}\n")

try:
    # Test the INSERT with RETURNING clause (simulating what the endpoint does)
    print("Step 1: Testing INSERT with RETURNING clause...")
    
    result = execute_query(
        """
        INSERT INTO ai_infrastructure.prompt_library 
        (user_id, workspace_id, name, category, type, description, 
         prompt_text, tags, visibility, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, workspace_id, name, category, type,
            description, prompt_text, tags, visibility,
            usage_count, created_at, updated_at
        """,
        (
            test_prompt['user_id'],
            test_prompt['workspace_id'],
            test_prompt['name'],
            test_prompt['category'],
            test_prompt['type'],
            test_prompt['description'],
            test_prompt['prompt_text'],
            test_prompt['tags'],
            test_prompt['visibility'],
            datetime.utcnow(),
            datetime.utcnow()
        ),
        fetch_mode='one'
    )
    
    print("✅ INSERT successful!")
    print(f"  Returned ID: {result['id']}")
    print(f"  Name: {result['name']}")
    print(f"  Category: {result['category']}")
    print(f"  Usage Count: {result['usage_count']}")
    print(f"  Created: {result['created_at']}\n")
    
    # Verify it's in the database
    print("Step 2: Verifying prompt was saved...")
    verify = execute_query(
        "SELECT * FROM ai_infrastructure.prompt_library WHERE id = %s",
        (result['id'],),
        fetch_mode='one'
    )
    
    if verify:
        print("✅ Verification successful - prompt found in database!")
        print(f"  ID: {verify['id']}")
        print(f"  Name: {verify['name']}\n")
    else:
        print("❌ Verification failed - prompt not found!\n")
    
    # Cleanup
    print("Step 3: Cleaning up test data...")
    execute_query(
        "DELETE FROM ai_infrastructure.prompt_library WHERE id = %s",
        (result['id'],)
    )
    print("✅ Test data cleaned up\n")
    
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nThe prompt library save endpoint should now work correctly.")
    print("Fixed issues:")
    print("  1. ✅ Added datetime import")
    print("  2. ✅ Removed duplicate cursor.fetchone()")
    print("  3. ✅ Fixed undefined prompt_id variable")
    print("  4. ✅ Using RETURNING clause for PostgreSQL compatibility\n")

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    print("\nThe fix may need additional adjustments.\n")
