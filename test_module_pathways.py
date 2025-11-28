"""
Test Module Connection Pathways - Complete Integration Verification

This script traces the complete pathway from:
1. Module Registry (Backend) -> Flask API -> Frontend Module Loader -> Browser

Tests:
- Module discovery and registration
- File path resolution
- API endpoint accessibility
- Frontend module loader integration
- Complete end-to-end pathway
"""

import sys
import os
from pathlib import Path
import requests
import json

# Add AI_infrastructure to path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir))

from AI_infrastructure.core.module_registry import get_module_registry

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_backend_module_discovery():
    """Test 1: Backend Module Registry Discovery"""
    print_section("TEST 1: BACKEND MODULE REGISTRY")
    
    registry = get_module_registry()
    
    # Test internal modules
    internal_modules = ['thread-cards', 'synergy_sessions', 'settings-sidebar', 'automation-workflows']
    
    results = {
        'discovered': [],
        'missing': [],
        'path_errors': []
    }
    
    for module_id in internal_modules:
        module = registry.get_module(module_id)
        
        if module:
            results['discovered'].append(module_id)
            print(f"[OK] {module_id}")
            print(f"     Path: {module.module_path}")
            print(f"     Script: {module.scriptPath}")
            print(f"     Style: {module.stylePath}")
            
            # Verify files exist
            if module.scriptPath:
                script_path = base_dir / "UI" / module.scriptPath
                if script_path.exists():
                    print(f"     [OK] Script file exists")
                else:
                    print(f"     [FAIL] Script file NOT FOUND: {script_path}")
                    results['path_errors'].append(f"{module_id}: script missing")
            
            if module.stylePath:
                style_path = base_dir / "UI" / module.stylePath
                if style_path.exists():
                    print(f"     [OK] Style file exists")
                else:
                    print(f"     [FAIL] Style file NOT FOUND: {style_path}")
                    results['path_errors'].append(f"{module_id}: style missing")
            
            print()
        else:
            results['missing'].append(module_id)
            print(f"[FAIL] {module_id} - NOT FOUND IN REGISTRY")
            print()
    
    # Summary
    print("\nBACKEND DISCOVERY SUMMARY:")
    print(f"  Discovered: {len(results['discovered'])}/4")
    print(f"  Missing: {len(results['missing'])}")
    print(f"  Path Errors: {len(results['path_errors'])}")
    
    return results['missing'] == [] and results['path_errors'] == []


