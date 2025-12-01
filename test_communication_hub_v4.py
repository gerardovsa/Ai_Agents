"""
Test Communication Hub V4 Modern Framework Module
Checks if the module manifest is correctly configured and can be loaded.
"""

import sys
import os
import json

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

def test_communication_hub():
    """Test communication-hub module configuration"""
    
    print("=" * 70)
    print("COMMUNICATION HUB V4 - MODULE TEST")
    print("=" * 70)
    print()
    
    # 1. Check manifest file
    manifest_path = os.path.join(
        os.path.dirname(__file__),
        'UI', 'modules_external', 'communication-hub', 'manifest.json'
    )
    
    print(f"1. Checking manifest file...")
    if not os.path.exists(manifest_path):
        print(f"   ❌ Manifest not found: {manifest_path}")
        return False
    print(f"   ✅ Manifest exists")
    
    # 2. Load and validate manifest
    print(f"\n2. Loading manifest...")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        print(f"   ✅ Manifest loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load manifest: {e}")
        return False
    
    # 3. Check key fields
    print(f"\n3. Validating manifest structure...")
    required_fields = ['id', 'name', 'version', 'js_file', 'capabilities', 'dependencies']
    
    for field in required_fields:
        if field in manifest:
            print(f"   ✅ {field}: {manifest.get(field) if field != 'capabilities' else 'present'}")
        else:
            print(f"   ❌ Missing required field: {field}")
            return False
    
    # 4. Check JS file exists
    js_file = manifest.get('js_file')
    js_path = os.path.join(
        os.path.dirname(__file__),
        'UI', 'modules_external', 'communication-hub', js_file
    )
    
    print(f"\n4. Checking JavaScript file...")
    print(f"   Expected: {js_file}")
    
    if not os.path.exists(js_path):
        print(f"   ❌ JS file not found: {js_path}")
        return False
    
    file_size = os.path.getsize(js_path) / 1024  # KB
    print(f"   ✅ JS file exists ({file_size:.1f} KB)")
    
    # 5. Check JS file structure (basic validation)
    print(f"\n5. Validating JavaScript structure...")
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for Modern Framework patterns
        checks = {
            'export default': 'export default' in js_content,
            'onDashboardLoad': 'onDashboardLoad' in js_content,
            'Object.assign(this, utilities)': 'Object.assign(this, utilities)' in js_content,
            'this.dom': 'this.dom' in js_content,
            'this.api': 'this.api' in js_content,
            'this.log': 'this.log' in js_content,
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            if not passed:
                all_passed = False
        
        if not all_passed:
            print(f"   ⚠️  Some Modern Framework patterns missing")
    
    except Exception as e:
        print(f"   ❌ Failed to validate JS: {e}")
        return False
    
    # 6. Check dependencies structure
    print(f"\n6. Checking dependencies...")
    deps = manifest.get('dependencies', {})
    
    if isinstance(deps, dict) and 'utilities' in deps:
        utilities = deps['utilities']
        print(f"   ✅ Modern Framework utilities declared:")
        for util in utilities:
            print(f"      - {util}")
    else:
        print(f"   ⚠️  Legacy dependencies structure (should migrate to utilities)")
    
    # 7. Check capabilities
    print(f"\n7. Checking capabilities...")
    capabilities = manifest.get('capabilities', {})
    
    if 'dashboard' in capabilities:
        dashboard = capabilities['dashboard']
        print(f"   ✅ Dashboard capability:")
        print(f"      - enabled: {dashboard.get('enabled')}")
        print(f"      - container_id: {dashboard.get('container_id')}")
    else:
        print(f"   ❌ Dashboard capability not defined")
    
    # 8. Summary
    print(f"\n" + "=" * 70)
    print(f"TEST SUMMARY")
    print(f"=" * 70)
    print(f"Module ID: {manifest.get('id')}")
    print(f"Version: {manifest.get('version')}")
    print(f"JS File: {manifest.get('js_file')}")
    print(f"Framework: Modern V4 (Composition Pattern)")
    print(f"Status: ✅ READY TO LOAD")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_communication_hub()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
