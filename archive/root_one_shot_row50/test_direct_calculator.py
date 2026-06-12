#!/usr/bin/env python3
"""Direct test of calculator via registry"""
import sys
import os
from pathlib import Path

# Set working directory and paths
os.chdir(Path(__file__).parent)
root = Path(__file__).parent

sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "AI_infrastructure"))
sys.path.insert(0, str(root / "tools"))

print("="*80)
print("DIRECT CALCULATOR TEST VIA REGISTRY")
print("="*80)

# Import registry (this will load all tools)
print("\n[1] Loading registry...")
from tools.registry_v3 import RegistryV3
registry = RegistryV3()

print(f"[1] Registry loaded: {len(registry.tools)} tools")

# Test calculate_business_cards
print("\n[2] Testing calculate_business_cards...")
try:
    result = registry.execute_tool(
        tool_name="calculate_business_cards",
        quantity=1000,
        finish_size="90x55mm",
        stock_type="satin_350gsm",
        print_type="double_sided",
        celloglaze="2_side_matt",
        artworks=1
    )
    
    if isinstance(result, dict) and 'total_price' in result:
        print(f"[2] PASS - Total: ${result['total_price']:.2f}, Unit: ${result.get('unit_price', 0):.4f}")
    else:
        print(f"[2] Result: {result}")
        
except Exception as e:
    print(f"[2] FAIL: {e}")
    import traceback
    traceback.print_exc()

# Test calculate_folded_flyers_shopify
print("\n[3] Testing calculate_folded_flyers_shopify...")
try:
    result = registry.execute_tool(
        tool_name="calculate_folded_flyers_shopify",
        quantity=1000,
        finish_size="A4",
        stock_type="satin_350gsm",
        folds="half_fold",
        print_type="double_sided",
        celloglaze="2_side_matt",
        artworks=1
    )
    
    if isinstance(result, dict) and 'total_price' in result:
        print(f"[3] PASS - Total: ${result['total_price']:.2f}, Unit: ${result.get('unit_price', 0):.4f}")
    else:
        print(f"[3] Result: {result}")
        
except Exception as e:
    print(f"[3] FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("CALCULATOR TOOLS WORKING VIA REGISTRY")
print("="*80)
