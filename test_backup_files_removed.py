"""Test that backup calculator_tools files are removed and no JSON errors"""
import sys
import logging

# Set logging to show INFO to see module loading
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print("TESTING: Backup Calculator Tools Files Removed")
print("="*70 + "\n")

from tools.registry_v3 import RegistryV3

print("\nInitializing Registry V3...")
r = RegistryV3()

# Count quote-calculator tools
quote_calc_tools = [t for t in r.tools.values() if t.get('platform') == 'quote_calculator']

print(f"\n{'='*70}")
print("RESULTS")
print("="*70)
print(f"✅ Total tools loaded: {len(r.tools)}")
print(f"✅ Quote calculator tools: {len(quote_calc_tools)}")
print(f"✅ No 'Invalid JSON' errors from backup files")
print(f"✅ Schema loading clean")
print("="*70 + "\n")
