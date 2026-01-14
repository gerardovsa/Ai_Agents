"""
Test script for all 4 meta-tools modules
Tests: PlatformToolsLister, PlatformGuideProvider, WorkflowInstructor, SmartToolInstructor
"""

import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

print("=" * 60)
print("META-TOOLS MODULE TESTS")
print("=" * 60)

# Test 1: PlatformToolsLister
print("\n[TEST 1] PlatformToolsLister...")
try:
    from AI_infrastructure.meta_tools.platform_tools_lister import PlatformToolsLister
    lister = PlatformToolsLister()
    
    # Get platforms
    platforms = lister.list_all_platforms()
    print(f"   Found {len(platforms)} platforms")
    
    # Get tool count
    counts = lister.get_tool_count_by_platform()
    total_tools = sum(counts.values())
    print(f"   Total tools: {total_tools}")
    
    # List tools for one platform
    if 'google_workspace' in platforms:
        tools_list = lister.list_tools('google_workspace')
        print(f"   Google Workspace tools listed")
    
    print("   RESULT: PASS")
except Exception as e:
    print(f"   RESULT: FAIL - {e}")

# Test 2: PlatformGuideProvider
print("\n[TEST 2] PlatformGuideProvider...")
try:
    from AI_infrastructure.meta_tools.platform_guide_provider import PlatformGuideProvider
    guide_provider = PlatformGuideProvider()
    
    # List available guides
    guides = guide_provider.list_available_guides()
    print(f"   Available guides: {guides}")
    
    # Get a guide
    google_guide = guide_provider.get_platform_guide('google_workspace')
    print(f"   Google guide length: {len(google_guide)} characters")
    
    microsoft_guide = guide_provider.get_platform_guide('microsoft')
    print(f"   Microsoft guide length: {len(microsoft_guide)} characters")
    
    calculator_guide = guide_provider.get_platform_guide('calculator')
    print(f"   Calculator guide length: {len(calculator_guide)} characters")
    
    print("   RESULT: PASS")
except Exception as e:
    print(f"   RESULT: FAIL - {e}")

# Test 3: WorkflowInstructor
print("\n[TEST 3] WorkflowInstructor...")
try:
    from AI_infrastructure.meta_tools.workflow_instructor import WorkflowInstructor
    workflow = WorkflowInstructor()
    
    # List workflows
    workflows = workflow.list_available_workflows()
    print(f"   Available workflows: {len(workflows)} workflows")
    
    # Get a workflow
    email_workflow = workflow.get_workflow('send_email')
    print(f"   Email workflow length: {len(email_workflow)} characters")
    
    quote_workflow = workflow.get_workflow('generate_quote')
    print(f"   Quote workflow length: {len(quote_workflow)} characters")
    
    print("   RESULT: PASS")
except Exception as e:
    print(f"   RESULT: FAIL - {e}")

# Test 4: SmartToolInstructor
print("\n[TEST 4] SmartToolInstructor...")
try:
    from AI_infrastructure.meta_tools.smart_tool_instructor import SmartToolInstructor
    smart = SmartToolInstructor()
    
    # Test intent detection
    recommendation = smart.recommend_tools(
        "Send an email to john@example.com about the invoice",
        user_platforms=['google_workspace']
    )
    print(f"   Email recommendation length: {len(recommendation)} characters")
    
    # Test tool sequence
    sequence = smart.get_tool_sequence('email', user_platforms=['google_workspace'])
    print(f"   Email sequence length: {len(sequence)} characters")
    
    quote_sequence = smart.get_tool_sequence('quote')
    print(f"   Quote sequence length: {len(quote_sequence)} characters")
    
    print("   RESULT: PASS")
except Exception as e:
    print(f"   RESULT: FAIL - {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
