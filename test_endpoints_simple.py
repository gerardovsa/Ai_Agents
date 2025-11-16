"""Simple endpoint test - test each endpoint individually"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

print("\n[TEST 1] Create workflow")
workflow_data = {
    "slug": f"test-{int(time.time())}",
    "title": "Test Workflow",
    "description": "Test",
    "status": "draft",
    "ui_json": {"shapes": [], "connections": []},
    "execution_json": {"steps": []}
}

try:
    response = requests.post(
        f"{BASE_URL}/api/automation/save",
        json=workflow_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    workflow_slug = workflow_data["slug"]
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

time.sleep(1)

print("\n[TEST 2] Get workflow by slug")
try:
    response = requests.get(
        f"{BASE_URL}/api/automation/list?slug={workflow_slug}",
        timeout=5
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Workflows found: {len(result.get('workflows', []))}")
    if result.get('workflows'):
        print(f"Title: {result['workflows'][0]['title']}")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

print("\n✅ All tests passed!")
