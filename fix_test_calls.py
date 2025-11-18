"""Fix execute_tool calls in test script"""

with open('test_automation_workflow_tools.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace registry.execute_tool('tool_name' with registry.execute_tool(tool_name='tool_name'
import re
content = re.sub(r"registry\.execute_tool\(\s*'([^']+)'", r"registry.execute_tool(tool_name='\1'", content)

with open('test_automation_workflow_tools.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all execute_tool calls")
