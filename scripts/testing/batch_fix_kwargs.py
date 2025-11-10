"""
Batch fix Google Workspace functions to add **kwargs

This script automatically adds **kwargs to function signatures
"""

import re
from pathlib import Path

def fix_function_signature(content, function_name):
    """Add **kwargs to a function signature if missing"""
    
    # Pattern to match function definition (handle multi-line)
    pattern = rf'(def {re.escape(function_name)}\([^)]*?)(\)):'
    
    def replacer(match):
        params = match.group(1)
        closing_paren = match.group(2)
        
        # Check if already has **kwargs
        if '**kwargs' in params or '**' in params:
            return match.group(0)  # No change needed
        
        # Add **kwargs before closing paren
        if params.strip().endswith(','):
            return f"{params} **kwargs{closing_paren}:"
        elif params.strip().endswith('('):
            # No parameters yet
            return f"{params}**kwargs{closing_paren}:"
        else:
            # Has parameters
            return f"{params}, **kwargs{closing_paren}:"
    
    # Handle multi-line function signatures
    # First, try to find the function and its full signature
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a function definition
        if f'def {function_name}(' in line:
            # Collect full signature (handle multi-line)
            signature = line
            while not signature.rstrip().endswith(':'):
                i += 1
                if i >= len(lines):
                    break
                signature += '\n' + lines[i]
            
            # Check if **kwargs already present
            if '**kwargs' not in signature and '**' not in signature:
                # Find the closing paren before the colon
                if signature.rstrip().endswith('):'):
                    # Check if there are parameters
                    if signature.count('(') == signature.count(')'):
                        # Simple case - single line or already collected
                        paren_pos = signature.rfind(')')
                        colon_pos = signature.rfind(':')
                        
                        # Insert **kwargs before the closing paren
                        before_paren = signature[:paren_pos]
                        after_paren = signature[paren_pos:]
                        
                        # Check if we need a comma
                        if before_paren.rstrip().endswith(','):
                            signature = before_paren + ' **kwargs' + after_paren
                        elif before_paren.rstrip().endswith('('):
                            signature = before_paren + '**kwargs' + after_paren
                        else:
                            signature = before_paren + ', **kwargs' + after_paren
            
            result_lines.append(signature)
        else:
            result_lines.append(line)
        
        i += 1
    
    return '\n'.join(result_lines)

def fix_file(file_path, functions_to_fix):
    """Fix all functions in a file"""
    print(f"\nFixing {file_path.name}...")
    print(f"Functions to fix: {len(functions_to_fix)}")
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    
    for func_name in functions_to_fix:
        print(f"  Fixing: {func_name}")
        content = fix_function_signature(content, func_name)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file_path.name}")
        return True
    else:
        print(f"No changes needed for {file_path.name}")
        return False

def main():
    base_path = Path(r'C:\Users\gpoli\GIT\AI_agents\google_workspace')
    
    # Google Forms - all 86 functions
    forms_functions = [
        'google_forms_create_form', 'google_forms_get_form', 'google_forms_add_question',
        'google_forms_add_multiple_choice', 'google_forms_add_text_question',
        'google_forms_add_linear_scale', 'google_forms_update_question',
        'google_forms_delete_question', 'google_forms_get_responses',
        'google_forms_get_response', 'google_forms_delete_response',
        'google_forms_update_settings', 'google_forms_export_responses_csv',
        'google_forms_create_quiz', 'google_forms_add_quiz_question',
        'google_forms_delete_form', 'google_forms_clone_form',
        'google_forms_update_info', 'google_forms_set_settings',
        'google_forms_add_checkbox', 'google_forms_add_dropdown',
        'google_forms_add_date_question', 'google_forms_add_time_question',
        'google_forms_add_grid', 'google_forms_add_file_upload',
        'google_forms_move_question', 'google_forms_add_section',
        'google_forms_add_description', 'google_forms_add_image',
        'google_forms_add_video', 'google_forms_delete_all_responses',
        'google_forms_set_quiz_settings', 'google_forms_grade_response',
        'google_forms_add_validation', 'google_forms_set_question_description',
        'google_forms_shuffle_options', 'google_forms_set_other_option',
        'google_forms_set_accepts_response', 'google_forms_export_responses_json',
        'google_forms_get_summary_statistics', 'google_forms_link_to_sheets',
        'google_forms_create_watch', 'google_forms_delete_watch',
        'google_forms_list_watches', 'google_forms_renew_watch',
        'google_forms_bulk_create_forms', 'google_forms_create_from_template',
        'google_forms_clone_multiple', 'google_forms_batch_add_questions',
        'google_forms_batch_update_questions', 'google_forms_batch_delete_questions',
        'google_forms_reorder_questions', 'google_forms_batch_delete_responses',
        'google_forms_export_all_responses', 'google_forms_analyze_responses_bulk',
        'google_forms_batch_update_settings', 'google_forms_batch_open_close',
        'google_forms_ai_generate_from_prompt', 'google_forms_ai_generate_survey',
        'google_forms_ai_generate_quiz', 'google_forms_ai_generate_registration',
        'google_forms_ai_optimize_questions', 'google_forms_ai_suggest_questions',
        'google_forms_ai_translate_form', 'google_forms_ai_generate_multilingual',
        'google_forms_ai_analyze_responses', 'google_forms_ai_sentiment_analysis',
        'google_forms_ai_categorize_responses', 'google_forms_ai_extract_insights',
        'google_forms_ai_generate_report', 'google_forms_ai_detect_spam',
        'google_forms_ai_flag_priority', 'google_forms_ai_auto_respond',
        'google_forms_ai_suggest_improvements', 'google_forms_extract_entry_ids',
        'google_forms_submit_response_http', 'google_forms_bulk_submit_responses',
        'google_forms_auto_test', 'google_forms_export_with_metadata',
        'google_forms_sync_to_sheets', 'google_forms_export_pdf_report',
        'google_forms_inject_custom_html', 'google_forms_set_custom_theme',
        'google_forms_create_complete_form', 'google_forms_ai_generate_form',
        'google_forms_bulk_create_multiple'
    ]
    
    # Run fix
    forms_path = base_path / 'google_forms.py'
    if forms_path.exists():
        fix_file(forms_path, forms_functions)
    else:
        print(f"File not found: {forms_path}")

if __name__ == '__main__':
    main()
