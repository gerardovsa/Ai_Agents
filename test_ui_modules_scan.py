"""
Test UI Modules Discovery and Path Validation

This script verifies that all modules in UI/modules/ are properly:
1. Discovered by the module registry
2. Have correct file paths
3. Have all required files accessible
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir))

from AI_infrastructure.core.module_registry import get_module_registry

def test_ui_modules_discovery():
    """Test that all UI/modules/ are discovered"""
    print("\n" + "="*80)
    print("UI MODULES DISCOVERY TEST")
    print("="*80 + "\n")
    
    registry = get_module_registry()
    
    # Expected modules in UI/modules/
    expected_modules = [
        'thread-cards',
        'synergy_sessions',
        'settings-sidebar',
        'automation-workflows'
    ]
    
    print(f"Total modules loaded: {len(registry.modules)}\n")
    
    # Check each expected module
    for module_id in expected_modules:
        module = registry.get_module(module_id)
        
        if module:
            print(f"[OK] MODULE FOUND: {module_id}")
            print(f"   Name: {module.name}")
            print(f"   Version: {module.version}")
            print(f"   Icon: {module.icon}")
            print(f"   Color: {module.color}")
            
            # Check file paths
            if module.scriptPath:
                print(f"   Script: {module.scriptPath}")
                # Verify file exists
                script_full_path = base_dir / "UI" / module.scriptPath
                if script_full_path.exists():
                    print(f"      [OK] File exists: {script_full_path}")
                else:
                    print(f"      [FAIL] File NOT found: {script_full_path}")
            
            if module.stylePath:
                print(f"   Style: {module.stylePath}")
                # Verify file exists
                style_full_path = base_dir / "UI" / module.stylePath
                if style_full_path.exists():
                    print(f"      [OK] File exists: {style_full_path}")
                else:
                    print(f"      [FAIL] File NOT found: {style_full_path}")
            
            if module.htmlPath:
                print(f"   HTML: {module.htmlPath}")
                # Verify file exists
                html_full_path = base_dir / "UI" / module.htmlPath
                if html_full_path.exists():
                    print(f"      [OK] File exists: {html_full_path}")
                else:
                    print(f"      [FAIL] File NOT found: {html_full_path}")
            
            print(f"   Module Path: {module.module_path}")
            print()
        else:
            print(f"[FAIL] MODULE NOT FOUND: {module_id}")
            print(f"   Expected in: UI/modules/{module_id}/")
            print()
    
    # List all discovered modules
    print("\n" + "-"*80)
    print("ALL DISCOVERED MODULES:")
    print("-"*80)
    
    for module_id, module in sorted(registry.modules.items()):
        # Normalize path for comparison (handle Windows backslashes)
        normalized_path = module.module_path.replace('\\', '/')
        
        if "UI/modules" in normalized_path and "external" not in normalized_path:
            source = "UI/modules (INTERNAL)"
        elif "UI/external/modules" in normalized_path or "external" in normalized_path:
            source = "UI/external/modules (EXTERNAL)"
        elif "frontend/modules" in normalized_path:
            source = "frontend/modules (LEGACY)"
        else:
            source = "UNKNOWN"
        
        print(f"  {module_id:30} → {source}")
    
    print("\n" + "="*80)
    print(f"SUMMARY: {len(registry.modules)} modules discovered")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_ui_modules_discovery()
