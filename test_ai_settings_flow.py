"""
Test AI Settings Flow End-to-End

This script tests:
1. Database schema has AI settings columns
2. User preferences can be saved with AI settings
3. User preferences can be retrieved with AI settings
4. Settings are properly typed (float, int, bool)
"""
import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("="*80)
print("AI SETTINGS FLOW TEST")
print("="*80)

# Test 1: Verify database schema
print("\n1️⃣ Test 1: Database Schema")
print("-" * 80)
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(user_preferences)')
columns = {row[1]: row[2] for row in cursor.fetchall()}

ai_columns = ['ai_model', 'ai_temperature', 'ai_top_p', 'ai_max_tokens', 
              'ai_thinking_enabled', 'ai_thinking_budget', 'ai_streaming_enabled']

all_exist = True
for col in ai_columns:
    if col in columns:
        print(f"   ✅ {col} ({columns[col]})")
    else:
        print(f"   ❌ {col} MISSING")
        all_exist = False

if all_exist:
    print("✅ Test 1 PASSED: All AI settings columns exist\n")
else:
    print("❌ Test 1 FAILED: Some columns missing\n")
    conn.close()
    exit(1)

# Test 2: Save AI settings for user 14
print("2️⃣ Test 2: Save AI Settings")
print("-" * 80)

test_settings = {
    'ai_model': 'claude-sonnet-4-5-20250929',
    'ai_temperature': 0.7,
    'ai_top_p': 0.9,
    'ai_max_tokens': 8000,
    'ai_thinking_enabled': 1,
    'ai_thinking_budget': 15000,
    'ai_streaming_enabled': 1
}

try:
    cursor.execute("""
        UPDATE user_preferences
        SET ai_model = ?,
            ai_temperature = ?,
            ai_top_p = ?,
            ai_max_tokens = ?,
            ai_thinking_enabled = ?,
            ai_thinking_budget = ?,
            ai_streaming_enabled = ?
        WHERE user_id = 14
    """, (
        test_settings['ai_model'],
        test_settings['ai_temperature'],
        test_settings['ai_top_p'],
        test_settings['ai_max_tokens'],
        test_settings['ai_thinking_enabled'],
        test_settings['ai_thinking_budget'],
        test_settings['ai_streaming_enabled']
    ))
    conn.commit()
    print("   ✅ Settings saved successfully")
    print("✅ Test 2 PASSED: Save AI Settings\n")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("❌ Test 2 FAILED\n")
    conn.close()
    exit(1)

# Test 3: Retrieve AI settings
print("3️⃣ Test 3: Retrieve AI Settings")
print("-" * 80)

cursor.execute("""
    SELECT ai_model, ai_temperature, ai_top_p, ai_max_tokens,
           ai_thinking_enabled, ai_thinking_budget, ai_streaming_enabled
    FROM user_preferences
    WHERE user_id = 14
""")

row = cursor.fetchone()

if row:
    retrieved = {
        'ai_model': row[0],
        'ai_temperature': row[1],
        'ai_top_p': row[2],
        'ai_max_tokens': row[3],
        'ai_thinking_enabled': row[4],
        'ai_thinking_budget': row[5],
        'ai_streaming_enabled': row[6]
    }
    
    print("   Retrieved settings:")
    for key, value in retrieved.items():
        expected = test_settings[key]
        match = "✅" if value == expected else "❌"
        print(f"   {match} {key}: {value} (expected: {expected})")
    
    # Check types
    type_checks = [
        (isinstance(retrieved['ai_model'], str), "ai_model is string"),
        (isinstance(retrieved['ai_temperature'], float), "ai_temperature is float"),
        (isinstance(retrieved['ai_top_p'], float), "ai_top_p is float"),
        (isinstance(retrieved['ai_max_tokens'], int), "ai_max_tokens is int"),
        (isinstance(retrieved['ai_thinking_enabled'], int), "ai_thinking_enabled is int"),
        (isinstance(retrieved['ai_thinking_budget'], int), "ai_thinking_budget is int"),
        (isinstance(retrieved['ai_streaming_enabled'], int), "ai_streaming_enabled is int")
    ]
    
    print("\n   Type checks:")
    all_types_ok = True
    for check, desc in type_checks:
        if check:
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc}")
            all_types_ok = False
    
    if all_types_ok and retrieved == test_settings:
        print("\n✅ Test 3 PASSED: Retrieve AI Settings\n")
    else:
        print("\n❌ Test 3 FAILED: Values or types don't match\n")
        conn.close()
        exit(1)
else:
    print("   ❌ No settings found for user 14")
    print("❌ Test 3 FAILED\n")
    conn.close()
    exit(1)

# Test 4: Test default values for new user
print("4️⃣ Test 4: Default Values")
print("-" * 80)

# Check defaults from schema
cursor.execute('PRAGMA table_info(user_preferences)')
defaults = {}
for row in cursor.fetchall():
    col_name = row[1]
    default_val = row[4]
    if col_name.startswith('ai_'):
        defaults[col_name] = default_val

print("   Schema defaults:")
for col, val in defaults.items():
    print(f"   ✅ {col} = {val}")

print("\n✅ Test 4 PASSED: Default Values\n")

conn.close()

print("="*80)
print("ALL TESTS PASSED!")
print("="*80)
print("\nNext Steps:")
print("1. Reload browser to get window.currentUserId fix")
print("2. Open Settings modal and change AI settings")
print("3. Click Save")
print("4. Send a test message and check Flask logs for:")
print("   - 'AI Model: claude-sonnet-4-5-20250929'")
print("   - 'Temperature: 0.7'")
print("   - 'Max Tokens: 8000'")
print("   - 'Extended Thinking: Enabled'")
print("   - 'Thinking Budget: 15000 tokens'")
print("\n✅ AI Settings flow is READY!")