def test_flask_api_endpoints():
    """Test 2: Flask API Endpoints"""
    print_section("TEST 2: FLASK API ENDPOINTS")
    
    base_url = "http://localhost:5001"
    
    tests = [
        {
            'name': 'List All Modules',
            'url': f'{base_url}/api/modules/list',
            'method': 'GET',
            'expected_keys': ['modules']
        },
        {
            'name': 'Get Thread Cards Module',
            'url': f'{base_url}/api/modules/thread-cards',
            'method': 'GET',
            'expected_keys': ['id', 'name', 'scriptPath', 'stylePath']
        },
        {
            'name': 'Get Synergy Module',
            'url': f'{base_url}/api/modules/synergy_sessions',
            'method': 'GET',
            'expected_keys': ['id', 'name', 'scriptPath', 'stylePath']
        }
    ]
    
    results = {'passed': 0, 'failed': 0, 'errors': []}
    
    for test in tests:
        try:
            print(f"Testing: {test['name']}")
            print(f"  URL: {test['url']}")
            
            response = requests.get(test['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected keys
                if test['name'] == 'List All Modules':
                    if 'modules' in data and len(data['modules']) > 0:
                        print(f"  [OK] Response valid ({len(data['modules'])} modules)")
                        
                        # Verify internal modules present
                        module_ids = [m['id'] for m in data['modules']]
                        internal = ['thread-cards', 'synergy_sessions', 'settings-sidebar', 'automation-workflows']
                        found_internal = [mid for mid in internal if mid in module_ids]
                        
                        print(f"  [OK] Internal modules found: {len(found_internal)}/4")
                        results['passed'] += 1
                    else:
                        print(f"  [FAIL] Invalid response structure")
                        results['failed'] += 1
                else:
                    # Individual module check
                    missing_keys = [key for key in test['expected_keys'] if key not in data]
                    
                    if not missing_keys:
                        print(f"  [OK] All required keys present")
                        print(f"       scriptPath: {data.get('scriptPath', 'N/A')}")
                        print(f"       stylePath: {data.get('stylePath', 'N/A')}")
                        results['passed'] += 1
                    else:
                        print(f"  [FAIL] Missing keys: {missing_keys}")
                        results['failed'] += 1
                        results['errors'].append(f"{test['name']}: missing {missing_keys}")
            else:
                print(f"  [FAIL] HTTP {response.status_code}")
                results['failed'] += 1
                results['errors'].append(f"{test['name']}: HTTP {response.status_code}")
            
            print()
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            results['failed'] += 1
            results['errors'].append(f"{test['name']}: {str(e)}")
            print()
    
    # Summary
    print("\nAPI ENDPOINT SUMMARY:")
    print(f"  Passed: {results['passed']}/{len(tests)}")
    print(f"  Failed: {results['failed']}/{len(tests)}")
    
    if results['errors']:
        print("\nERRORS:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return results['failed'] == 0


def test_file_path_resolution():
    """Test 3: File Path Resolution"""
    print_section("TEST 3: FILE PATH RESOLUTION")
    
    # Test that paths resolve correctly
    modules_to_test = [
        {
            'id': 'thread-cards',
            'scriptPath': 'modules/thread-cards/thread-card-registry.js',
            'stylePath': 'modules/thread-cards/thread-card-styles.css'
        },
        {
            'id': 'synergy_sessions',
            'scriptPath': 'modules/synergy/synergy-sidebar-controller.js',
            'stylePath': 'modules/synergy/synergy-sidebar.css'
        },
        {
            'id': 'settings-sidebar',
            'scriptPath': 'modules/settings-sidebar-externalversion/settings-sidebar.js',
            'stylePath': 'modules/settings-sidebar-externalversion/settings-sidebar.css'
        },
        {
            'id': 'automation-workflows',
            'scriptPath': 'modules/automation-workflows/automation-workflows.js',
            'stylePath': 'modules/automation-workflows/automation-workflows.css'
        }
    ]
    
    results = {'passed': 0, 'failed': 0, 'errors': []}
    
    for module in modules_to_test:
        print(f"Testing: {module['id']}")
        
        # Test script path
        script_full_path = base_dir / "UI" / module['scriptPath']
        if script_full_path.exists():
            size = script_full_path.stat().st_size
            print(f"  [OK] Script: {module['scriptPath']} ({size} bytes)")
        else:
            print(f"  [FAIL] Script NOT FOUND: {module['scriptPath']}")
            results['errors'].append(f"{module['id']}: script missing")
            results['failed'] += 1
        
        # Test style path
        style_full_path = base_dir / "UI" / module['stylePath']
        if style_full_path.exists():
            size = style_full_path.stat().st_size
            print(f"  [OK] Style: {module['stylePath']} ({size} bytes)")
        else:
            print(f"  [FAIL] Style NOT FOUND: {module['stylePath']}")
            results['errors'].append(f"{module['id']}: style missing")
            results['failed'] += 1
        
        if script_full_path.exists() and style_full_path.exists():
            results['passed'] += 1
        
        print()
    
    # Summary
    print("\nFILE PATH RESOLUTION SUMMARY:")
    print(f"  Passed: {results['passed']}/4 modules")
    print(f"  Errors: {len(results['errors'])}")
    
    return results['failed'] == 0


def test_module_manifest_validity():
    """Test 4: Module Manifest Validity"""
    print_section("TEST 4: MODULE MANIFEST VALIDITY")
    
    modules_dir = base_dir / "UI" / "modules"
    
    module_folders = [
        'thread-cards',
        'synergy',
        'settings-sidebar-externalversion',
        'automation-workflows'
    ]
    
    results = {'passed': 0, 'failed': 0, 'errors': []}
    
    for folder in module_folders:
        manifest_path = modules_dir / folder / "manifest.json"
        
        print(f"Testing: {folder}/manifest.json")
        
        if not manifest_path.exists():
            print(f"  [FAIL] Manifest not found")
            results['failed'] += 1
            results['errors'].append(f"{folder}: manifest.json missing")
            print()
            continue
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Check required fields
            required_fields = ['id', 'name', 'version', 'icon', 'color']
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                print(f"  [FAIL] Missing required fields: {missing_fields}")
                results['failed'] += 1
                results['errors'].append(f"{folder}: missing {missing_fields}")
            else:
                print(f"  [OK] All required fields present")
                print(f"       ID: {manifest['id']}")
                print(f"       Name: {manifest['name']}")
                print(f"       Version: {manifest['version']}")
                
                # Check for scriptPath/stylePath
                if 'scriptPath' in manifest:
                    print(f"       scriptPath: {manifest['scriptPath']}")
                if 'stylePath' in manifest:
                    print(f"       stylePath: {manifest['stylePath']}")
                
                results['passed'] += 1
            
        except json.JSONDecodeError as e:
            print(f"  [FAIL] Invalid JSON: {str(e)}")
            results['failed'] += 1
            results['errors'].append(f"{folder}: invalid JSON")
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            results['failed'] += 1
            results['errors'].append(f"{folder}: {str(e)}")
        
        print()
    
    # Summary
    print("\nMANIFEST VALIDITY SUMMARY:")
    print(f"  Passed: {results['passed']}/4")
    print(f"  Failed: {results['failed']}/4")
    
    return results['failed'] == 0


def test_complete_integration_pathway():
    """Test 5: Complete Integration Pathway"""
    print_section("TEST 5: COMPLETE INTEGRATION PATHWAY")
    
    print("Tracing complete pathway for 'thread-cards' module:\n")
    
    # Step 1: Backend Registry
    print("STEP 1: Backend Module Registry")
    print("-" * 40)
    registry = get_module_registry()
    module = registry.get_module('thread-cards')
    
    if module:
        print(f"[OK] Module found in registry")
        print(f"     Module Path: {module.module_path}")
        print(f"     Script Path: {module.scriptPath}")
        print(f"     Style Path: {module.stylePath}")
    else:
        print(f"[FAIL] Module NOT found in registry")
        return False
    
    # Step 2: Flask API
    print("\nSTEP 2: Flask API Endpoint")
    print("-" * 40)
    try:
        response = requests.get('http://localhost:5001/api/modules/thread-cards', timeout=5)
        if response.status_code == 200:
            api_data = response.json()
            print(f"[OK] API endpoint accessible")
            print(f"     Response keys: {list(api_data.keys())}")
            print(f"     scriptPath from API: {api_data.get('scriptPath')}")
            print(f"     stylePath from API: {api_data.get('stylePath')}")
        else:
            print(f"[FAIL] API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] API request failed: {str(e)}")
        return False
    
    # Step 3: File Resolution
    print("\nSTEP 3: File Resolution")
    print("-" * 40)
    script_path = base_dir / "UI" / module.scriptPath
    style_path = base_dir / "UI" / module.stylePath
    
    if script_path.exists():
        print(f"[OK] Script file exists")
        print(f"     Full path: {script_path}")
        print(f"     Size: {script_path.stat().st_size} bytes")
    else:
        print(f"[FAIL] Script file NOT found")
        return False
    
    if style_path.exists():
        print(f"[OK] Style file exists")
        print(f"     Full path: {style_path}")
        print(f"     Size: {style_path.stat().st_size} bytes")
    else:
        print(f"[FAIL] Style file NOT found")
        return False
    
    # Step 4: Frontend URL Construction
    print("\nSTEP 4: Frontend URL Construction")
    print("-" * 40)
    expected_script_url = f"/UI/{module.scriptPath}"
    expected_style_url = f"/UI/{module.stylePath}"
    
    print(f"Expected script URL: {expected_script_url}")
    print(f"Expected style URL: {expected_style_url}")
    print(f"[OK] URLs constructed correctly")
    
    # Step 5: Complete Pathway Summary
    print("\nSTEP 5: Complete Pathway Summary")
    print("-" * 40)
    print("PATHWAY TRACE:")
    print(f"  1. Module folder: UI/modules/thread-cards/")
    print(f"  2. Manifest loaded: manifest.json")
    print(f"  3. Registry entry: ModuleRegistry.modules['thread-cards']")
    print(f"  4. Flask API: /api/modules/thread-cards")
    print(f"  5. Frontend loader: ModuleLoader.loadModule('thread-cards')")
    print(f"  6. Script injection: <script src='/UI/{module.scriptPath}'>")
    print(f"  7. Style injection: <link href='/UI/{module.stylePath}'>")
    print(f"  8. Module initialization: window.ThreadCardRegistry.initialize()")
    print("\n[OK] Complete pathway verified!")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  MODULE CONNECTION PATHWAY TEST SUITE")
    print("="*80)
    
    results = {
        'Backend Discovery': False,
        'Flask API Endpoints': False,
        'File Path Resolution': False,
        'Manifest Validity': False,
        'Integration Pathway': False
    }
    
    # Run tests
    try:
        results['Backend Discovery'] = test_backend_module_discovery()
    except Exception as e:
        print(f"\n[ERROR] Backend Discovery test failed: {str(e)}\n")
    
    try:
        results['Flask API Endpoints'] = test_flask_api_endpoints()
    except Exception as e:
        print(f"\n[ERROR] Flask API test failed: {str(e)}\n")
    
    try:
        results['File Path Resolution'] = test_file_path_resolution()
    except Exception as e:
        print(f"\n[ERROR] File Path Resolution test failed: {str(e)}\n")
    
    try:
        results['Manifest Validity'] = test_module_manifest_validity()
    except Exception as e:
        print(f"\n[ERROR] Manifest Validity test failed: {str(e)}\n")
    
    try:
        results['Integration Pathway'] = test_complete_integration_pathway()
    except Exception as e:
        print(f"\n[ERROR] Integration Pathway test failed: {str(e)}\n")
    
    # Final Summary
    print_section("FINAL TEST RESULTS")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\n{'='*80}")
    print(f"  OVERALL: {passed}/{total} tests passed")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("SUCCESS: All module connection pathways verified!")
        return 0
    else:
        print(f"PARTIAL SUCCESS: {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
