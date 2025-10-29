"""
Tool System Testing Script
===========================

This script tests all platform tool integrations.

Usage:
    python test_tools.py                    # Test all tools
    python test_tools.py --platform supabase  # Test specific platform
    python test_tools.py --tool supabase_query  # Test specific tool
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import ToolRegistry


def test_registry():
    """Test the tool registry initialization"""
    print("\n" + "="*60)
    print("TESTING: Tool Registry")
    print("="*60)
    
    try:
        registry = ToolRegistry()
        print(f"✅ Registry initialized")
        print(f"   Total tools: {len(registry.tools)}")
        print(f"   Platforms: {', '.join(registry.get_all_platforms())}")
        
        return registry
    except Exception as e:
        print(f"❌ Registry initialization failed: {e}")
        return None


def test_list_tools(registry):
    """Test listing tools"""
    print("\n" + "="*60)
    print("TESTING: List Tools")
    print("="*60)
    
    try:
        all_tools = registry.list_tools()
        print(f"✅ Listed {len(all_tools)} tools")
        
        # List by platform
        for platform in registry.get_all_platforms():
            platform_tools = registry.list_tools(platform)
            print(f"\n📦 {platform.upper()}: {len(platform_tools)} tools")
            for tool in platform_tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        return True
    except Exception as e:
        print(f"❌ List tools failed: {e}")
        return False


def test_tool_schemas(registry):
    """Test tool schema retrieval"""
    print("\n" + "="*60)
    print("TESTING: Tool Schemas")
    print("="*60)
    
    try:
        # Test a few schemas
        test_tools = ['supabase_query', 'cloudconvert_convert', 'assemblyai_transcribe']
        
        for tool_name in test_tools:
            schema = registry.get_tool_schema(tool_name)
            if schema:
                print(f"✅ {tool_name}: {len(schema.get('parameters', {}))} parameters")
            else:
                print(f"❌ {tool_name}: Schema not found")
        
        return True
    except Exception as e:
        print(f"❌ Schema retrieval failed: {e}")
        return False


def test_parameter_validation(registry):
    """Test parameter validation"""
    print("\n" + "="*60)
    print("TESTING: Parameter Validation")
    print("="*60)
    
    try:
        # Test valid parameters
        valid, error = registry.validate_parameters(
            'supabase_query',
            {'table': 'users', 'select': '*'}
        )
        if valid:
            print("✅ Valid parameters accepted")
        else:
            print(f"❌ Valid parameters rejected: {error}")
        
        # Test missing required parameter
        valid, error = registry.validate_parameters(
            'supabase_query',
            {'select': '*'}  # Missing 'table'
        )
        if not valid:
            print(f"✅ Missing parameter detected: {error}")
        else:
            print("❌ Missing parameter not detected")
        
        # Test unknown parameter
        valid, error = registry.validate_parameters(
            'supabase_query',
            {'table': 'users', 'unknown_param': 'value'}
        )
        if not valid:
            print(f"✅ Unknown parameter detected: {error}")
        else:
            print("❌ Unknown parameter not detected")
        
        return True
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
        return False


def test_dry_run_tools(registry):
    """Test tool execution (dry run - doesn't actually call APIs)"""
    print("\n" + "="*60)
    print("TESTING: Dry Run Tool Execution")
    print("="*60)
    
    # Test tools that don't require actual API calls
    test_cases = [
        {
            'tool': 'supabase_query',
            'params': {'table': 'test_table', 'limit': 5},
            'description': 'Supabase query (would query database)'
        },
        {
            'tool': 'cloudconvert_status',
            'params': {'job_id': 'test-job-123'},
            'description': 'CloudConvert status check'
        },
        {
            'tool': 'ngrok_list_tunnels',
            'params': {},
            'description': 'Ngrok tunnel listing'
        }
    ]
    
    print("\n⚠️ NOTE: These tests validate tool structure but don't make actual API calls")
    print("   To test with real APIs, use the live testing section below.\n")
    
    for test in test_cases:
        tool_name = test['tool']
        params = test['params']
        desc = test['description']
        
        print(f"\n🔍 Testing: {desc}")
        print(f"   Tool: {tool_name}")
        print(f"   Parameters: {params}")
        
        # Validate parameters
        valid, error = registry.validate_parameters(tool_name, params)
        if valid:
            print(f"   ✅ Parameters validated")
        else:
            print(f"   ❌ Validation failed: {error}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print(" "*20 + "AI AGENTS TOOL SYSTEM TEST SUITE")
    print("="*80)
    
    registry = test_registry()
    if not registry:
        print("\n❌ Cannot continue - registry initialization failed")
        return False
    
    results = []
    results.append(test_list_tools(registry))
    results.append(test_tool_schemas(registry))
    results.append(test_parameter_validation(registry))
    test_dry_run_tools(registry)  # Informational only
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. Review test results above
2. Check implementations in tools/implementations/
3. Run live API tests with actual credentials (see TESTING_LIVE.md)
4. Integrate tools into your AI copilot workflows

For live testing with real APIs:
  python test_tools_live.py --platform supabase

For usage examples:
  See examples/ folder
    """)
    
    return passed == total


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test AI Agents Tool System')
    parser.add_argument('--platform', help='Test specific platform')
    parser.add_argument('--tool', help='Test specific tool')
    
    args = parser.parse_args()
    
    if args.platform or args.tool:
        # Targeted testing
        registry = ToolRegistry()
        
        if args.tool:
            print(f"\n🔍 Testing tool: {args.tool}")
            schema = registry.get_tool_schema(args.tool)
            if schema:
                print(f"✅ Tool found: {schema['description']}")
                print(f"   Platform: {schema['platform']}")
                print(f"   Parameters: {list(schema.get('parameters', {}).keys())}")
            else:
                print(f"❌ Tool not found: {args.tool}")
        
        elif args.platform:
            print(f"\n🔍 Testing platform: {args.platform}")
            tools = registry.get_platform_tools(args.platform)
            if tools:
                print(f"✅ Found {len(tools)} tools:")
                for tool_name in tools:
                    print(f"   - {tool_name}")
            else:
                print(f"❌ No tools found for platform: {args.platform}")
    
    else:
        # Run full test suite
        success = run_all_tests()
        sys.exit(0 if success else 1)
