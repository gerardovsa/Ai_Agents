"""
Verify Stream Fix - Check for remaining session_id references
Created: November 19, 2025 11:45 PM

Purpose: Scan agent_routes_v4.py for any remaining undefined session_id references
         in the stream_agent() function scope.

Expected: Should find ZERO undefined references after fix
"""

import re

def analyze_stream_function():
    """Analyze stream_agent() function for variable references"""
    
    with open('AI_infrastructure/routes/agent_routes_v4.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find stream_agent function bounds
    in_stream_function = False
    stream_start = 0
    stream_end = 0
    
    for i, line in enumerate(lines, 1):
        if 'def stream_agent(agent_id):' in line:
            in_stream_function = True
            stream_start = i
            print(f"✅ Found stream_agent() function at line {i}")
        
        if in_stream_function and line.startswith('def ') and i > stream_start:
            stream_end = i - 1
            break
    
    if not stream_end:
        stream_end = len(lines)
    
    print(f"   Function spans lines {stream_start}-{stream_end} ({stream_end - stream_start} lines)\n")
    
    # Check for thread_slug definition
    thread_slug_defined = False
    session_id_defined = False
    
    for i in range(stream_start, min(stream_start + 30, stream_end)):
        line = lines[i - 1]
        if 'thread_slug = ' in line and '=' in line:
            thread_slug_defined = True
            print(f"✅ thread_slug defined at line {i}: {line.strip()}")
        if 'session_id = ' in line and 'request.' in line:
            session_id_defined = True
            print(f"⚠️  session_id defined at line {i}: {line.strip()}")
    
    print()
    
    # Find all references to session_id in function scope
    session_id_refs = []
    thread_slug_refs = []
    
    for i in range(stream_start, stream_end):
        line = lines[i - 1]
        
        # Skip comments and strings
        if line.strip().startswith('#'):
            continue
        
        # Find session_id references (excluding assignments)
        if 'session_id' in line:
            # Skip definition line
            if 'thread_slug = request.args.get' in line:
                continue
            # Skip parameter names in function definitions
            if 'def ' in line and 'session_id' in line:
                continue
            # This is a reference
            session_id_refs.append((i, line.strip()))
        
        if 'thread_slug' in line:
            thread_slug_refs.append((i, line.strip()))
    
    print(f"📊 Analysis Results:\n")
    print(f"   thread_slug defined: {'✅ YES' if thread_slug_defined else '❌ NO'}")
    print(f"   session_id defined: {'⚠️  YES' if session_id_defined else '✅ NO (good)'}")
    print(f"   thread_slug references: {len(thread_slug_refs)}")
    print(f"   session_id references: {len(session_id_refs)}\n")
    
    # Analyze session_id references
    print("🔍 Detailed session_id Reference Analysis:\n")
    
    valid_refs = 0
    invalid_refs = 0
    
    for line_num, line_content in session_id_refs:
        # Check if this is a valid reference
        is_valid = False
        
        # Valid patterns:
        # 1. Parameter name in function call: session_id=thread_slug
        if 'session_id=' in line_content and 'thread_slug' in line_content:
            is_valid = True
            reason = "Parameter passing (session_id=thread_slug)"
        
        # 2. Dictionary key: 'session_id': thread_slug
        elif "'session_id':" in line_content and 'thread_slug' in line_content:
            is_valid = True
            reason = "Dict key with thread_slug value"
        
        # 3. Comment or docstring
        elif line_content.strip().startswith('#') or '"""' in line_content:
            is_valid = True
            reason = "Comment/docstring"
        
        # 4. Inside a string literal
        elif 'f"' in line_content or "f'" in line_content:
            # If thread_slug is in the f-string, it's valid
            if 'thread_slug' in line_content or 'Session:' in line_content:
                is_valid = True
                reason = "String literal (safe)"
            else:
                reason = "F-STRING WITH UNDEFINED VAR!"
        
        # 5. Fallback in get() chain: or request.args.get('session_id')
        elif "request.args.get('session_id')" in line_content:
            is_valid = True
            reason = "Fallback in request.args.get()"
        
        else:
            reason = "⚠️  UNDEFINED VARIABLE REFERENCE"
        
        if is_valid:
            valid_refs += 1
            status = "✅"
        else:
            invalid_refs += 1
            status = "❌"
        
        print(f"   {status} Line {line_num}: {reason}")
        print(f"      {line_content[:100]}")
        print()
    
    print(f"\n📈 Summary:\n")
    print(f"   ✅ Valid references: {valid_refs}")
    print(f"   ❌ Invalid references: {invalid_refs}")
    
    if invalid_refs == 0:
        print(f"\n🎉 SUCCESS! No undefined session_id references found!")
        print(f"   All {len(session_id_refs)} session_id references are valid.")
        return True
    else:
        print(f"\n⚠️  WARNING! Found {invalid_refs} undefined session_id references!")
        print(f"   These will cause NameError at runtime.")
        return False


if __name__ == '__main__':
    print("="*80)
    print("STREAM FIX VERIFICATION")
    print("Checking for undefined session_id references in stream_agent() function")
    print("="*80)
    print()
    
    success = analyze_stream_function()
    
    print()
    print("="*80)
    
    if success:
        print("✅ VERIFICATION PASSED - Ready to restart server")
    else:
        print("❌ VERIFICATION FAILED - More fixes needed")
    
    print("="*80)
