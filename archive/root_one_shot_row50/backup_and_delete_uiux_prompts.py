"""
Backup and Delete UI/UX Prompts from Supabase
Date: January 19, 2026
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query

def backup_and_delete_uiux_prompts():
    """Backup and delete UI/UX related prompts"""
    print("=" * 80)
    print("BACKUP & DELETE UI/UX PROMPTS")
    print("=" * 80)
    
    # Find UI/UX prompts
    result = execute_query("""
        SELECT 
            id, user_id, workspace_id, name, category, type,
            description, prompt_text, tags, visibility,
            usage_count, created_at, updated_at
        FROM ai_infrastructure.prompt_library
        WHERE name LIKE %s OR name LIKE %s OR category = %s
        ORDER BY name
    """, ('%UI%', '%UX%', 'creative'), fetch_mode='all')
    
    if not result:
        print("\n❌ No UI/UX prompts found")
        return
    
    print(f"\n📋 Found {len(result)} UI/UX related prompts:")
    for i, row in enumerate(result, 1):
        print(f"   {i}. {row['name']} ({row['category']}, {row['type']})")
    
    # Save backup
    backup_file = Path(__file__).parent / 'UI_UX_PROMPTS_BACKUP_JAN19_2026.json'
    
    backup_data = {
        'export_date': '2026-01-19',
        'total_prompts': len(result),
        'prompts': result
    }
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n✅ Saved to: {backup_file}")
    print(f"   File size: {backup_file.stat().st_size / 1024:.1f} KB")
    
    # Delete prompts
    print(f"\n🗑️  Deleting {len(result)} prompts from database...")
    
    deleted_count = 0
    for row in result:
        try:
            execute_query("""
                DELETE FROM ai_infrastructure.prompt_library
                WHERE id = %s
            """, (row['id'],), fetch_mode=None)
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete {row['name']}: {e}")
    
    print(f"\n✅ Successfully deleted {deleted_count} prompts")
    
    # Verify
    remaining = execute_query("""
        SELECT COUNT(*) as count
        FROM ai_infrastructure.prompt_library
        WHERE name LIKE %s OR name LIKE %s OR category = %s
    """, ('%UI%', '%UX%', 'creative'), fetch_mode='one')
    
    total = execute_query("""
        SELECT COUNT(*) as count
        FROM ai_infrastructure.prompt_library
    """, fetch_mode='one')
    
    print(f"✅ Remaining UI/UX prompts: {remaining['count']}")
    print(f"✅ Total prompts in database: {total['count']}")
    
    print("\n" + "=" * 80)
    print("COMPLETED")
    print("=" * 80)

if __name__ == '__main__':
    backup_and_delete_uiux_prompts()
