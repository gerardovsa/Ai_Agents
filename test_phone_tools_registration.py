#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Phone Communication Tools Registration
Verifies that phone tools are properly registered and discoverable by AI agents
"""

import sys
import os
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_phone_tools_registration():
    """Test that phone tools are registered in the tool registry"""
    print("\n" + "="*80)
    print("🧪 TESTING PHONE COMMUNICATION TOOLS REGISTRATION")
    print("="*80)
    
    # Import registry
    print("\n📦 Step 1: Importing registry...")
    try:
        from tools.registry_v3 import get_registry
        registry = get_registry()
        print(f"✅ Registry loaded: {len(registry.tools)} total tools")
    except Exception as e:
        print(f"❌ Failed to load registry: {e}")
        return False
    
    # Check if phone tools are in schema
    print("\n📋 Step 2: Checking phone tool schemas...")
    phone_tools = [
        'send_email_veterinary_coaching',
        'send_sms_veterinary_alert',
        'send_bulk_coaching_emails'
    ]
    
    schema_check = True
    for tool_name in phone_tools:
        if tool_name in registry.tools:
            tool_info = registry.tools[tool_name]
            print(f"✅ {tool_name}")
            print(f"   Description: {tool_info.get('short_description', 'N/A')[:80]}...")
            print(f"   Parameters: {len(tool_info.get('parameters', {}).get('properties', {}))} params")
        else:
            print(f"❌ {tool_name} - NOT FOUND in schema")
            schema_check = False
    
    if not schema_check:
        print("\n⚠️  Some tools missing from schema!")
        return False
    
    # Check if implementations are loaded
    print("\n🔧 Step 3: Checking phone tool implementations...")
    impl_check = True
    
    # Check if phone_communication_tools module is loaded
    if 'phone_communication_tools' in registry.implementations:
        impl = registry.implementations['phone_communication_tools']
        print(f"✅ phone_communication_tools module loaded")
        
        # Check if functions exist
        for tool_name in phone_tools:
            if hasattr(impl, tool_name):
                print(f"✅ {tool_name} - implementation found")
            else:
                print(f"❌ {tool_name} - implementation NOT FOUND")
                impl_check = False
    else:
        print(f"❌ phone_communication_tools module NOT LOADED")
        impl_check = False
    
    if not impl_check:
        print("\n⚠️  Some implementations missing!")
        return False
    
    # Test tool execution (dry run - no actual sending)
    print("\n🧪 Step 4: Testing tool discovery by AI...")
    try:
        from tools.implementations.meta_tools import search_tools, get_tool_schema
        
        # Search for phone tools
        search_result = search_tools(query="send email coaching veterinary")
        print(f"✅ search_tools() found {len(search_result.get('results', []))} tools")
        
        # Get schema for email tool
        schema_result = get_tool_schema(tool_name='send_email_veterinary_coaching')
        if schema_result.get('success'):
            print(f"✅ get_tool_schema() retrieved email tool schema")
            # Schema is in the result directly, not nested under 'schema' key
            params = schema_result.get('parameters', {}).get('properties', {})
            print(f"   Parameters: {list(params.keys())}")
        else:
            print(f"❌ get_tool_schema() failed: {schema_result.get('error')}")
            return False
        
        # Get schema for SMS tool
        schema_result = get_tool_schema(tool_name='send_sms_veterinary_alert')
        if schema_result.get('success'):
            print(f"✅ get_tool_schema() retrieved SMS tool schema")
        else:
            print(f"❌ get_tool_schema() failed: {schema_result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Meta-tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check environment variables
    print("\n🔐 Step 5: Checking environment configuration...")
    smtp_vars = ['SMTP_USER', 'SMTP_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    twilio_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_PHONE']
    
    smtp_configured = all(os.getenv(var) for var in ['SMTP_USER', 'SMTP_PASSWORD'])
    twilio_configured = all(os.getenv(var) for var in twilio_vars)
    
    if smtp_configured:
        print(f"✅ SMTP credentials configured")
        print(f"   Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
        print(f"   Port: {os.getenv('SMTP_PORT', '587')}")
        print(f"   User: {os.getenv('SMTP_USER')}")
    else:
        print(f"⚠️  SMTP credentials NOT configured")
        print(f"   Missing: {[var for var in smtp_vars if not os.getenv(var)]}")
    
    if twilio_configured:
        print(f"✅ Twilio credentials configured")
        print(f"   Account SID: {os.getenv('TWILIO_ACCOUNT_SID')[:10]}...")
        print(f"   From Phone: {os.getenv('TWILIO_FROM_PHONE')}")
    else:
        print(f"⚠️  Twilio credentials NOT configured")
        print(f"   Missing: {[var for var in twilio_vars if not os.getenv(var)]}")
    
    # Check Twilio package
    try:
        import twilio
        print(f"✅ Twilio package installed (version {twilio.__version__})")
    except ImportError:
        print(f"⚠️  Twilio package NOT installed")
        print(f"   Install with: pip install twilio")
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Schema Registration: PASSED")
    print(f"✅ Implementation Loading: PASSED")
    print(f"✅ AI Discovery (meta-tools): PASSED")
    print(f"{'✅' if smtp_configured else '⚠️ '} SMTP Configuration: {'COMPLETE' if smtp_configured else 'INCOMPLETE'}")
    print(f"{'✅' if twilio_configured else '⚠️ '} Twilio Configuration: {'COMPLETE' if twilio_configured else 'INCOMPLETE'}")
    
    print("\n🎉 PHONE TOOLS REGISTRATION: SUCCESS")
    print("\n📝 Next Steps:")
    if not smtp_configured:
        print("   1. Configure SMTP credentials (see PHONE_TOOLS_SETUP_GUIDE.md)")
    if not twilio_configured:
        print("   2. Configure Twilio credentials (see PHONE_TOOLS_SETUP_GUIDE.md)")
    print("   3. Test email sending with test_phone_tools_live.py")
    print("   4. AI agents can now discover and use phone tools!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_phone_tools_registration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
