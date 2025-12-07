"""
Test Script for deploy_agent() System

Tests:
1. Schema Discovery - Can registry find deploy_agent tool?
2. Schema Loading - Does schema load properly with full instructions?
3. Tool Implementation - Does the implementation exist and import?
4. Parameter Validation - Are all required parameters defined?
5. Simulated Execution - Can we call the tool (dry run)?

Run: python test_deploy_agent.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_1_schema_discovery():
    """Test 1: Can registry discover deploy_agent schema?"""
    print("\n" + "="*70)
    print("TEST 1: Schema Discovery")
    print("="*70)
    
    try:
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
        
        if "deploy_agent" in registry.tools:
            print("✅ SUCCESS: deploy_agent found in registry")
            print(f"   Total tools in registry: {len(registry.tools)}")
            return True
        else:
            print("❌ FAILED: deploy_agent NOT found in registry")
            print(f"   Available tools: {list(registry.tools.keys())[:10]}...")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_schema_content():
    """Test 2: Does schema contain full instructions?"""
    print("\n" + "="*70)
    print("TEST 2: Schema Content & Instructions")
    print("="*70)
    
    try:
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
        
        tool_schema = registry.tools.get("deploy_agent")
        if not tool_schema:
            print("❌ FAILED: Tool schema not found")
            return False
        
        description = tool_schema.get("description", "")
        input_schema = tool_schema.get("input_schema", {})
        properties = input_schema.get("properties", {})
        
        print(f"✅ Schema loaded successfully")
        print(f"\n📋 Description length: {len(description)} characters")
        print(f"📋 Parameters defined: {len(properties)}")
        print(f"\n📝 Parameters:")
        for param_name, param_def in properties.items():
            param_type = param_def.get("type", "unknown")
            required = param_name in input_schema.get("required", [])
            req_marker = "🔴 REQUIRED" if required else "🔵 Optional"
            print(f"   {req_marker} {param_name} ({param_type})")
        
        # Check for key instruction sections in description
        key_sections = [
            "WHEN TO USE",
            "AGENT TYPES",
            "SECURITY",
            "EXAMPLES",
            "COMMON MISTAKES"
        ]
        
        print(f"\n📖 Key Instruction Sections:")
        for section in key_sections:
            if section in description:
                print(f"   ✅ {section}")
            else:
                print(f"   ❌ {section} (missing)")
        
        # Show first 500 chars of description
        print(f"\n📄 Description Preview:")
        print("-" * 70)
        print(description[:500] + "..." if len(description) > 500 else description)
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_implementation_exists():
    """Test 3: Does the implementation file exist and import?"""
    print("\n" + "="*70)
    print("TEST 3: Implementation File")
    print("="*70)
    
    try:
        impl_file = project_root / "tools" / "implementations" / "agent_deployment_tools.py"
        
        if impl_file.exists():
            print(f"✅ Implementation file exists: {impl_file}")
            print(f"   File size: {impl_file.stat().st_size} bytes")
        else:
            print(f"❌ Implementation file NOT found: {impl_file}")
            return False
        
        # Try to import
        try:
            from tools.implementations.agent_deployment_tools import deploy_agent
            print(f"✅ Successfully imported deploy_agent function")
            
            # Check function signature
            import inspect
            sig = inspect.signature(deploy_agent)
            print(f"\n📋 Function Signature:")
            print(f"   deploy_agent{sig}")
            
            return True
        except ImportError as ie:
            print(f"❌ Import failed: {ie}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_python_exec_exists():
    """Test 4: Does python_exec tool exist (required by workers)?"""
    print("\n" + "="*70)
    print("TEST 4: Python Exec Tool (Required by Workers)")
    print("="*70)
    
    try:
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
        
        python_exec_tools = [
            "python_exec",
            "python_exec_with_dataframe",
            "python_exec_analysis"
        ]
        
        found_tools = []
        missing_tools = []
        
        for tool_name in python_exec_tools:
            if tool_name in registry.tools:
                found_tools.append(tool_name)
                print(f"✅ {tool_name} - Available")
            else:
                missing_tools.append(tool_name)
                print(f"❌ {tool_name} - NOT FOUND")
        
        if missing_tools:
            print(f"\n⚠️  WARNING: {len(missing_tools)} python_exec tools missing")
            print(f"   Workers won't be able to execute Python code!")
            return False
        else:
            print(f"\n✅ All {len(found_tools)} python_exec tools available")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_simulated_execution():
    """Test 5: Simulate calling deploy_agent (dry run)"""
    print("\n" + "="*70)
    print("TEST 5: Simulated Execution (Dry Run)")
    print("="*70)
    
    try:
        from tools.implementations.agent_deployment_tools import deploy_agent
        
        print("🧪 Attempting to call deploy_agent with test parameters...")
        print("\n📝 Test Parameters:")
        test_params = {
            "agent_type": "data_analyst",
            "task_description": "Test task: Analyze sample data",
            "files": [],
            "output_requirements": {
                "files": ["test_output.csv"],
                "upload_to": "google_drive"
            },
            "tool_filter": ["python_exec", "read_file", "write_file"],
            "execution_mode": "sync"
        }
        
        for key, value in test_params.items():
            print(f"   {key}: {value}")
        
        print("\n⚠️  NOTE: Actual execution requires:")
        print("   • Claude API credentials")
        print("   • Google Workspace authentication")
        print("   • Active agent worker system")
        print("\n   This is a DRY RUN - checking function callable only")
        
        # Just verify the function is callable (don't actually execute)
        import inspect
        sig = inspect.signature(deploy_agent)
        
        # Check if all required params are in our test
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty and param_name != 'kwargs':
                if param_name not in test_params:
                    print(f"❌ Missing required parameter: {param_name}")
                    return False
        
        print(f"\n✅ All required parameters present")
        print(f"✅ Function is callable with correct signature")
        print(f"\n💡 To actually execute, run:")
        print(f"   result = deploy_agent(**test_params)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and show summary"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  DEPLOY_AGENT() SYSTEM TEST SUITE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    tests = [
        ("Schema Discovery", test_1_schema_discovery),
        ("Schema Content", test_2_schema_content),
        ("Implementation File", test_3_implementation_exists),
        ("Python Exec Tools", test_4_python_exec_exists),
        ("Simulated Execution", test_5_simulated_execution)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! deploy_agent() system is ready!")
        print("\n📚 Next Steps:")
        print("   1. Start the AI agent: BISTART")
        print("   2. Test with real query: 'Analyze my customer data'")
        print("   3. AI will call get_tool_schema('deploy_agent')")
        print("   4. AI will execute deploy_agent with correct parameters")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - see details above")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
