"""
Fix Microsoft Word Tools to use credential injection pattern
This script updates microsoft_word_tools.py to match the Calendar pattern:
1. Add **kwargs to all function signatures
2. Replace self.headers with self._get_headers(**kwargs)
3. Replace self.access_token references
4. Create global instance and export functions
"""

import re

# Read the file
with open('microsoft_word_tools.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Add **kwargs to all def word_* function signatures (if not already present)
def add_kwargs_to_signature(match):
    signature = match.group(0)
    # Skip if **kwargs already in signature
    if '**kwargs' in signature:
        return signature
    # Find the closing parenthesis before ):
    # Replace ) with , **kwargs)
    if signature.endswith('):'):
        return signature[:-2] + ', **kwargs):'
    return signature

# Match all word_* function definitions
pattern = r'def word_\w+\([^)]*\):'
content = re.sub(pattern, add_kwargs_to_signature, content)

# Step 2: Replace self.headers with self._get_headers(**kwargs)
content = content.replace('headers=self.headers', 'headers=self._get_headers(**kwargs)')

# Step 3: Replace self.access_token in Authorization headers
content = re.sub(
    r'"Authorization":\s*f"Bearer\s+{self\.access_token}"',
    '"Authorization": f"Bearer {self._get_headers(**kwargs)[\'Authorization\'].split(\' \')[1]}"',
    content
)

# Step 4: Replace the get_word_tools() function with global instance pattern
old_export = r'''# ========================================
# TOOL FUNCTION EXPORTS
# ========================================

def get_word_tools\(access_token: str\) -> Dict\[str, callable\]:
    """
    Get all Word tool functions
    
    Args:
        access_token: Microsoft Graph API access token
        
    Returns:
        Dict mapping tool names to functions
    """
    tools = MicrosoftWordTools\(access_token\)
    
    return \{.*?\}'''

# Find the end of the file (after get_word_tools)
# We'll replace everything after the class definition with global instance export

new_export = '''

# ========================================
# GLOBAL INSTANCE AND FUNCTION EXPORTS
# ========================================

# Create global instance
microsoft_word_tools = MicrosoftWordTools()

# Export all functions as module-level attributes for tool registry
word_create_document = microsoft_word_tools.word_create_document
word_get_document = microsoft_word_tools.word_get_document
word_list_documents = microsoft_word_tools.word_list_documents
word_delete_document = microsoft_word_tools.word_delete_document
word_get_content = microsoft_word_tools.word_get_content
word_append_text = microsoft_word_tools.word_append_text
word_search_text = microsoft_word_tools.word_search_text
word_insert_heading = microsoft_word_tools.word_insert_heading
word_insert_table = microsoft_word_tools.word_insert_table
word_insert_image = microsoft_word_tools.word_insert_image
word_apply_style = microsoft_word_tools.word_apply_style
word_add_comment = microsoft_word_tools.word_add_comment
word_get_comments = microsoft_word_tools.word_get_comments
word_export_pdf = microsoft_word_tools.word_export_pdf
word_copy_document = microsoft_word_tools.word_copy_document
word_smart_generate_report = microsoft_word_tools.word_smart_generate_report
word_smart_merge_documents = microsoft_word_tools.word_smart_merge_documents
word_smart_template_fill = microsoft_word_tools.word_smart_template_fill
word_smart_extract_data = microsoft_word_tools.word_smart_extract_data
'''

# Find and replace the exports section
content = re.sub(old_export, new_export, content, flags=re.DOTALL)

# If the regex didn't work, manually find and replace
if 'def get_word_tools' in content:
    # Find the start of the exports section
    export_start = content.find('# ========================================\n# TOOL FUNCTION EXPORTS')
    if export_start != -1:
        content = content[:export_start] + new_export

# Write the fixed file
with open('microsoft_word_tools_FIXED.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed file written to microsoft_word_tools_FIXED.py")
print("Review the file, then rename it to microsoft_word_tools.py")
