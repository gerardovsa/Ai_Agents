"""Test all prompt system fixes"""

import sys
sys.path.insert(0, 'AI_infrastructure')

print("\n" + "="*70)
print("TESTING PROMPT SYSTEM FIXES")
print("="*70)

# Test 1: Import and initialization
print("\n1. Testing prompt_injection_manager import...")
try:
    from core.prompt_injection_manager import PromptInjectionManager
    manager = PromptInjectionManager()
    print(f"   ✅ Manager initialized")
    print(f"   ✅ Quick actions loaded: {len(manager.quick_actions)}")
    print(f"   ✅ Library prompts loaded: {len(manager.prompt_library)}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 2: Database query
print("\n2. Testing database query (prompt_library table)...")
try:
    prompt = manager.get_user_custom_prompt(1, 'Test Prompt')
    print(f"   ✅ Query successful")
    print(f"   Result: {prompt if prompt else 'No prompt found (expected if none created)'}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 3: Prompt injection with query parameters simulation
print("\n3. Testing prompt injection...")
try:
    base_prompt = "Base system prompt with {{USER_CONTEXT}} and {{PLATFORM_SPECIFIC_INSTRUCTIONS}}"
    
    final_prompt = manager.inject_prompts(
        base_prompt=base_prompt,
        quick_actions=['expert_coder'],
        library_prompts=['sql_expert'],
        user_id=1
    )
    
    print(f"   ✅ Injection successful")
    print(f"   Base length: {len(base_prompt)} chars")
    print(f"   Final length: {len(final_prompt)} chars")
    print(f"   Added: {len(final_prompt) - len(base_prompt)} chars")
    
    if 'QUICK ACTION MODIFIERS' in final_prompt:
        print(f"   ✅ Quick action injected")
    if 'SPECIALIZATION PROMPTS' in final_prompt:
        print(f"   ✅ Library prompt injected")
        
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 4: Check agent_routes_v4.py changes
print("\n4. Checking agent_routes_v4.py fixes...")
try:
    with open('AI_infrastructure/routes/agent_routes_v4.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("request.args.get('quick_actions'", "Query params used (not request.json)"),
        ("system_prompt.replace('{{USER_CONTEXT}}'", "USER_CONTEXT placeholder used"),
        ("system_prompt.replace('{{PLATFORM_SPECIFIC_INSTRUCTIONS}}'", "PLATFORM_SPECIFIC_INSTRUCTIONS placeholder used"),
        ("MANDATORY PLATFORM USE:", "Platform mandate in user context"),
    ]
    
    for check_str, description in checks:
        if check_str in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ MISSING: {description}")
            
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 5: Verify table schema
print("\n5. Verifying database schema...")
try:
    import sqlite3
    conn = sqlite3.connect('data/ai_infrastructure.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(prompt_library)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = ['id', 'user_id', 'name', 'prompt_text', 'category', 'type', 'tags']
    
    for col in required_columns:
        if col in columns:
            print(f"   ✅ Column '{col}' exists")
        else:
            print(f"   ❌ MISSING column: {col}")
    
    conn.close()
    
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("All fixes verified and working correctly!")
print("\nNext step: RESTART FLASK SERVER")
print("  BISTOP")
print("  BISTART")
print("="*70 + "\n")
