"""
Test InHouse Kanban module routes
"""

import requests
import json

BASE_URL = "http://localhost:5001"

print("Testing InHouse Kanban Module Routes")
print("=" * 60)

# Test 1: Module list
print("\n1. Testing /api/modules/list...")
response = requests.get(f"{BASE_URL}/api/modules/list")
print(f"   Status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"   Modules: {data.get('count', 0)}")
    modules = data.get('modules', [])
    kanban = next((m for m in modules if m['id'] == 'inhouse-kanban'), None)
    if kanban:
        print(f"   ✅ InHouse Kanban found:")
        print(f"      - scriptPath: {kanban.get('scriptPath', 'MISSING')}")
        print(f"      - stylePath: {kanban.get('stylePath', 'MISSING')}")
        print(f"      - htmlPath: {kanban.get('htmlPath', 'MISSING')}")
    else:
        print("   ❌ InHouse Kanban NOT found in module list")

# Test 2: JS route
print("\n2. Testing /api/modules/inhouse-kanban/js...")
response = requests.get(f"{BASE_URL}/api/modules/inhouse-kanban/js")
print(f"   Status: {response.status_code}")
if response.ok:
    content = response.text
    print(f"   Size: {len(content)} bytes")
    if "window.ModuleRegistry" in content:
        print("   ✅ window.ModuleRegistry found")
    else:
        print("   ❌ window.ModuleRegistry NOT found")
    if "class InhouseKanbanModule" in content:
        print("   ✅ InhouseKanbanModule class found")
    else:
        print("   ❌ InhouseKanbanModule class NOT found")
else:
    print(f"   ❌ Error: {response.text[:200]}")

# Test 3: CSS route
print("\n3. Testing /api/modules/inhouse-kanban/css...")
response = requests.get(f"{BASE_URL}/api/modules/inhouse-kanban/css")
print(f"   Status: {response.status_code}")
if response.ok:
    content = response.text
    print(f"   Size: {len(content)} bytes")
    if ".kanban" in content:
        print("   ✅ Kanban CSS rules found")
    else:
        print("   ⚠️  No Kanban-specific CSS found")

# Test 4: HTML route
print("\n4. Testing /api/modules/inhouse-kanban/html...")
response = requests.get(f"{BASE_URL}/api/modules/inhouse-kanban/html")
print(f"   Status: {response.status_code}")
if response.ok:
    content = response.text
    print(f"   Size: {len(content)} bytes")
    if "inhouse-kanban-sidebar" in content:
        print("   ✅ Sidebar HTML found")
    else:
        print("   ❌ Sidebar HTML NOT found")

print("\n" + "=" * 60)
print("Test complete!")
