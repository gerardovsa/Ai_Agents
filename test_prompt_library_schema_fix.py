"""
Test prompt_library initialization with correct schema prefix
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from init_prompt_library import init_prompt_library_table
import logging

logging.basicConfig(level=logging.INFO)

print("\n" + "="*60)
print("Testing prompt_library initialization...")
print("="*60 + "\n")

result = init_prompt_library_table()

print("\n" + "="*60)
if result:
    print("✅ SUCCESS: prompt_library table initialized with correct schema")
else:
    print("❌ FAILED: prompt_library table initialization failed")
print("="*60)
