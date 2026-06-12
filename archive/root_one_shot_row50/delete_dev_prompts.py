"""
Delete Development Prompts from Supabase
Date: January 19, 2026

Safe deletion - backup already created in DEVELOPMENT_PROMPTS_BACKUP_JAN19_2026.json
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query

def delete_development_prompts():
    """Delete all development category prompts"""
    print("=" * 80)
    print("DELETING DEVELOPMENT PROMPTS FROM SUPABASE")
    print("=" * 80)
    
    # Get all development prompt IDs
    result = execute_query("""
        SELECT id, name, type
        FROM ai_infrastructure.prompt_library
        WHERE category = 'development'
        ORDER BY type, name
    """, fetch_mode='all')
    
    if not result:
        print("\n❌ No development prompts found to delete")
        return
    
    print(f"\n📋 Found {len(result)} development prompts to delete:")
    for i, row in enumerate(result[:10], 1):
        print(f"   {i}. {row['name']} ({row['type']})")
    if len(result) > 10:
        print(f"   ... and {len(result) - 10} more")
    
    # Delete each prompt
    deleted_count = 0
    for row in result:
        try:
            execute_query("""
                DELETE FROM ai_infrastructure.prompt_library
                WHERE id = %s
            """, (row['id'],), fetch_mode=None)  # DELETE doesn't return results
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete {row['name']}: {e}")
    
    print(f"\n✅ Successfully deleted {deleted_count} prompts")
    
    # Verify deletion
    remaining = execute_query("""
        SELECT COUNT(*) as count
        FROM ai_infrastructure.prompt_library
        WHERE category = 'development'
    """, fetch_mode='one')
    
    print(f"✅ Remaining development prompts: {remaining['count']}")
    
    # Show total remaining
    total = execute_query("""
        SELECT COUNT(*) as count
        FROM ai_infrastructure.prompt_library
    """, fetch_mode='one')
    
    print(f"✅ Total prompts in database: {total['count']}")
    
    print("\n" + "=" * 80)
    print("DELETION COMPLETE")
    print("=" * 80)
    print("\n⚠️  Backup saved in: DEVELOPMENT_PROMPTS_BACKUP_JAN19_2026.json")
    print("   To restore, run: python restore_dev_prompts.py")

if __name__ == '__main__':
    delete_development_prompts()
