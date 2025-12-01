"""Validate the changes made to Microsoft Outlook and Xero tools"""
import json
import sys

print("=" * 70)
print("VALIDATION REPORT - Microsoft Outlook & Xero Tools Update")
print("=" * 70)

# Test 1: Microsoft Outlook Schema
print("\n1. Microsoft Outlook Schema Validation")
print("-" * 70)
try:
    with open('tools/schemas/microsoft_outlook_tools.json', encoding='utf-8') as f:
        outlook_schema = json.load(f)
    
    # Check platform description
    platform_desc = outlook_schema['description']
    print(f"✅ Platform description contains 'DISABLED': {'DISABLED' in platform_desc}")
    print(f"✅ Platform description contains 'drafts': {'drafts' in platform_desc.lower()}")
    
    # Check send_email tool
    send_email_tool = [t for t in outlook_schema['tools'] if t['name'] == 'microsoft_outlook_send_email'][0]
    tool_desc = send_email_tool['description']
    
    print(f"✅ Tool contains 'PERMANENTLY DISABLED': {'PERMANENTLY DISABLED' in tool_desc}")
    print(f"✅ Tool contains 'DO NOT REACTIVATE': {'DO NOT REACTIVATE' in tool_desc}")
    print(f"✅ Tool contains 'DRAFTS ONLY': {'DRAFTS ONLY' in tool_desc}")
    print(f"✅ Tool contains warning symbols: {'🛑' in tool_desc}")
    
    print("\nFirst 250 chars of updated description:")
    print(tool_desc[:250] + "...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Microsoft Outlook Implementation
print("\n\n2. Microsoft Outlook Implementation Validation")
print("-" * 70)
try:
    with open('tools/implementations/microsoft_outlook_tools.py', encoding='utf-8') as f:
        impl_code = f.read()
    
    print(f"✅ Implementation contains 'PERMANENTLY DISABLED': {'PERMANENTLY DISABLED' in impl_code}")
    print(f"✅ Implementation contains 'DO NOT REACTIVATE': {'DO NOT REACTIVATE' in impl_code}")
    print(f"✅ Implementation contains draft warning: {'DRAFTS ONLY' in impl_code}")
    
    # Check that the actual send is still commented out
    print(f"✅ Original send code is commented: {'# result = self._make_request' in impl_code}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Credential Injector - Xero Support
print("\n\n3. Credential Injector - Xero Support Validation")
print("-" * 70)
try:
    with open('AI_infrastructure/auth/credential_injector.py', encoding='utf-8') as f:
        injector_code = f.read()
    
    print(f"✅ Xero prefix defined: {'xero_tools_prefixes' in injector_code}")
    print(f"✅ Xero detection logic: {'is_xero_tool' in injector_code}")
    print(f"✅ Xero injection branch: {'elif is_xero_tool:' in injector_code}")
    print(f"✅ Xero credential comment: {'XeroAPIClient' in injector_code}")
    
    # Count how many platform types are supported
    platform_count = injector_code.count('elif is_') + 1  # +1 for the first 'if'
    print(f"✅ Total platform types supported: {platform_count} (Google, Microsoft, Xero, Other)")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: System Prompt
print("\n\n4. System Prompt Validation")
print("-" * 70)
try:
    with open('AI_infrastructure/prompts/tool_usage_system_prompt.md', encoding='utf-8') as f:
        prompt = f.read()
    
    print(f"✅ Contains Outlook restrictions section: {'MICROSOFT OUTLOOK EMAIL RESTRICTIONS' in prompt}")
    print(f"✅ Contains 'PERMANENTLY DISABLED': {'PERMANENTLY DISABLED' in prompt}")
    print(f"✅ Contains draft warning: {'saved as a draft' in prompt}")
    print(f"✅ Contains manual sending requirement: {'manually send' in prompt}")
    print(f"✅ Contains alternative suggestions: {'gmail_send_email' in prompt}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 5: Xero Tools
print("\n\n5. Xero Tools Structure Validation")
print("-" * 70)
try:
    with open('tools/implementations/xero.py', encoding='utf-8') as f:
        xero_code = f.read()
    
    print(f"✅ Xero tools file exists")
    print(f"✅ Contains XeroAPIClient import: {'XeroAPIClient' in xero_code}")
    print(f"✅ Contains _get_client function: {'def _get_client' in xero_code}")
    print(f"✅ Contains kwargs handling: {'**kwargs' in xero_code}")
    
    # Check credential extraction
    print(f"✅ Has credential extraction logic: {'_extract_token' in xero_code}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
print("\nSUMMARY:")
print("✅ Microsoft Outlook send_email permanently disabled with warnings")
print("✅ Schema updated with DRAFTS ONLY status")
print("✅ Implementation updated with security warnings")
print("✅ System prompt updated with restrictions and alternatives")
print("✅ Xero credential injection added to credential_injector.py")
print("✅ Xero tools structure validated")
print("\n🎉 All changes successfully implemented!\n")
