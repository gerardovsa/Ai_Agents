"""Test the new references guide in synergy_agent_instructions"""

from tools.implementations.synergy_instructions import synergy_agent_instructions

# Test the new references topic
result = synergy_agent_instructions('references')

if result['success']:
    print(f"SUCCESS - Guide loaded")
    print(f"Topic: {result['topic']}")
    print(f"Guide length: {len(result['guide'])} characters")
    print("\nFirst 500 characters:")
    print(result['guide'][:500])
else:
    print("FAILED to load guide")
