"""Quick test of veterinary alerts tools import"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools.implementations.veterinary_alerts_tools import (
    get_alerts_by_tag,
    get_call_transcript,
    get_call_metadata,
    analyze_multiple_alerts,
    create_action_plan,
    update_alert_status,
    bulk_update_alerts,
    TOOLS_METADATA
)

print("✅ Import successful!")
print("\n📋 Available Tools:")
print(f"   Platform: {TOOLS_METADATA['platform']}")
print(f"   Version: {TOOLS_METADATA['version']}")
print(f"   Database: {TOOLS_METADATA['database']}")
print(f"\n🛠️  {len(TOOLS_METADATA['tools'])} tools loaded:")
for tool in TOOLS_METADATA['tools']:
    print(f"   ✓ {tool['name']} ({tool['category']}) - {tool['estimated_time']}")

print("\n🎉 All tools ready for use!")
