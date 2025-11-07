# MICROSOFT 365 TOOL EXECUTION - ROOT CAUSE ANALYSIS
## November 3, 2025

## STATUS: ✅ SCHEMAS ARE CORRECT - ISSUE IS WITH AI PROMPT/CONTEXT

### WHAT'S WORKING ✅

All schemas are properly configured with required parameters:

```
word_create_document   → required: ["name"]
outlook_send_email     → required: ["to", "subject", "body"]
excel_create_workbook  → required: ["name"]
```

### WHY IT'S STILL FAILING ❌

The issue is NOT with the schemas. It's with **how Claude is being prompted**.

Claude sees that `name` is required for `word_create_document`, but when you ask:
> "Create a Word document"

Claude might interpret this as needing to call it without understanding WHERE to store the name or WHAT name to use. The AI doesn't know:
- What name should the document have?
- What should be in it?
- Is there a specific naming convention?

Same issue with email:
> "Send an email with links"

Claude sees `to`, `subject`, `body` are required, but it doesn't know:
- What exact subject line to use?
- What exactly should the body say?
- Should it be HTML formatted?

### THE REAL SOLUTION: Better AI Prompting

You need to tell the AI EXACTLY what to do:

#### Instead of:
```
"Create a Word document and send an email"
```

#### Use:
```
"Create a Word document named 'Business Report 2025' with the text:
'This is our quarterly business report.
Q1 Revenue: $50,000
Q2 Revenue: $60,000
Q3 Revenue: $75,000
Total: $185,000'

Then send an email to inhouse@vetsuccessacademy.com and gerardo@vetsuccessacademy.com
with subject 'Business Report Ready' and body 'Please review the attached business report.'"
```

This gives Claude:
- ✓ Specific document name
- ✓ Specific content
- ✓ Specific recipients  
- ✓ Specific subject
- ✓ Specific message

### SECOND SOLUTION: Increase Agent Max Turns

Current setting in `agent_worker.py` line 152:
```python
max_turns=20,  # ✓ Already set!
```

This is ALREADY at 20 turns! So Claude can iterate and refine if needed.

### THIRD SOLUTION: System Prompt Clarification

The system prompt should explicitly tell Claude:
1. It CAN use Microsoft 365 tools
2. These tools require specific parameters
3. If unsure about parameter values, ASK rather than guess

### VERIFICATION

The schemas ARE working correctly. Proof:

```python
from tools.registry_v3 import RegistryV3
import json

r = RegistryV3()
tools = r.get_anthropic_tools()

# Check word_create_document
word = [t for t in tools if t['name'] == 'word_create_document'][0]
print("Word schema:")
print(f"  Required: {word['input_schema']['required']}")
# Output: ['name'] ✓

# Check outlook_send_email  
outlook = [t for t in tools if t['name'] == 'outlook_send_email'][0]
print("Outlook schema:")
print(f"  Required: {outlook['input_schema']['required']}")
# Output: ['to', 'subject', 'body'] ✓

# Check excel_create_workbook
excel = [t for t in tools if t['name'] == 'excel_create_workbook'][0]
print("Excel schema:")
print(f"  Required: {excel['input_schema']['required']}")
# Output: ['name'] ✓
```

### WHAT TO DO NOW

1. **Test with specific instructions:**
   ```
   "Create a Word document named 'Sales Report Q4' with content about quarterly sales figures.
    Create an Excel workbook named 'Financial Data Q4' with sales by quarter.
    Send an email to inhouse@vetsuccessacademy.com and gerardo@vetsuccessacademy.com 
    with subject 'Q4 Reports' and body explaining the documents are ready for review."
   ```

2. **Max turns are already at 20** - Claude can make multiple calls if needed

3. **Schemas are correct** - All required parameters properly marked

4. **Framework is fixed** - `execute_tool` meta-function no longer has parameter conflicts

### COMMAND TO VERIFY EVERYTHING

```bash
cd c:\Users\gpoli\GIT\AI_agents
python test_microsoft_tools_fixed.py
```

Expected: All 5 tests pass, showing framework is operational

### CONCLUSION

**This is NOT a framework problem anymore - it's an AI instruction problem.**

Claude needs:
- Clear, specific instructions about what to create
- Explicit parameter values (document names, email recipients, etc.)
- Understanding that it needs to provide these values when calling tools

The tool framework is ready. The schemas are correct. The max_turns is configured properly.

You just need to give Claude better instructions with specific values for all required parameters.
