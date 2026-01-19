"""
Export and Delete Development Prompts from Supabase
Date: January 19, 2026

This script:
1. Exports all development category prompts to JSON backup
2. Optionally deletes them from Supabase database
"""

import sys
import json
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query

def export_development_prompts():
    """Export all development category prompts to JSON backup"""
    print("=" * 80)
    print("EXPORTING DEVELOPMENT PROMPTS")
    print("=" * 80)
    
    # Fetch all development prompts
    result = execute_query("""
        SELECT 
            id, user_id, workspace_id, name, category, type,
            description, prompt_text, tags, visibility,
            usage_count, created_at, updated_at
        FROM ai_infrastructure.prompt_library
        WHERE category = 'development'
        ORDER BY type, name
    """, fetch_mode='all')
    
    print(f"\n✅ Found {len(result)} development prompts")
    
    # Group by type
    quick_actions = [p for p in result if p['type'] == 'quick_action']
    full_prompts = [p for p in result if p['type'] == 'full_prompt']
    
    print(f"   - {len(quick_actions)} quick actions")
    print(f"   - {len(full_prompts)} full prompts")
    
    # Save to JSON file
    backup_file = Path(__file__).parent / 'DEVELOPMENT_PROMPTS_BACKUP_JAN19_2026.json'
    
    backup_data = {
        'export_date': '2026-01-19',
        'total_prompts': len(result),
        'quick_actions_count': len(quick_actions),
        'full_prompts_count': len(full_prompts),
        'prompts': result
    }
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n✅ Saved to: {backup_file}")
    print(f"   File size: {backup_file.stat().st_size / 1024:.1f} KB")
    
    # Print sample prompts
    print("\n📋 Sample Prompts:")
    for i, prompt in enumerate(result[:5], 1):
        print(f"\n{i}. {prompt['name']} ({prompt['type']})")
        print(f"   ID: {prompt['id']}")
        print(f"   Preview: {prompt['prompt_text'][:80]}...")
    
    return result

def delete_development_prompts(prompt_ids):
    """Delete development prompts from database"""
    print("\n" + "=" * 80)
    print("DELETING DEVELOPMENT PROMPTS FROM SUPABASE")
    print("=" * 80)
    
    if not prompt_ids:
        print("❌ No prompts to delete")
        return
    
    print(f"\n⚠️  About to delete {len(prompt_ids)} prompts")
    print(f"   IDs: {prompt_ids[:10]}{'...' if len(prompt_ids) > 10 else ''}")
    
    # Confirm deletion
    response = input("\n⚠️  Type 'DELETE' to confirm deletion: ")
    if response != 'DELETE':
        print("❌ Deletion cancelled")
        return
    
    # Delete prompts
    for prompt_id in prompt_ids:
        execute_query("""
            DELETE FROM ai_infrastructure.prompt_library
            WHERE id = %s
        """, (prompt_id,))
    
    print(f"\n✅ Deleted {len(prompt_ids)} prompts from database")
    
    # Verify deletion
    remaining = execute_query("""
        SELECT COUNT(*) as count
        FROM ai_infrastructure.prompt_library
        WHERE category = 'development'
    """, fetch_mode='one')
    
    print(f"✅ Remaining development prompts: {remaining['count']}")

def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("DEVELOPMENT PROMPTS BACKUP & DELETE UTILITY")
    print("=" * 80)
    
    # Export prompts
    prompts = export_development_prompts()
    
    # Ask if user wants to delete
    print("\n" + "=" * 80)
    print("DELETE PROMPTS FROM DATABASE?")
    print("=" * 80)
    print("\nThe prompts have been safely backed up to:")
    print("  DEVELOPMENT_PROMPTS_BACKUP_JAN19_2026.json")
    print("\nDo you want to delete them from Supabase? (y/n): ", end='')
    
    response = input().lower()
    if response == 'y':
        prompt_ids = [p['id'] for p in prompts]
        delete_development_prompts(prompt_ids)
    else:
        print("\n✅ Prompts kept in database (backup created)")
    
    print("\n" + "=" * 80)
    print("COMPLETED")
    print("=" * 80)

if __name__ == '__main__':
    main()
