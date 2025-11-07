"""Test Synergy endpoints with new thread_ids and assigned_agents fields"""

from tools.implementations.synergy import synergy_create_session, synergy_update_session, synergy_get_session
import json

print("\n" + "="*70)
print("  TESTING SYNERGY TOOLS - thread_ids & assigned_agents")
print("="*70)

# Test 1: Create session with new fields
print("\n[TEST 1] Creating session with thread_ids and assigned_agents...")
try:
    result = synergy_create_session(
        title="Python Tool Test Session",
        description="Testing new fields from Python implementation",
        priority="high",
        kanban_column="in_progress",
        thread_ids=["thread_py_001", "thread_py_002", "thread_py_003"],
        assigned_agents=["Python Agent", "Test Agent", "Debug Agent"],
        documents=[
            {
                "title": "Python Test Doc",
                "url": "https://example.com/python/doc",
                "type": "google_doc"
            }
        ],
        next_steps=["Test creation", "Test update", "Verify UI"]
    )
    
    print(f"✅ SUCCESS: {result['message']}")
    print(f"   Session ID: {result['session_id']}")
    session_id = result['session_id']
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

# Test 2: Retrieve session to verify fields
print("\n[TEST 2] Retrieving session to verify fields were saved...")
try:
    result = synergy_get_session(session_id=session_id)
    # The result has nested session: {"success": True, "session": {"success": True, "session": {...}}}
    if 'session' in result and 'session' in result['session']:
        session = result['session']['session']
    elif 'session' in result:
        session = result['session']
    else:
        session = result
    
    print(f"✅ SUCCESS: Retrieved session")
    print(f"   Title: {session['title']}")
    print(f"   Priority: {session['priority']}")
    print(f"   Column: {session['kanban_column']}")
    
    # Parse JSON fields (they should already be parsed by the backend now)
    thread_ids = session.get('thread_ids', [])
    assigned_agents = session.get('assigned_agents', [])
    documents = session.get('documents', [])
    
    print(f"   Thread IDs: {thread_ids}")
    print(f"   Thread count: {len(thread_ids)}")
    print(f"   Assigned Agents: {assigned_agents}")
    print(f"   Agent count: {len(assigned_agents)}")
    print(f"   Documents: {len(documents)} document(s)")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Update thread_ids and assigned_agents
print("\n[TEST 3] Updating thread_ids and assigned_agents...")
try:
    result = synergy_update_session(
        session_id=session_id,
        thread_ids=["thread_py_001", "thread_py_002", "thread_py_003", "thread_py_004", "thread_py_005"],
        assigned_agents=["Python Agent", "Test Agent", "Debug Agent", "Analytics Agent"],
        priority="critical"
    )
    
    print(f"✅ SUCCESS: {result['message']}")
    print(f"   Updated fields: {', '.join(result['updated_fields'])}")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

# Test 4: Verify update
print("\n[TEST 4] Verifying update...")
try:
    result = synergy_get_session(session_id=session_id)
    # Handle nested structure
    if 'session' in result and 'session' in result['session']:
        session = result['session']['session']
    elif 'session' in result:
        session = result['session']
    else:
        session = result
    
    # Get fields (already parsed by backend)
    thread_ids = session.get('thread_ids', [])
    assigned_agents = session.get('assigned_agents', [])
    
    print(f"✅ SUCCESS: Update verified")
    print(f"   Priority: {session['priority']} (changed from 'high' to 'critical')")
    print(f"   Thread IDs: {thread_ids}")
    print(f"   Thread count: {len(thread_ids)} (increased from 3 to 5)")
    print(f"   Assigned Agents: {assigned_agents}")
    print(f"   Agent count: {len(assigned_agents)} (increased from 3 to 4)")
    
    # Verify counts
    assert len(thread_ids) == 5, f"Expected 5 thread IDs, got {len(thread_ids)}"
    assert len(assigned_agents) == 4, f"Expected 4 agents, got {len(assigned_agents)}"
    assert session['priority'] == 'critical', f"Expected priority 'critical', got {session['priority']}"
    
    print("\n" + "="*70)
    print("  🎉 ALL TESTS PASSED!")
    print("="*70)
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
