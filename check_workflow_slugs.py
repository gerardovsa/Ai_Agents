"""Check actual workflow slug structure from API"""
import requests
import json

response = requests.get(
    'http://localhost:5001/api/automation/list',
    headers={'Authorization': 'Bearer test'}
)

print(f"Status Code: {response.status_code}")
data = response.json()

workflows = data.get('workflows', [])
print(f"\nTotal Workflows: {len(workflows)}\n")

for workflow in workflows:
    print(f"Title: {workflow.get('title')}")
    print(f"  Slug: {workflow.get('slug')}")
    print(f"  automation_id: {workflow.get('automation_id')}")
    print(f"  id: {workflow.get('id')}")
    print()

# Show full structure of first workflow
if workflows:
    print("\n" + "="*80)
    print("FIRST WORKFLOW FULL STRUCTURE:")
    print("="*80)
    print(json.dumps(workflows[0], indent=2, default=str))
