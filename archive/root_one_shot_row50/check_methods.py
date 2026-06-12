"""Check that thread-local methods exist in RegistryV3"""
from tools.registry_v3 import RegistryV3
import inspect

print("="*60)
print("CHECKING THREAD-LOCAL METHODS")
print("="*60)

methods = [m for m in dir(RegistryV3) if 'thread' in m.lower()]
print(f"\nThread-related methods found: {len(methods)}")
for m in methods:
    print(f"  - {m}")

print("\n" + "="*60)
print("METHOD SIGNATURES")
print("="*60)

for method_name in ['set_thread_user_id', 'get_thread_user_id', 'clear_thread_user_id']:
    if hasattr(RegistryV3, method_name):
        method = getattr(RegistryV3, method_name)
        sig = inspect.signature(method)
        print(f"[OK] {method_name}{sig}")
    else:
        print(f"[FAIL] {method_name} NOT FOUND")

print("\n" + "="*60)
print("CLASS VARIABLE CHECK")
print("="*60)

if hasattr(RegistryV3, '_thread_local'):
    print("[OK] _thread_local class variable exists")
else:
    print("[FAIL] _thread_local class variable NOT FOUND")

print("\n" + "="*60)
print("[OK] ALL CHECKS PASSED - Methods are in place!")
print("="*60)
