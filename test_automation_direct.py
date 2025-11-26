"""Test automation tools with direct database access"""
import sys
sys.path.insert(0, 'tools/implementations')

# Force reload to bypass cache
import importlib
if 'automation' in sys.modules:
    importlib.reload(sys.modules['automation'])
else:
    import automation

# Test automation_list_workflows
print("Testing automation_list_workflows...")
result = automation.automation_list_workflows(_user_id=14, limit=5)

print(f"\nSUCCESS: Found {result['count']} workflows")
print("\nFirst 5 workflows:")
for i, workflow in enumerate(result['workflows'][:5], 1):
    print(f"{i}. {workflow['title']}")
    print(f"   Slug: {workflow['slug']}")
    print(f"   Status: {workflow['status']}")
    print(f"   Category: {workflow['category']}")
    print()

# Test automation_get_workflow_by_slug
print("\n" + "="*60)
print("Testing automation_get_workflow_by_slug...")
result2 = automation.automation_get_workflow_by_slug(
    slug='morning-email-triage-1763946900',
    _user_id=14
)

print(f"\nSUCCESS: {result2['message']}")
print(f"Title: {result2['workflow']['title']}")
print(f"Status: {result2['workflow']['status']}")
print(f"Actions: {len(result2['workflow']['execution_json'].get('actions', []))}")

print("\n" + "="*60)
print("ALL TESTS PASSED - Direct database access working!")
