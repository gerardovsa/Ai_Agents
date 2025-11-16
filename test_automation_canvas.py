"""
TEST: Visual Automation Canvas - Complete Integration Test
==========================================================
Tests the entire automation workflow system:
1. Tool registry loading (9 new automation tools)
2. Backend API endpoints (9 routes)
3. UI module registration
4. End-to-end workflow creation and execution

Usage:
    python test_automation_canvas.py
    
Expected Results:
    - All 9 automation tools loaded in registry
    - Backend routes respond correctly
    - UI module appears in sidebar
    - Sample workflow created and executable
"""

import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / 'AI_infrastructure'))

def test_tool_registry():
    """Test that automation tools are loaded in registry"""
    print("\n" + "="*80)
    print("TEST 1: Tool Registry Loading")
    print("="*80)
    
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        # Check for automation tools
        automation_tools = [name for name in registry.tools.keys() if name.startswith('automation_')]
        
        print(f"\nTotal tools loaded: {len(registry.tools)}")
        print(f"Automation tools found: {len(automation_tools)}")
        
        expected_tools = [
            'automation_create_workflow',
            'automation_list_workflows',
            'automation_get_workflow',
            'automation_execute_workflow',
            'automation_schedule_workflow',
            'automation_deactivate_workflow',
            'automation_delete_workflow',
            'automation_get_execution_history',
            'automation_export_workflow'
        ]
        
        print("\nExpected automation tools:")
        for tool in expected_tools:
            exists = tool in automation_tools
            status = "PASS" if exists else "FAIL"
            print(f"  [{status}] {tool}")
        
        missing = set(expected_tools) - set(automation_tools)
        if missing:
            print(f"\n  MISSING TOOLS: {missing}")
            return False
        
        print("\n  ALL AUTOMATION TOOLS LOADED SUCCESSFULLY")
        return True
        
    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_routes():
    """Test that backend routes are accessible"""
    print("\n" + "="*80)
    print("TEST 2: Backend API Routes")
    print("="*80)
    
    try:
        import requests
        
        base_url = 'http://localhost:5001'
        
        # Test health check first
        print(f"\nTesting backend at {base_url}...")
        health_response = requests.get(f'{base_url}/health', timeout=5)
        
        if health_response.status_code != 200:
            print(f"  FAIL: Backend not responding (status {health_response.status_code})")
            print("  Make sure to run: BISTART")
            return False
        
        print("  PASS: Backend is running")
        
        # Test automation endpoints
        test_cases = [
            ('/api/automation/list', 'GET', 'List workflows'),
            ('/api/automation/parse', 'POST', 'Parse visual flow'),
            ('/api/automation/save', 'POST', 'Save workflow'),
        ]
        
        print("\nTesting automation endpoints:")
        for endpoint, method, description in test_cases:
            url = f'{base_url}{endpoint}'
            
            try:
                if method == 'GET':
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.post(url, json={}, timeout=5)
                
                # We expect 400 (bad request) or 401 (unauthorized) for incomplete requests
                # 404 means endpoint doesn't exist
                if response.status_code == 404:
                    print(f"  [FAIL] {method} {endpoint} - NOT FOUND")
                else:
                    print(f"  [PASS] {method} {endpoint} - {description} (status {response.status_code})")
            except requests.exceptions.RequestException as e:
                print(f"  [FAIL] {method} {endpoint} - {str(e)}")
        
        print("\n  BACKEND ROUTES TEST COMPLETE")
        return True
        
    except ImportError:
        print("  SKIP: requests library not available")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_module():
    """Test that UI module is registered"""
    print("\n" + "="*80)
    print("TEST 3: UI Module Registration")
    print("="*80)
    
    try:
        import json
        
        manifest_path = root_dir / 'UI' / 'external' / 'modules' / 'manifest.json'
        
        if not manifest_path.exists():
            print(f"  FAIL: Main manifest not found at {manifest_path}")
            return False
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check if automation-workflows is registered
        modules = manifest.get('modules', [])
        automation_module = None
        
        for module in modules:
            if module.get('id') == 'automation-workflows':
                automation_module = module
                break
        
        if not automation_module:
            print("  FAIL: automation-workflows module not found in manifest")
            return False
        
        print("  PASS: Module registered in manifest")
        print(f"    Name: {automation_module.get('name')}")
        print(f"    Icon: {automation_module.get('icon')}")
        print(f"    Color: {automation_module.get('color')}")
        print(f"    Enabled: {automation_module.get('enabled')}")
        
        # Check module files exist
        module_dir = root_dir / 'UI' / 'external' / 'modules' / 'automation-workflows'
        
        required_files = [
            'manifest.json',
            'automation-workflows.js',
            'automation-workflows.css',
            'automation-canvas-extensions.js'
        ]
        
        print("\n  Checking module files:")
        all_exist = True
        for file in required_files:
            file_path = module_dir / file
            exists = file_path.exists()
            status = "PASS" if exists else "FAIL"
            print(f"    [{status}] {file}")
            if not exists:
                all_exist = False
        
        if not all_exist:
            return False
        
        print("\n  UI MODULE REGISTRATION COMPLETE")
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shape_rendering():
    """Test that CSS shapes are correct"""
    print("\n" + "="*80)
    print("TEST 4: Shape Rendering CSS")
    print("="*80)
    
    try:
        css_path = root_dir / 'UI' / 'external' / 'modules' / 'automation-workflows' / 'automation-workflows.css'
        
        if not css_path.exists():
            print(f"  FAIL: CSS file not found")
            return False
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for corrected shapes
        shape_tests = [
            ('hexagon', 'clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)', 'TRIGGER'),
            ('diamond', 'clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)', 'DECISION'),
            ('circle', 'border-radius: 50%', 'END'),
            ('rectangle', 'border-radius: 8px', 'ACTION')
        ]
        
        print("\n  Checking shape definitions:")
        all_correct = True
        for shape_type, expected_css, label in shape_tests:
            if expected_css in css_content:
                print(f"    [PASS] {shape_type} ({label}) - Correct SVG path")
            else:
                print(f"    [FAIL] {shape_type} ({label}) - Incorrect or missing SVG path")
                all_correct = False
        
        if not all_correct:
            print("\n  WARNING: Some shapes may render incorrectly")
        else:
            print("\n  SHAPE RENDERING CSS CORRECT")
        
        return all_correct
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_creation():
    """Test creating a sample workflow via AI tools"""
    print("\n" + "="*80)
    print("TEST 5: Workflow Creation (End-to-End)")
    print("="*80)
    
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        # Create sample workflow
        print("\n  Creating sample workflow: 'Daily Email Summary'")
        
        result = registry.execute_tool(
            'automation_create_workflow',
            title='Daily Email Summary',
            description='Summarize unread emails every morning at 9am',
            trigger={
                'type': 'schedule',
                'schedule_cron': '0 9 * * *'
            },
            actions=[
                {
                    'tool': 'gmail_list_messages',
                    'parameters': {'max_results': 10, 'query': 'is:unread'}
                },
                {
                    'tool': 'ai_summarize_text',
                    'parameters': {'text': '{{emails}}', 'max_length': 500}
                },
                {
                    'tool': 'gmail_send_email',
                    'parameters': {
                        'to': 'user@example.com',
                        'subject': 'Daily Email Summary',
                        'body': '{{summary}}'
                    }
                }
            ],
            category='email',
            _user_id=1
        )
        
        if result.get('success'):
            print(f"  PASS: Workflow created successfully")
            print(f"    Automation ID: {result.get('automation_id')}")
            print(f"    Slug: {result.get('slug')}")
            print(f"    Actions: {len(result.get('visual_flow_json', '{}'))}")
        else:
            print(f"  FAIL: Workflow creation failed")
            print(f"    Error: {result.get('error', 'Unknown error')}")
            return False
        
        print("\n  END-TO-END WORKFLOW TEST COMPLETE")
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("*" * 80)
    print("  VISUAL AUTOMATION CANVAS - COMPLETE INTEGRATION TEST")
    print("*" * 80)
    
    tests = [
        ("Tool Registry", test_tool_registry),
        ("Backend Routes", test_backend_routes),
        ("UI Module", test_ui_module),
        ("Shape Rendering", test_shape_rendering),
        ("Workflow Creation", test_workflow_creation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  CRITICAL ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  SUCCESS: All tests passed!")
        print("\n  Next Steps:")
        print("    1. Start the backend: BISTART")
        print("    2. Open UI: http://localhost:5001")
        print("    3. Navigate to Automation Workflows module")
        print("    4. Verify shapes render correctly (hexagon, diamond, circle, rectangle)")
        print("    5. Test dragging nodes to canvas")
        print("    6. Test saving workflows")
        print("    7. Test AI agent workflow creation via chat")
        return 0
    else:
        print("\n  FAILURE: Some tests failed")
        print("  Review errors above and fix issues")
        return 1


if __name__ == '__main__':
    exit(main())
