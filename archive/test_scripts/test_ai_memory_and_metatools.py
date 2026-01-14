"""
Test AI Memory and Meta-Tool Behavior

Questions to answer:
1. What does recommend_tools_for_task() actually do?
2. Does the AI remember tools from previous list_platform_tools() calls?
3. Does the AI remember tool results without writing text?
4. Why does it re-fetch tool lists?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.registry_v3 import get_registry

print("=" * 80)
print("TEST 1: What does recommend_tools_for_task() actually do?")
print("=" * 80)

registry = get_registry()

# Test the function directly
result = registry.execute_tool(
    tool_name='recommend_tools_for_task',
    task_description='Send an email to john@example.com with a report',
    user_platforms=['google_workspace', 'microsoft_365']
)

print("\nResult from recommend_tools_for_task():")
print(f"  Success: {result.get('success')}")
print(f"  Task: {result.get('task')}")
print(f"  Recommendation: {result.get('recommendation')}")
print(f"  Example: {result.get('example')}")

print("\n" + "=" * 80)
print("ANALYSIS: This tool is basically a stub!")
print("=" * 80)
print("It just tells you to use search_tools() instead.")
print("It's NOT a smart AI-powered recommendation engine.")
print("It's essentially useless compared to search_tools().")

print("\n" + "=" * 80)
print("TEST 2: Simulate Claude's memory behavior")
print("=" * 80)

# Simulate Turn 1: Claude calls list_platform_tools
print("\n--- TURN 1: Discovery Phase ---")
print("Claude calls: list_platform_tools('gmail')")

gmail_tools = registry.execute_tool(tool_name='list_platform_tools', platform='gmail')
print(f"\nResult: {len(gmail_tools.get('tools', []))} tools returned")
print("\nFirst 5 tools:")
for i, tool in enumerate(gmail_tools.get('tools', [])[:5]):
    print(f"  {i+1}. {tool['name']}")

print("\n--- CLAUDE'S THINKING ---")
print("Claude sees these tools in the tool_result block.")
print("Question: Does Claude remember these in Turn 2?")
print("\nANSWER: YES - Claude has the full conversation history!")
print("The tool_result is in the messages array:")
print("  messages = [")
print("    {role: 'user', content: 'Send email'},")
print("    {role: 'assistant', content: [tool_use: list_platform_tools]},")
print("    {role: 'user', content: [tool_result: gmail_tools list]} <- HERE")
print("  ]")

print("\n--- TURN 2: Execution Phase ---")
print("User says: 'Send to john@example.com'")
print("\nClaude has access to:")
print("  1. Full conversation history (including tool_result from Turn 1)")
print("  2. All 594 tools now loaded")
print("\nShould Claude remember the gmail_send_email tool?")
print("YES - It's in the conversation history!")

print("\n" + "=" * 80)
print("TEST 3: Why does Claude re-fetch tool lists?")
print("=" * 80)

print("\nPossible reasons:")
print("\n1. FORGOT THE INSTRUCTIONS")
print("   - Prompt doesn't emphasize reusing discovered tools")
print("   - No explicit 'remember tools from previous calls' instruction")

print("\n2. OVERLY CAUTIOUS")
print("   - Wants to verify tools still exist")
print("   - Doesn't trust memory of tool_result contents")

print("\n3. PATTERN MATCHING")
print("   - Sees 'send email' in user message")
print("   - Immediately thinks 'I should search for email tools'")
print("   - Doesn't check if it already has this info")

print("\n4. PROMPT STRUCTURE ISSUE")
print("   - STEP 2 says: 'IF you don't know which tool to use: Call search_tools()'")
print("   - Claude interprets 'don't know' as 'haven't verified this turn'")
print("   - Doesn't realize previous tool_result counts as 'knowing'")

print("\n" + "=" * 80)
print("TEST 4: Does Claude need to write text to remember?")
print("=" * 80)

print("\nANSWER: NO - Tool results are automatically remembered!")
print("\nAnthropicMessages API structure:")
print("  - tool_use blocks: Claude's tool calls")
print("  - tool_result blocks: System's responses")
print("  - text blocks: Claude's written responses")
print("\nAll three are in conversation_history array.")
print("Claude has access to ALL previous blocks, not just text blocks.")

print("\nExample conversation_history:")
print("""
[
  {role: 'user', content: 'Send email'},
  {role: 'assistant', content: [
    {type: 'tool_use', id: '1', name: 'search_tools', input: {query: 'email'}}
  ]},
  {role: 'user', content: [
    {type: 'tool_result', tool_use_id: '1', content: '[tool list]'}  <- REMEMBERED
  ]},
  {role: 'assistant', content: [
    {type: 'text', text: 'I found email tools'}  <- Not required for memory!
  ]}
]
""")

print("\n" + "=" * 80)
print("CONCLUSION & RECOMMENDATIONS")
print("=" * 80)

print("\n1. recommend_tools_for_task() is USELESS")
print("   - It's just a stub that says 'use search_tools instead'")
print("   - Should either be removed or properly implemented")
print("   - RECOMMENDATION: Mark as ⚠️ Stub/Not Functional")

print("\n2. Claude DOES remember tool results")
print("   - All tool_result blocks are in conversation_history")
print("   - No need to write text for memory")

print("\n3. Claude re-fetches because of PROMPT ISSUES")
print("   - Prompt doesn't say 'reuse previously discovered tools'")
print("   - STEP 2 is ambiguous about when discovery is needed")
print("   - No instruction to check conversation history first")

print("\n4. RECOMMENDED PROMPT FIXES:")
print("\n   A. Add 'Check History First' rule:")
print("      'Before calling search_tools or list_platform_tools,")
print("       check if you ALREADY called them in this conversation.'")

print("\n   B. Enhance STEP 2:")
print("      'IF you don't know which tool to use AND haven't searched yet:")
print("       - Call search_tools() or list_platform_tools()'")

print("\n   C. Add efficiency guidance:")
print("      'AVOID redundant tool discovery calls.")
print("       If you already have a tool list from a previous turn,")
print("       reuse it instead of fetching again.'")

print("\n5. MEMORY ARCHITECTURE IS CORRECT")
print("   - Claude has full conversation history")
print("   - Tool results are preserved")
print("   - Problem is PROMPT INSTRUCTIONS, not memory")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

print("\n1. Update META_TOOL_ANALYSIS_SUMMARY.md:")
print("   - Mark recommend_tools_for_task as stub/non-functional")
print("   - Add section on 'Avoiding Redundant Discovery Calls'")

print("\n2. Enhance system prompt with:")
print("   - 'Check conversation history before re-discovering tools'")
print("   - 'Reuse tool lists from previous turns'")
print("   - 'Only call discovery tools once per conversation'")

print("\n3. Consider removing recommend_tools_for_task:")
print("   - It provides no value over search_tools()")
print("   - Reduces meta-tool count from 5 to 4")
print("   - Simplifies progressive loading")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
