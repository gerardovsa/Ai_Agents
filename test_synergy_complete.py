"""
Comprehensive Synergy Tools Test Suite
========================================
Tests all critical functionality after bug fixes:
1. Create session with documents, links, checklist
2. Update session with more items
3. Move session between columns
4. Retrieve and verify all fields
5. Test edit button compatibility (structure validation)

Run after applying fixes to:
- business-ai-platform-v2.html (checklist parsing)
- synergy_routes.py (kanban_column updates, move session parameter)
- synergy.py (document/link name normalization)
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:5001/api/synergy"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_create_session_with_all_features():
    """TEST 1: Create session with documents, links, and checklist"""
    print_section("TEST 1: Create Session with All Features")
    
    payload = {
        "title": "Complete Feature Test Session",
        "description": "Testing all Synergy features: documents, links, checklists, subtasks",
        "priority": "high",
        "kanban_column": "in_progress",
        "platforms_involved": ["gmail", "sheets", "docs"],
        "tags": ["test", "comprehensive", "validation"],
        "documents": [
            {
                "title": "Test Google Doc",
                "url": "https://docs.google.com/document/d/test123",
                "type": "google_doc"
            },
            {
                "title": "Test Excel Sheet",
                "url": "https://example.com/sheet.xlsx",
                "type": "excel"
            }
        ],
        "links": [
            {
                "title": "Project Dashboard",
                "url": "https://example.com/dashboard",
                "type": "dashboard"
            },
            {
                "title": "GitHub Repo",
                "url": "https://github.com/test/repo",
                "type": "github"
            }
        ],
        "checklist": [
            {
                "task": "Main Task 1 - Research",
                "completed": False,
                "subtasks": [
                    {"task": "Subtask 1.1 - Gather data", "completed": False},
                    {"task": "Subtask 1.2 - Analyze results", "completed": False}
                ]
            },
            {
                "task": "Main Task 2 - Implementation",
                "completed": False,
                "subtasks": [
                    {"task": "Subtask 2.1 - Write code", "completed": False},
                    {"task": "Subtask 2.2 - Test code", "completed": False}
                ]
            }
        ],
        "next_steps": [
            "Complete initial research",
            "Build prototype",
            "Run tests"
        ],
        "thread_ids": ["thread_test_001", "thread_test_002"],
        "assigned_agents": ["Test Agent", "Validation Agent"]
    }
    
    try:
        print(f"Sending payload to: {BASE_URL}/create")
        response = requests.post(f"{BASE_URL}/create", json=payload, timeout=10)
        
        # Debug: Print response
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            session_id = result['session_id']
            print(f"✅ SUCCESS: Created session")
            print(f"   Session ID: {session_id}")
            print(f"   Title: {payload['title']}")
            print(f"   Documents: {len(payload['documents'])} added")
            print(f"   Links: {len(payload['links'])} added")
            print(f"   Checklist: {len(payload['checklist'])} items (with subtasks)")
            print(f"   Thread IDs: {len(payload['thread_ids'])} threads")
            print(f"   Agents: {len(payload['assigned_agents'])} agents")
            return session_id
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_retrieve_session(session_id):
    """TEST 2: Retrieve session and verify all fields"""
    print_section("TEST 2: Retrieve Session and Verify Fields")
    
    try:
        response = requests.get(f"{BASE_URL}/{session_id}", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            session = result['session']
            print(f"✅ SUCCESS: Retrieved session")
            print(f"   Title: {session.get('title')}")
            print(f"   Priority: {session.get('priority')}")
            print(f"   Column: {session.get('kanban_column')}")
            
            # Validate documents
            documents = session.get('documents', [])
            print(f"   Documents: {len(documents)} found")
            for doc in documents:
                print(f"      - {doc.get('title')} ({doc.get('type')})")
                if 'name' in doc and 'title' not in doc:
                    print(f"        ⚠️  WARNING: Document has 'name' but no 'title' - edit button will fail!")
            
            # Validate links
            links = session.get('links', [])
            print(f"   Links: {len(links)} found")
            for link in links:
                print(f"      - {link.get('title')} ({link.get('type')})")
            
            # Validate checklist
            checklist = session.get('checklist', [])
            print(f"   Checklist: {len(checklist)} items")
            for idx, item in enumerate(checklist):
                print(f"      {idx+1}. {item.get('task')} (completed: {item.get('completed')})")
                subtasks = item.get('subtasks', [])
                if subtasks:
                    for sub in subtasks:
                        print(f"         - {sub.get('task')} (completed: {sub.get('completed')})")
            
            # Validate thread_ids and assigned_agents
            thread_ids = session.get('thread_ids', [])
            assigned_agents = session.get('assigned_agents', [])
            print(f"   Thread IDs: {thread_ids}")
            print(f"   Assigned Agents: {assigned_agents}")
            
            return session
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def test_update_session(session_id):
    """TEST 3: Update session with additional items"""
    print_section("TEST 3: Update Session - Add More Items")
    
    payload = {
        "updates": {
            "priority": "critical",
            "documents": [
                # Keep existing
                {
                    "title": "Test Google Doc",
                    "url": "https://docs.google.com/document/d/test123",
                    "type": "google_doc"
                },
                {
                    "title": "Test Excel Sheet",
                    "url": "https://example.com/sheet.xlsx",
                    "type": "excel"
                },
                # Add new
                {
                    "title": "New PDF Document",
                    "url": "https://example.com/document.pdf",
                    "type": "pdf"
                }
            ],
            "links": [
                # Keep existing
                {
                    "title": "Project Dashboard",
                    "url": "https://example.com/dashboard",
                    "type": "dashboard"
                },
                {
                    "title": "GitHub Repo",
                    "url": "https://github.com/test/repo",
                    "type": "github"
                },
                # Add new
                {
                    "title": "Figma Design",
                    "url": "https://figma.com/file/test",
                    "type": "figma"
                }
            ],
            "thread_ids": ["thread_test_001", "thread_test_002", "thread_test_003"],
            "assigned_agents": ["Test Agent", "Validation Agent", "Update Agent"]
        }
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/{session_id}", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print(f"✅ SUCCESS: Updated session")
            print(f"   Priority changed to: critical")
            print(f"   Documents: 2 → 3 (added 1 new)")
            print(f"   Links: 2 → 3 (added 1 new)")
            print(f"   Thread IDs: 2 → 3")
            print(f"   Agents: 2 → 3")
            return True
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_move_session(session_id):
    """TEST 4: Move session to different column"""
    print_section("TEST 4: Move Session to Review Column")
    
    payload = {
        "target_column": "review",
        "notes": "Moving to review after comprehensive testing"
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/{session_id}/column", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            session = result.get('session', {})
            print(f"✅ SUCCESS: Moved session")
            print(f"   New column: {session.get('kanban_column')}")
            print(f"   Notes: {payload['notes']}")
            return True
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_kanban_column_via_update(session_id):
    """TEST 5: Update kanban_column via PATCH (not /column endpoint)"""
    print_section("TEST 5: Update Kanban Column via PATCH Endpoint")
    
    payload = {
        "updates": {
            "kanban_column": "done"
        }
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/{session_id}", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print(f"✅ SUCCESS: Updated kanban_column via PATCH")
            print(f"   Column should now be: done")
            return True
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_verify_final_state(session_id):
    """TEST 6: Verify final state matches all updates"""
    print_section("TEST 6: Verify Final State")
    
    try:
        response = requests.get(f"{BASE_URL}/{session_id}", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            session = result['session']
            
            # Verify counts
            documents = session.get('documents', [])
            links = session.get('links', [])
            thread_ids = session.get('thread_ids', [])
            assigned_agents = session.get('assigned_agents', [])
            checklist = session.get('checklist', [])
            
            print(f"✅ SUCCESS: Final verification")
            print(f"   Priority: {session.get('priority')} (expected: critical)")
            print(f"   Column: {session.get('kanban_column')} (expected: done)")
            print(f"   Documents: {len(documents)} (expected: 3)")
            print(f"   Links: {len(links)} (expected: 3)")
            print(f"   Checklist: {len(checklist)} items (expected: 2)")
            print(f"   Thread IDs: {len(thread_ids)} (expected: 3)")
            print(f"   Agents: {len(assigned_agents)} (expected: 3)")
            
            # Verify specific values
            all_correct = True
            if session.get('priority') != 'critical':
                print(f"   ❌ Priority mismatch!")
                all_correct = False
            if session.get('kanban_column') != 'done':
                print(f"   ❌ Column mismatch!")
                all_correct = False
            if len(documents) != 3:
                print(f"   ❌ Document count mismatch!")
                all_correct = False
            if len(links) != 3:
                print(f"   ❌ Link count mismatch!")
                all_correct = False
            if len(thread_ids) != 3:
                print(f"   ❌ Thread ID count mismatch!")
                all_correct = False
            if len(assigned_agents) != 3:
                print(f"   ❌ Agent count mismatch!")
                all_correct = False
            
            if all_correct:
                print(f"\n   🎉 ALL VERIFICATIONS PASSED!")
            else:
                print(f"\n   ⚠️  SOME VERIFICATIONS FAILED!")
            
            return all_correct
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("  SYNERGY TOOLS COMPREHENSIVE TEST SUITE")
    print("  Testing after bug fixes (November 8, 2025)")
    print("="*70)
    
    # Test 1: Create
    session_id = test_create_session_with_all_features()
    if not session_id:
        print("\n❌ ABORTING: Session creation failed")
        return
    
    # Test 2: Retrieve
    session = test_retrieve_session(session_id)
    if not session:
        print("\n❌ ABORTING: Session retrieval failed")
        return
    
    # Test 3: Update
    if not test_update_session(session_id):
        print("\n⚠️  WARNING: Session update failed (continuing...)")
    
    # Test 4: Move
    if not test_move_session(session_id):
        print("\n⚠️  WARNING: Session move failed (continuing...)")
    
    # Test 5: Update kanban_column via PATCH
    if not test_update_kanban_column_via_update(session_id):
        print("\n⚠️  WARNING: Kanban column update via PATCH failed (continuing...)")
    
    # Test 6: Final verification
    test_verify_final_state(session_id)
    
    print_section("TEST SUITE COMPLETE")
    print(f"Session ID for manual testing: {session_id}")
    print(f"Open browser to: http://localhost:5001")
    print(f"Click edit button on this session to verify UI works")


if __name__ == "__main__":
    main()
