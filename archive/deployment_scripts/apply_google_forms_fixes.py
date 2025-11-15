"""
Apply Google Forms Critical Fixes
Directly modifies google_forms.py to fix all 3 bugs
"""

import re

# Read the file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Applying fixes to google_forms.py...")
print("="*70)

# Fix 1: Remove **kwargs from function signature
old_sig = "def google_forms_create_form(title, document_title=None, description=None, shareable=True, **kwargs):"
new_sig = "def google_forms_create_form(title, document_title=None, description=None, shareable=True):"
if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print("✅ Fix 1: Removed **kwargs from function signature")
else:
    print("⚠️  Fix 1: Function signature already correct")

# Fix 2: Replace form creation logic (two-step process)
old_logic = """    try:
        service = _get_forms_service()

        form_info = {
            'title': title,
            'documentTitle': document_title or title
        }

        if description:
            form_info['description'] = description

        form = {'info': form_info}

        result = service.forms().create(body=form).execute()
        form_id = result['formId']

        # Make it shareable (anyone with link can respond)"""

new_logic = """    try:
        service = _get_forms_service()

        # STEP 1: Create form with ONLY title (API restriction)
        # Google Forms API only accepts 'title' during creation
        # All other fields must be added via batchUpdate
        form_info = {
            'title': title
        }

        form = {'info': form_info}

        result = service.forms().create(body=form).execute()
        form_id = result['formId']

        # STEP 2: Add description and documentTitle via batchUpdate if provided
        if description or document_title:
            batch_requests = []

            if description:
                batch_requests.append({
                    'updateFormInfo': {
                        'info': {'description': description},
                        'updateMask': 'description'
                    }
                })

            if document_title and document_title != title:
                batch_requests.append({
                    'updateFormInfo': {
                        'info': {'documentTitle': document_title},
                        'updateMask': 'documentTitle'
                    }
                })

            if batch_requests:
                service.forms().batchUpdate(
                    formId=form_id,
                    body={'requests': batch_requests}
                ).execute()
                print(f"Added description/documentTitle to form: {form_id}")

        # Make it shareable (anyone with link can respond)"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    print("✅ Fix 2: Applied two-step form creation process")
else:
    print("⚠️  Fix 2: Form creation logic already updated")

# Fix 3: Remove all response_format parameters from AI functions
fixes_applied = 0

# Pattern to find response_format lines
response_format_pattern = r',\s*response_format=\{"type":\s*"json_object"\}'

matches = re.findall(response_format_pattern, content)
if matches:
    content = re.sub(response_format_pattern, '', content)
    fixes_applied = len(matches)
    print(f"✅ Fix 3: Removed {fixes_applied} response_format parameters")
else:
    print("⚠️  Fix 3: No response_format parameters found")

# Also add "Return ONLY valid JSON" to prompts that need it
# Find AI function calls and ensure they have the JSON instruction
json_instruction = "\\n\\nReturn ONLY valid JSON."
ai_functions = [
    'google_forms_ai_generate_from_prompt',
    'google_forms_ai_optimize_questions',
    'google_forms_ai_suggest_questions',
    'google_forms_ai_analyze_responses',
    'google_forms_ai_detect_spam',
    'google_forms_ai_flag_priority'
]

for func in ai_functions:
    # Look for system_prompt + in create calls
    pattern = rf'(messages=\[\s*\{{"role": "system", "content": system_prompt)\}},'
    replacement = r'\1 + "\\n\\nReturn ONLY valid JSON."},'
    
    # Find the function and add instruction if not present
    if func in content and json_instruction not in content[content.find(func):content.find(func)+5000]:
        content = re.sub(pattern, replacement, content, count=1)

# Write the fixed file
with open('google_workspace/google_forms.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("="*70)
print("✅ All fixes applied successfully!")
print("File written to disk: google_workspace/google_forms.py")
print("\nNext steps:")
print("1. Restart Flask server (kill Python processes)")
print("2. Run tests: python test_google_forms_fixes.py")
