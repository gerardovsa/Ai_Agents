"""Test database connection timeout fix"""
import sys
import time
sys.path.insert(0, 'inhouse_modules')

from db_connector import InHousePrintDB

print("Testing InHousePrintDB connection timeout...")
start = time.time()

try:
    db = InHousePrintDB()
    elapsed = time.time() - start
    print(f"✅ Connection successful after {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Connection failed after {elapsed:.2f}s")
    print(f"Error: {e}")

print(f"\nTotal time: {elapsed:.2f}s")
print(f"Expected: ~15s max (5 drivers × 3s timeout each)")
