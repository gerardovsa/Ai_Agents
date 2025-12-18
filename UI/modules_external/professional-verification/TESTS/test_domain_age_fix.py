"""Test check_domain_age datetime bug fix"""
import sys
import os
import json
from datetime import datetime

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(module_dir, 'tools', 'implementations'))

from verification_core import check_domain_age

print("=" * 80)
print("Testing check_domain_age datetime fix")
print("=" * 80)

# Test with scatechnology.ai (the one that failed)
test_domain = 'scatechnology.ai'
print(f"\n🔍 Testing: {test_domain}")
print("-" * 80)

result = check_domain_age(test_domain)
print(json.dumps(result, indent=2, default=str))

if result.get('success'):
    print("\n✅ SUCCESS: check_domain_age is working!")
    print(f"   Domain age: {result.get('age_days')} days")
    print(f"   Created: {result.get('creation_date')}")
    print(f"   Is recent: {result.get('is_recently_created')}")
    print(f"   Risk flag: {result.get('risk_flag')}")
else:
    print(f"\n❌ FAILED: {result.get('error')}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ All tests passed!")
print("=" * 80)
