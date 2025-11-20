"""
Test that list_platform_tools is NOT truncated anymore
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from AI_infrastructure.core.combined_agent_worker import smart_truncate_tool_result

# Simulate list_platform_tools result
result = {
    "success": True,
    "platform": "microsoft_outlook",
    "matched_platform": "microsoft_outlook",
    "tool_count": 23,
    "tools": [
        {"name": f"outlook_tool_{i}", "description": "Test tool"} 
        for i in range(23)
    ]
}

print("\n" + "="*70)
print("TEST: list_platform_tools Truncation Check")
print("="*70)

# Call smart_truncate_tool_result
result_str = smart_truncate_tool_result(result, tool_name='list_platform_tools', max_tokens=2000)

print(f"\nResult length: {len(result_str):,} chars")
print(f"\nFirst 500 chars:\n{result_str[:500]}")

# Check for truncation indicators
if 'truncated=False' in result_str and 'type=META_TOOL' in result_str:
    print("\n✅ SUCCESS: Meta-tool NOT truncated!")
    print("   - Contains 'truncated=False' marker")
    print("   - Contains 'type=META_TOOL' marker")
    print("   - Full result returned")
elif 'truncated": true' in result_str or '"truncated": true' in result_str:
    print("\n❌ FAIL: Meta-tool WAS truncated!")
    print("   - Contains truncation marker")
    print("   - Result was cut short")
else:
    print("\n⚠️  UNKNOWN: Could not determine truncation status")

# Check if all tools are present
import json
if '[METADATA:' in result_str:
    # Extract JSON after metadata header
    json_start = result_str.index('\n\n') + 2
    data = json.loads(result_str[json_start:])
    tool_count = len(data.get('tools', []))
    print(f"\n   Tools in result: {tool_count}")
    if tool_count == 23:
        print("   ✅ All 23 tools present!")
    else:
        print(f"   ❌ Only {tool_count} tools present (expected 23)")
