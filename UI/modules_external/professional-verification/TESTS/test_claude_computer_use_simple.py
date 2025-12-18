"""
Simple Computer Use Test - Direct API Call
==========================================

Tests if Claude Computer Use API works by making a direct API call.
This doesn't require Docker - just tests the API integration.

RUN: python test_claude_computer_use_simple.py
"""

import sys
import os
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except:
    pass

print("="*80)
print("COMPUTER USE API TEST (Without Docker)")
print("="*80)

# Check API key
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("\n❌ ANTHROPIC_API_KEY not found")
    print("Set it in .env file or environment")
    sys.exit(1)

print(f"\n✅ API key found: {api_key[:20]}...")

# Import Anthropic
try:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    print("✅ Anthropic client initialized")
except Exception as e:
    print(f"❌ Failed to import Anthropic: {e}")
    sys.exit(1)

# Test simple message (no computer use)
print("\n" + "="*80)
print("TEST 1: Simple Claude Message (No Computer Use)")
print("="*80)

try:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": "Say 'Hello! I am Claude Sonnet 4.5 and I'm ready to help!' in one sentence."
        }]
    )
    
    print("\n✅ Claude responded:")
    for block in response.content:
        if hasattr(block, 'text'):
            print(f"   {block.text}")
    
    print(f"\n✅ Model: {response.model}")
    print(f"✅ Stop reason: {response.stop_reason}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

# Test with Computer Use tools (without actual execution)
print("\n" + "="*80)
print("TEST 2: Computer Use Tool Declaration")
print("="*80)

try:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        tools=[{
            "type": "bash_20250124",
            "name": "bash"
        }],
        messages=[{
            "role": "user",
            "content": "I have a website isb.eco. What bash command would you use to check if it's accessible? Just describe, don't execute."
        }]
    )
    
    print("\n✅ Claude's plan:")
    for block in response.content:
        if hasattr(block, 'text'):
            print(f"   {block.text}")
    
    print(f"\n✅ Computer Use tool: Accepted by API")
    print(f"✅ Stop reason: {response.stop_reason}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ ALL TESTS PASSED!")
print("="*80)

print("\n📊 Summary:")
print("   ✅ Anthropic API: Working")
print("   ✅ Claude Sonnet 4.5: Working")
print("   ✅ Computer Use API: Available")
print("\n⚠️  Docker container: Not required for API testing")
print("   Docker is only needed for actual browser automation")

print("\n🎯 What this means:")
print("   - Your verification tools can call Claude for AI analysis ✅")
print("   - Claude can receive Computer Use tool definitions ✅")
print("   - For full browser automation, Docker container needed ⚠️")

print("\n📝 Next steps:")
print("   1. Use Claude for content analysis (works now!)")
print("   2. For form automation: Need Docker container with browser")
print("   3. For database entry: Use auto_enter_to_postgres (no Docker needed)")

print()
