"""
Debug script to test ModuleRegistry initialization
"""
import sys
import os
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

print("=" * 60)
print("MODULE REGISTRY DEBUG TEST")
print("=" * 60)

# Test 1: Check if modules directory exists
modules_dir = Path(__file__).parent / 'frontend' / 'modules'
print(f"\n1. Modules Directory Check:")
print(f"   Path: {modules_dir}")
print(f"   Exists: {modules_dir.exists()}")

if modules_dir.exists():
    module_dirs = [d for d in modules_dir.iterdir() if d.is_dir()]
    print(f"   Subdirectories: {len(module_dirs)}")
    for mod_dir in module_dirs:
        manifest_path = mod_dir / 'manifest.json'
        has_manifest = manifest_path.exists()
        print(f"     - {mod_dir.name}: manifest.json {'✓' if has_manifest else '✗'}")
        
        if has_manifest:
            try:
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                print(f"        ID: {manifest_data.get('id', 'MISSING')}")
                print(f"        Name: {manifest_data.get('name', 'MISSING')}")
                print(f"        Version: {manifest_data.get('version', 'MISSING')}")
            except Exception as e:
                print(f"        ERROR reading manifest: {e}")

# Test 2: Import and initialize ModuleRegistry
print(f"\n2. ModuleRegistry Import Test:")
try:
    from core.module_registry import get_module_registry
    print("   ✓ Successfully imported get_module_registry")
    
    registry = get_module_registry()
    print("   ✓ Got registry singleton instance")
    
    print(f"\n3. Registry Initialization Test:")
    print(f"   Initializing with path: {modules_dir}")
    registry.initialize(str(modules_dir))
    
    print(f"\n4. Registry Results:")
    print(f"   Total modules: {len(registry.modules)}")
    print(f"   Module IDs: {list(registry.modules.keys())}")
    
    if 'inhouse-kanban' in registry.modules:
        print(f"\n5. InHouse Kanban Module Details:")
        module = registry.modules['inhouse-kanban']
        print(f"   Name: {module.name}")
        print(f"   Version: {module.version}")
        print(f"   Description: {module.description}")
        print(f"   Icon: {module.icon}")
        print(f"   HTML File: {module.html_file}")
        print(f"   JS File: {module.js_file}")
        print(f"   CSS File: {module.css_file}")
        print(f"   Required Platforms: {module.required_platforms}")
        print(f"   Optional Platforms: {module.optional_platforms}")
        print(f"   Module Path: {module.module_path}")
    else:
        print(f"\n5. InHouse Kanban Module NOT FOUND")
        print(f"   Registry has these modules: {list(registry.modules.keys())}")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DEBUG TEST COMPLETE")
print("=" * 60)
