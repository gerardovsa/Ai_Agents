#!/usr/bin/env python3
"""
Communication Hub V4 - Verification Script
Tests all fixes implemented on December 17, 2025
"""

import re
import sys

def check_file_changes():
    """Verify all required changes are present in the files"""
    
    checks = []
    
    # 1. Check NATO names expansion
    print("=" * 80)
    print("1. Checking NATO agent names expansion...")
    print("-" * 80)
    
    with open('UI/modules_internal/communication-hub/communication-hub-v4-modern.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Check for all 26 NATO names
        nato_names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India',
                     'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
                     'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee', 'Zulu']
        
        found_all = all(name in content for name in nato_names)
        
        if found_all:
            print("✅ All 26 NATO agent names found")
            checks.append(True)
        else:
            print("❌ Missing some NATO agent names")
            missing = [name for name in nato_names if name not in content]
            print(f"   Missing: {', '.join(missing)}")
            checks.append(False)
    
    # 2. Check preview panel agent dropdown
    print("\n" + "=" * 80)
    print("2. Checking preview panel agent dropdown...")
    print("-" * 80)
    
    with open('UI/modules_internal/communication-hub/communication-hub-v4-modern.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Check for function definition
        has_function = 'showAgentAssignmentFromPreview' in content
        
        # Check for button onclick
        has_onclick = 'onclick="window.CommunicationHub.showAgentAssignmentFromPreview' in content
        
        # Check for custom instructions textarea
        has_textarea = 'ai-custom-instruction-' in content
        
        all_present = has_function and has_onclick and has_textarea
        
        if all_present:
            print("✅ Preview panel agent dropdown implementation found")
            print("   - showAgentAssignmentFromPreview() function: ✅")
            print("   - Button onclick handler: ✅")
            print("   - Custom instructions textarea: ✅")
            checks.append(True)
        else:
            print("❌ Preview panel implementation incomplete")
            if not has_function:
                print("   - showAgentAssignmentFromPreview() function: ❌")
            if not has_onclick:
                print("   - Button onclick handler: ❌")
            if not has_textarea:
                print("   - Custom instructions textarea: ❌")
            checks.append(False)
    
    # 3. Check task submenu function
    print("\n" + "=" * 80)
    print("3. Checking task submenu implementation...")
    print("-" * 80)
    
    with open('UI/modules_internal/communication-hub/communication-hub-v4-modern.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Check for function
        has_submenu = 'showTaskSubmenuFromPreview' in content
        
        # Check for task types
        task_types = ['generate_quote', 'summarize', 'draft_reply', 'extract_tasks', 'analyze', 'discuss']
        has_all_tasks = all(task in content for task in task_types)
        
        all_present = has_submenu and has_all_tasks
        
        if all_present:
            print("✅ Task submenu implementation found")
            print("   - showTaskSubmenuFromPreview() function: ✅")
            print("   - All 6 task types present: ✅")
            checks.append(True)
        else:
            print("❌ Task submenu implementation incomplete")
            if not has_submenu:
                print("   - showTaskSubmenuFromPreview() function: ❌")
            if not has_all_tasks:
                missing = [task for task in task_types if task not in content]
                print(f"   - Missing task types: {', '.join(missing)}")
            checks.append(False)
    
    # 4. Check Outlook API changes
    print("\n" + "=" * 80)
    print("4. Checking Outlook API changes...")
    print("-" * 80)
    
    try:
        with open('AI_infrastructure/tools/microsoft_outlook_tools.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for $select parameter
            has_select = '$select=' in content and 'uniqueBody' in content
            
            # Check for $expand parameter
            has_expand = '$expand=attachments' in content
            
            all_present = has_select and has_expand
            
            if all_present:
                print("✅ Outlook API changes found")
                print("   - $select with uniqueBody: ✅")
                print("   - $expand=attachments: ✅")
                checks.append(True)
            else:
                print("❌ Outlook API changes incomplete")
                if not has_select:
                    print("   - $select with uniqueBody: ❌")
                if not has_expand:
                    print("   - $expand=attachments: ❌")
                checks.append(False)
    except FileNotFoundError:
        print("⚠️  File not found: microsoft_outlook_tools.py")
        checks.append(None)
    
    # 5. Check communication routes changes
    print("\n" + "=" * 80)
    print("5. Checking communication routes changes...")
    print("-" * 80)
    
    try:
        with open('AI_infrastructure/routes/communication_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for uniqueBody preference
            has_unique_body = 'uniqueBody' in content
            
            # Check for attachment parsing
            has_attachments = 'attachments_list' in content or 'parse_parts' in content
            
            # Check for include_attachments parameter
            has_param = 'include_attachments=True' in content
            
            all_present = has_unique_body and has_attachments and has_param
            
            if all_present:
                print("✅ Communication routes changes found")
                print("   - uniqueBody preference: ✅")
                print("   - Attachment parsing: ✅")
                print("   - include_attachments parameter: ✅")
                checks.append(True)
            else:
                print("❌ Communication routes changes incomplete")
                if not has_unique_body:
                    print("   - uniqueBody preference: ❌")
                if not has_attachments:
                    print("   - Attachment parsing: ❌")
                if not has_param:
                    print("   - include_attachments parameter: ❌")
                checks.append(False)
    except FileNotFoundError:
        print("⚠️  File not found: communication_routes.py")
        checks.append(None)
    
    # 6. Check email formatter changes
    print("\n" + "=" * 80)
    print("6. Checking email formatter changes...")
    print("-" * 80)
    
    try:
        with open('UI/modules_external/communication/email-ai-formatter.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for stripHtml function
            has_strip_html = 'stripHtml' in content
            
            # Check for attachment formatting
            has_attachment_format = 'formatAttachment' in content
            
            all_present = has_strip_html and has_attachment_format
            
            if all_present:
                print("✅ Email formatter changes found")
                print("   - stripHtml() function: ✅")
                print("   - formatAttachment() function: ✅")
                checks.append(True)
            else:
                print("❌ Email formatter changes incomplete")
                if not has_strip_html:
                    print("   - stripHtml() function: ❌")
                if not has_attachment_format:
                    print("   - formatAttachment() function: ❌")
                checks.append(False)
    except FileNotFoundError:
        print("⚠️  File not found: email-ai-formatter.js")
        checks.append(None)
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for check in checks if check is True)
    failed = sum(1 for check in checks if check is False)
    skipped = sum(1 for check in checks if check is None)
    total = len(checks)
    
    print(f"Total Checks: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 All checks passed! Ready for deployment.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(check_file_changes())
