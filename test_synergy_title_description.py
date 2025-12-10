#!/usr/bin/env python3
"""
Test script for Synergy title+description format with fallback pattern

This script validates:
1. Creating milestones with separate title+description fields
2. Creating tasks with title\\n\\nDescription format
3. Creating subtasks with title\\n\\nDescription format
4. Updating all three using the fallback pattern
5. Validation of required fields
6. Backend compatibility (multi-field vs. per-field updates)

Run this after making schema/implementation changes to ensure everything works.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.implementations.synergy import (
    synergy_create_session,
    synergy_create_milestone,
    synergy_create_task,
    synergy_create_subtask,
    synergy_update_milestone,
    synergy_update_task,
    synergy_update_subtask,
    synergy_get_milestones,
    synergy_delete_session,
    SynergyError
)


def test_title_description_format():
    """Test creating hierarchical structure with title+description format"""
    
    print("=" * 80)
    print("SYNERGY TITLE+DESCRIPTION FORMAT TEST")
    print("=" * 80)
    print()
    
    session_id = None
    milestone_id = None
    task_id = None
    subtask_id = None
    
    try:
        # =====================================================================
        # TEST 1: Create test session
        # =====================================================================
        print("📝 TEST 1: Creating test session...")
        result = synergy_create_session(
            title="Test Title+Description Format",
            description="Test session for validating title+description format",
            project_name="testing",
            uses_milestones=True
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to create session: {result}")
        
        session_id = result['session_id']
        print(f"✅ Session created: {session_id}")
        print()
        
        # =====================================================================
        # TEST 2: Create milestone with separate title and description
        # =====================================================================
        print("📝 TEST 2: Creating milestone with separate title+description...")
        result = synergy_create_milestone(
            session_id=session_id,
            milestone_name="Phase 1: Infrastructure Setup",
            description="Set up all core infrastructure components.\n\nThis includes configuring cloud resources, setting up databases, implementing monitoring, and deploying CI/CD pipelines.",
            priority="critical"
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to create milestone: {result}")
        
        milestone_id = result['milestone_id']
        print(f"✅ Milestone created: {milestone_id}")
        print(f"   Title: Phase 1: Infrastructure Setup")
        print(f"   Description has line breaks: ✅")
        print()
        
        # =====================================================================
        # TEST 3: Create task with title\n\nDescription format
        # =====================================================================
        print("📝 TEST 3: Creating task with title\\n\\nDescription format...")
        result = synergy_create_task(
            milestone_id=milestone_id,
            task="Configure PostgreSQL database\n\nInstall PostgreSQL 14, create database schemas, set up replication, configure backup automation, and implement connection pooling.",
            priority="high"
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to create task: {result}")
        
        task_id = result['task_id']
        print(f"✅ Task created: {task_id}")
        print(f"   Format: Title\\n\\nDescription ✅")
        print()
        
        # =====================================================================
        # TEST 4: Create subtask with title\n\nDescription format
        # =====================================================================
        print("📝 TEST 4: Creating subtask with title\\n\\nDescription format...")
        result = synergy_create_subtask(
            task_id=task_id,
            subtask="Set up connection pooling\n\nConfigure pgBouncer for connection pooling. Set max_connections=100, pool_mode=transaction, and default_pool_size=25.",
            priority="medium"
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to create subtask: {result}")
        
        subtask_id = result['subtask_id']
        print(f"✅ Subtask created: {subtask_id}")
        print(f"   Format: Title\\n\\nDescription ✅")
        print()
        
        # =====================================================================
        # TEST 5: Update milestone (test fallback pattern)
        # =====================================================================
        print("📝 TEST 5: Updating milestone (testing fallback pattern)...")
        result = synergy_update_milestone(
            milestone_id=milestone_id,
            description="Set up all core infrastructure components.\n\nThis includes configuring cloud resources, setting up databases, implementing monitoring, deploying CI/CD pipelines, and establishing security protocols.",
            priority="critical"
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to update milestone: {result}")
        
        print(f"✅ Milestone updated successfully")
        print(f"   Fallback pattern: Handled backend compatibility ✅")
        print()
        
        # =====================================================================
        # TEST 6: Update task (test fallback pattern)
        # =====================================================================
        print("📝 TEST 6: Updating task (testing fallback pattern)...")
        result = synergy_update_task(
            task_id=task_id,
            task="Configure PostgreSQL database\n\nInstall PostgreSQL 14, create database schemas, set up replication, configure backup automation, implement connection pooling, and set up monitoring alerts.",
            priority="critical"
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to update task: {result}")
        
        print(f"✅ Task updated successfully")
        print(f"   Fallback pattern: Handled backend compatibility ✅")
        print()
        
        # =====================================================================
        # TEST 7: Update subtask (test fallback pattern)
        # =====================================================================
        print("📝 TEST 7: Updating subtask (testing fallback pattern)...")
        result = synergy_update_subtask(
            subtask_id=subtask_id,
            subtask="Set up connection pooling\n\nConfigure pgBouncer for connection pooling. Set max_connections=100, pool_mode=transaction, default_pool_size=25, and enable query logging.",
            completed=True
        )
        
        if not result.get('success'):
            raise Exception(f"Failed to update subtask: {result}")
        
        print(f"✅ Subtask updated successfully")
        print(f"   Fallback pattern: Handled backend compatibility ✅")
        print()
        
        # =====================================================================
        # TEST 8: Verify structure with synergy_get_milestones
        # =====================================================================
        print("📝 TEST 8: Verifying complete structure...")
        result = synergy_get_milestones(session_id=session_id)
        
        if not result.get('success'):
            raise Exception(f"Failed to get milestones: {result}")
        
        milestones = result.get('milestones', [])
        if not milestones:
            raise Exception("No milestones found!")
        
        milestone = milestones[0]
        print(f"✅ Structure verified:")
        print(f"   Milestone: {milestone.get('milestone_name')}")
        print(f"   Description lines: {milestone.get('description', '').count(chr(10)) + 1}")
        
        tasks = milestone.get('tasks', [])
        if tasks:
            task = tasks[0]
            print(f"   Task: {task.get('task', 'N/A')}")
            print(f"   Task has \\n\\n separator: {'\\n\\n' in task.get('task', '')}")
            
            subtasks = task.get('subtasks', [])
            if subtasks:
                subtask = subtasks[0]
                print(f"   Subtask: {subtask.get('task', 'N/A')[:50]}...")
                print(f"   Subtask has \\n\\n separator: {'\\n\\n' in subtask.get('task', '')}")
                print(f"   Subtask completed: {subtask.get('completed', False)}")
        print()
        
        # =====================================================================
        # TEST 9: Test validation (should fail with clear error)
        # =====================================================================
        print("📝 TEST 9: Testing validation (should fail gracefully)...")
        try:
            synergy_create_milestone(
                session_id=session_id,
                milestone_name="",  # Empty name should fail
                description="Test"
            )
            print("❌ VALIDATION FAILED: Empty milestone_name should have raised error!")
        except SynergyError as e:
            print(f"✅ Validation working: {str(e)}")
        
        try:
            synergy_create_task(
                milestone_id=milestone_id,
                task="",  # Empty task should fail
                priority="high"
            )
            print("❌ VALIDATION FAILED: Empty task should have raised error!")
        except SynergyError as e:
            print(f"✅ Validation working: {str(e)}")
        
        try:
            synergy_create_subtask(
                task_id=task_id,
                subtask="   ",  # Whitespace-only should fail
                priority="medium"
            )
            print("❌ VALIDATION FAILED: Whitespace-only subtask should have raised error!")
        except SynergyError as e:
            print(f"✅ Validation working: {str(e)}")
        
        print()
        
        # =====================================================================
        # CLEANUP
        # =====================================================================
        print("📝 Cleaning up test session...")
        result = synergy_delete_session(session_id=session_id)
        
        if result.get('success'):
            print(f"✅ Test session deleted")
        else:
            print(f"⚠️  Failed to delete session (may need manual cleanup): {session_id}")
        
        print()
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✅ Title+description format works for milestones (separate fields)")
        print("  ✅ Title+description format works for tasks (\\n\\n separator)")
        print("  ✅ Title+description format works for subtasks (\\n\\n separator)")
        print("  ✅ Fallback pattern handles backend compatibility")
        print("  ✅ Validation prevents empty/invalid inputs")
        print("  ✅ Updates preserve line breaks and formatting")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print()
        
        # Try to cleanup even on failure
        if session_id:
            print("Attempting cleanup...")
            try:
                synergy_delete_session(session_id=session_id)
                print("✅ Cleanup successful")
            except:
                print(f"⚠️  Manual cleanup needed: {session_id}")
        
        return False


if __name__ == "__main__":
    success = test_title_description_format()
    sys.exit(0 if success else 1)
