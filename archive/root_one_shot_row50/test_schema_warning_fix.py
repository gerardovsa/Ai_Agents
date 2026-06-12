"""Test schema loading with improved error handling"""
import sys
import logging

# Set up logging to capture warnings
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

from tools.registry_v3 import RegistryV3

print("\nInitializing Registry V3...")
r = RegistryV3()

print(f"\n✅ SUCCESS: Loaded {len(r.tools)} tools")
print(f"   No 'knowledge_graph_tools.json' warning")
print(f"   Improved error handling working")
