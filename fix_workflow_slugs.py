"""
Fix Workflow Slugs - Replace Title-Based Slugs with True Unique IDs
====================================================================
Generates proper unique slugs in format: wf_<random>_<timestamp>
"""

import requests
import json
import time
import random
import string

API_BASE_URL = "http://localhost:5001"

def generate_unique_slug():
    """Generate TRUE unique slug (not title-based)"""
    timestamp = int(time.time())
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"wf_{random_part}_{timestamp}"

def get_all_workflows():
    """Fetch all workflows from API"""
    response = requests.get(
        f"{API_BASE_URL}/api/automation/list",
        headers={'Authorization': 'Bearer test'}
    )
    if response.status_code == 200:
        return response.json().get('workflows', [])
    return []

def update_workflow_slug(old_slug, new_slug, workflow_data):
    """Update workflow with new unique slug"""
    # Delete old workflow
    delete_response = requests.delete(
        f"{API_BASE_URL}/api/automation/{old_slug}",
        headers={'Authorization': 'Bearer test'}
    )
    
    # Create with new slug
    workflow_data['slug'] = new_slug
    save_response = requests.post(
        f"{API_BASE_URL}/api/automation/save",
        json=workflow_data,
        headers={
            'Authorization': 'Bearer test',
            'Content-Type': 'application/json'
        }
    )
    
    return save_response.status_code == 201

print("="*80)
print("FIXING WORKFLOW SLUGS - Converting to True Unique Identifiers")
print("="*80)
print()

# Get all workflows
workflows = get_all_workflows()
print(f"Found {len(workflows)} workflows\n")

# Track changes
slug_mapping = {}
updated_count = 0
failed_count = 0

for workflow in workflows:
    old_slug = workflow.get('slug', '')
    title = workflow.get('title', 'Untitled')
    
    # Check if slug is title-based (contains hyphens/underscores but no random component)
    if old_slug and not old_slug.startswith('wf_'):
        new_slug = generate_unique_slug()
        
        print(f"Title: {title}")
        print(f"  Old Slug (title-based): {old_slug}")
        print(f"  New Slug (unique):      {new_slug}")
        
        # Update workflow
        try:
            success = update_workflow_slug(old_slug, new_slug, workflow)
            if success:
                slug_mapping[old_slug] = new_slug
                updated_count += 1
                print(f"  Status: ✅ Updated successfully")
            else:
                failed_count += 1
                print(f"  Status: ❌ Update failed")
        except Exception as e:
            failed_count += 1
            print(f"  Status: ❌ Error: {str(e)}")
        
        print()
        time.sleep(0.1)  # Small delay to avoid rate limiting
    else:
        print(f"Title: {title}")
        print(f"  Slug: {old_slug}")
        print(f"  Status: ⏭️  Already has unique slug")
        print()

print("="*80)
print("SLUG MIGRATION SUMMARY")
print("="*80)
print(f"Total Workflows: {len(workflows)}")
print(f"Updated: {updated_count}")
print(f"Failed: {failed_count}")
print(f"Unchanged: {len(workflows) - updated_count - failed_count}")
print()

if slug_mapping:
    print("SLUG MAPPING (OLD → NEW):")
    print("-"*80)
    for old, new in slug_mapping.items():
        print(f"  {old}")
        print(f"  → {new}")
        print()

print("✅ Slug migration complete!")
print()
print("IMPORTANT NOTES:")
print("- Old slugs are NO LONGER VALID")
print("- All API calls must use NEW unique slugs")
print("- Slugs are now IMMUTABLE (won't change if title changes)")
print("- Format: wf_<8-random-chars>_<timestamp>")
print("- Example: wf_a3f8b2c1_1732029847")
