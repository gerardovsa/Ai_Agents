"""Quick test with broader date range"""
import sys
import os
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from tools.implementations.veterinary_alerts_tools import get_alerts_by_tag

print("🔍 Testing with broader date range...")
print("="*80)

# Try last 30 days
date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
print(f"\n📅 Searching from: {date_from}")

result = get_alerts_by_tag(
    alert_tags="ALL",
    date_from=date_from,
    limit=10
)

print(f"\n✅ Success: {result['success']}")
print(f"📊 Found {result['alert_count']} alerts")

if result['alerts']:
    print(f"\n📋 Sample Alerts:")
    for i, alert in enumerate(result['alerts'][:3], 1):
        print(f"\n{i}. Call ID: {alert.get('call_id')}")
        print(f"   Code: {alert.get('alert_code')}")
        print(f"   Severity: {alert.get('severity')}")
        print(f"   Priority: {alert.get('priority')}")
        print(f"   Tags: {alert.get('tags')}")
        print(f"   Reason: {alert.get('core_reason', '')[:100]}...")
    
    print(f"\n📈 Summary:")
    print(f"   By Severity: {result['summary'].get('by_severity', {})}")
    print(f"   By Priority: {result['summary'].get('by_priority', {})}")
    print(f"   By Tag: {dict(list(result['summary'].get('by_tag', {}).items())[:5])}")
else:
    print("\n⚠️  No alerts found in last 30 days")
    print("   This may indicate:")
    print("   - No recent alerts in database")
    print("   - Database is empty")
    print("   - Date filtering needs adjustment")

print("\n🎉 Test completed!")
