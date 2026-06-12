"""Test if system prompt has the meta-tool fix"""
from pathlib import Path

# Just read the prompt file directly
prompt_path = Path("AI_infrastructure/prompts/tool_usage_system_prompt.md")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt = f.read()

print(f"Prompt size: {len(prompt):,} characters")
print(f"\nMeta-tool fix present: {'execute_tool(tool_name=\"search_tools\"' in prompt}")
print(f"Old incorrect pattern present: {('search_tools(\"' in prompt) and ('execute_tool(tool_name=\"search_tools\"' not in prompt)}")

# Check for the warning section
has_warning = "CRITICAL: META-TOOL USAGE RULES" in prompt
print(f"Warning section present: {has_warning}")

# Show first 200 chars of the search_tools section
if "search_tools" in prompt:
    idx = prompt.find("search_tools")
    snippet = prompt[max(0, idx-50):idx+150]
    print(f"\nSearch tools context:\n{snippet}")
