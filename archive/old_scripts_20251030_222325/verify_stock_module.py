"""
Stock Management Module - Registration Verification
===================================================

This script verifies the stock-management module is properly registered
and can be loaded by the ModuleManager.

Checks:
1. manifest.json exists and is valid JSON
2. stock-management.js exists
3. Module registration code is present
4. Flask serves the files correctly
"""

import requests
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}→ {text}{Colors.ENDC}")

BASE_URL = "http://localhost:5001"

def main():
    print_header("STOCK MANAGEMENT MODULE - REGISTRATION VERIFICATION")
    
    # Check 1: Module manifest file
    print_info("Check 1: Module manifest.json")
    module_manifest_path = Path("UI/external/modules/stock-management/manifest.json")
    
    if not module_manifest_path.exists():
        print_error(f"Module manifest not found: {module_manifest_path}")
        return False
    
    try:
        with open(module_manifest_path, 'r') as f:
            module_manifest = json.load(f)
        
        # Validate required fields
        required_fields = ['id', 'name', 'version', 'icon', 'scriptPath']
        missing_fields = [f for f in required_fields if f not in module_manifest]
        
        if missing_fields:
            print_error(f"Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print_success(f"Module manifest valid: {module_manifest['name']} v{module_manifest['version']}")
        print(f"  ID: {module_manifest['id']}")
        print(f"  Icon: {module_manifest['icon']}")
        print(f"  Tabs: {len(module_manifest.get('tabs', []))}")
        
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in manifest: {e}")
        return False
    
    # Check 2: Module JavaScript file
    print_info("\nCheck 2: Module JavaScript file")
    module_js_path = Path("UI/external/modules/stock-management/stock-management.js")
    
    if not module_js_path.exists():
        print_error(f"Module JS not found: {module_js_path}")
        return False
    
    # Read JS file and check for registration code
    with open(module_js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    checks = {
        'Class definition': 'class StockManagementModule extends BaseModule' in js_content,
        'ModuleRegistry registration': "window.ModuleRegistry['stock-management']" in js_content,
        'Initialize method': 'async initialize()' in js_content,
        'InitializeSubTabs method': 'initializeSubTabs()' in js_content
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} MISSING")
            all_passed = False
    
    if not all_passed:
        return False
    
    # Check 3: Main manifest registration
    print_info("\nCheck 3: Main modules manifest")
    main_manifest_path = Path("UI/external/modules/manifest.json")
    
    if not main_manifest_path.exists():
        print_error(f"Main manifest not found: {main_manifest_path}")
        return False
    
    try:
        with open(main_manifest_path, 'r') as f:
            main_manifest = json.load(f)
        
        # Check if stock-management is registered
        stock_module = None
        for module in main_manifest.get('modules', []):
            if module.get('id') == 'stock-management':
                stock_module = module
                break
        
        if not stock_module:
            print_error("stock-management not found in main manifest")
            return False
        
        print_success("stock-management registered in main manifest")
        print(f"  Enabled: {stock_module.get('enabled', True)}")
        print(f"  Manifest Path: {stock_module.get('manifestPath')}")
        print(f"  Script Path: {stock_module.get('scriptPath')}")
        
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in main manifest: {e}")
        return False
    
    # Check 4: Flask serves files
    print_info("\nCheck 4: Flask server file serving")
    
    try:
        # Test manifest endpoint
        manifest_response = requests.get(
            f"{BASE_URL}/external/modules/stock-management/manifest.json",
            timeout=5
        )
        
        if manifest_response.status_code == 200:
            print_success("Manifest served successfully")
        else:
            print_error(f"Manifest HTTP {manifest_response.status_code}")
            return False
        
        # Test JS endpoint
        js_response = requests.get(
            f"{BASE_URL}/external/modules/stock-management/stock-management.js",
            timeout=5
        )
        
        if js_response.status_code == 200:
            print_success("JavaScript served successfully")
            print(f"  Size: {len(js_response.text)} bytes")
        else:
            print_error(f"JavaScript HTTP {js_response.status_code}")
            return False
        
        # Test CSS endpoint
        css_response = requests.get(
            f"{BASE_URL}/external/modules/stock-management/stock-management.css",
            timeout=5
        )
        
        if css_response.status_code == 200:
            print_success("CSS served successfully")
        else:
            print_warning(f"CSS HTTP {css_response.status_code} (optional)")
        
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to Flask server at {BASE_URL}")
        print_warning("Make sure Flask is running: BISTART")
        return False
    except requests.exceptions.Timeout:
        print_error("Request timeout")
        return False
    
    # Check 5: Browser console check instructions
    print_header("BROWSER VERIFICATION STEPS")
    
    print_info("Open browser console (F12) and check:")
    print("  1. No 404 errors for stock-management files")
    print("  2. Console shows: '✅ StockManagementModule registered in ModuleRegistry'")
    print("  3. Run: window.ModuleRegistry['stock-management']")
    print("     Should return: class StockManagementModule")
    print("  4. Module appears in sidebar with blue box icon")
    print("  5. Clicking module shows 6 tabs")
    
    print_info("\nIf module still not loading:")
    print("  1. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
    print("  2. Clear browser cache")
    print("  3. Check browser console for JavaScript errors")
    print("  4. Verify ModuleManager is initialized before loading modules")
    
    print_header("VERIFICATION COMPLETE")
    print_success("All file checks passed!")
    print_info("Module should now load in browser")
    print_info("URL: http://localhost:5001/business-ai-platform-v2.html")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
