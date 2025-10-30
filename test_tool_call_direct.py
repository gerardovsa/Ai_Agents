"""Direct test of Anthropic API with tools"""
import os
from anthropic import Anthropic

# Initialize client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Define ONE simple tool for testing
tools = [
    {
        "name": "list_platform_tools",
        "description": "List available tools for specified platforms",
        "input_schema": {
            "type": "object",
            "properties": {
                "platforms": {
                    "type": "array",
                    "description": "Platform names to list tools for",
                    "items": {"type": "string"}
                }
            },
            "required": ["platforms"]
        }
    }
]

print("=" * 80)
print("DIRECT ANTHROPIC API TOOL CALL TEST")
print("=" * 80)

# Make API call with tools
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto"},  # Important!
    messages=[
        {
            "role": "user",
            "content": "What platforms do you have tools for?"
        }
    ]
)

print("\n📊 RESPONSE ANALYSIS:")
print(f"   Stop reason: {response.stop_reason}")
print(f"   Content blocks: {len(response.content)}")

for i, block in enumerate(response.content):
    print(f"\n   Block {i+1}:")
    print(f"      Type: {block.type}")
    
    if block.type == "text":
        print(f"      Text: {block.text[:200]}")
    elif block.type == "tool_use":
        print(f"      ✅ TOOL CALL DETECTED!")
        print(f"      Tool name: {block.name}")
        print(f"      Tool ID: {block.id}")
        print(f"      Input: {block.input}")

if response.stop_reason == "tool_use":
    print("\n✅ SUCCESS: Claude is using tools correctly!")
else:
    print(f"\n❌ PROBLEM: Stop reason is '{response.stop_reason}', not 'tool_use'")
    print("   This means Claude isn't calling tools properly")

print("\n" + "=" * 80)