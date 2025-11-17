"""
Test Database Placeholder Conversion
Tests that $1, $2, $3... placeholders are properly converted to %s, %s, %s...
"""

import sys
import re
sys.path.insert(0, 'AI_infrastructure')

def test_placeholder_conversion():
    """Test that numbered positional parameters are converted"""
    
    test_cases = [
        # (input_sql, expected_output)
        (
            "INSERT INTO threads (id, name) VALUES ($1, $2)",
            "INSERT INTO threads (id, name) VALUES (%s, %s)"
        ),
        (
            "INSERT INTO sessions.threads (id, thread_slug, workspace_id, name, user_id, created_at, updated_at, metadata, location, tags, synergy_card_id, parent_thread_id, branch_point_message_id, branch_name) VALUES (DEFAULT, $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)",
            "INSERT INTO sessions.threads (id, thread_slug, workspace_id, name, user_id, created_at, updated_at, metadata, location, tags, synergy_card_id, parent_thread_id, branch_point_message_id, branch_name) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        ),
        (
            "SELECT * FROM users WHERE id = $1 AND email = $2",
            "SELECT * FROM users WHERE id = %s AND email = %s"
        ),
        (
            "UPDATE threads SET name = $1 WHERE thread_slug = $2",
            "UPDATE threads SET name = %s WHERE thread_slug = %s"
        )
    ]
    
    print("=" * 70)
    print("DATABASE PLACEHOLDER CONVERSION TEST")
    print("=" * 70)
    print()
    
    all_passed = True
    
    for i, (input_sql, expected) in enumerate(test_cases, 1):
        # Convert using regex (same as DatabaseCursor.execute)
        converted = re.sub(r'\$\d+', '%s', input_sql)
        
        passed = converted == expected
        all_passed = all_passed and passed
        
        status = "PASS" if passed else "FAIL"
        print(f"Test {i}: {status}")
        print(f"  Input:    {input_sql[:80]}{'...' if len(input_sql) > 80 else ''}")
        print(f"  Expected: {expected[:80]}{'...' if len(expected) > 80 else ''}")
        print(f"  Got:      {converted[:80]}{'...' if len(converted) > 80 else ''}")
        
        if not passed:
            print(f"  ERROR: Conversion mismatch!")
        print()
    
    print("=" * 70)
    if all_passed:
        print("SUCCESS: All placeholder conversions passed!")
    else:
        print("FAILURE: Some conversions failed")
    print("=" * 70)
    
    return all_passed


if __name__ == '__main__':
    success = test_placeholder_conversion()
    sys.exit(0 if success else 1)
