#!/usr/bin/env python3
"""
Simple test to verify basic Synergy operations work
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.implementations.synergy import (
    synergy_create_session,
    synergy_create_milestone,
    synergy_create_task,
    synergy_delete_session
)

def simple_test():
    print("Testing basic Synergy operations...")
    
    session_id = None
    milestone_id = None
    
    try:
        # Create session
        print("\n1. Creating session...")
        result = synergy_create_session(
            title="Simple Test",
            description="Basic test",
            uses_milestones=True
        )
        session_id = result['session_id']
        print(f"   ✅ Session: {session_id}")
        
        # Create milestone
        print("\n2. Creating milestone...")
        result = synergy_create_milestone(
            session_id=session_id,
            milestone_name="Test Milestone",
            description="Test description",
            priority="medium"
        )
        milestone_id = result['milestone_id']
        print(f"   ✅ Milestone: {milestone_id}")
        
        # Create simple task WITHOUT subtasks
        print("\n3. Creating simple task (no subtasks)...")
        result = synergy_create_task(
            milestone_id=milestone_id,
            task="Simple task",
            priority="medium"
        )
        print(f"   ✅ Task: {result['task_id']}")
        
        # Create task with title+description
        print("\n4. Creating task with title+description...")
        result = synergy_create_task(
            milestone_id=milestone_id,
            task="Complex task\n\nThis is the detailed description",
            priority="high"
        )
        print(f"   ✅ Task: {result['task_id']}")
        
        # Cleanup
        print("\n5. Cleaning up...")
        synergy_delete_session(session_id=session_id)
        print(f"   ✅ Deleted session")
        
        print("\n✅ ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if session_id:
            try:
                synergy_delete_session(session_id=session_id)
                print(f"Cleanup successful")
            except:
                print(f"Manual cleanup needed: {session_id}")
        return False

if __name__ == "__main__":
    success = simple_test()
    sys.exit(0 if success else 1)
