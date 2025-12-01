"""
Test Vector Database with credential injection from Platform Connections
"""

from tools.registry_v3 import RegistryV3

# Initialize registry
registry = RegistryV3()

print("\n=== TESTING VECTOR DATABASE WITH CREDENTIALS ===\n")

# Test 1: List namespaces (should work with user_id=1 who has Pinecone credentials)
print("1. Testing vector_db_list_namespaces with user_id=1...")
try:
    result = registry.execute_tool(
        tool_name='vector_db_list_namespaces',
        _user_id=1,  # This user has Pinecone + Voyager AI + OpenAI credentials in database
        _injected_credentials=True
    )
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== TEST COMPLETE ===\n")
