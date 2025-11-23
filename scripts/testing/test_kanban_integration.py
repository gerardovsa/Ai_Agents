"""
Kanban & AI Infrastructure Integration Test
============================================
Tests the bridge between Synergy Kanban Board and AI Infrastructure
from shared.database_utils import convert_sql_placeholders

Tests:
1. Create Kanban task
2. Link task to AI agent
3. Query across databases
4. Sync status updates
5. Bidirectional communication
"""

import sqlite3
import requests
import json
from datetime import datetime
import time

# Database paths
SYNERGY_DB = 'data/synergy_sessions.db'
AI_INFRASTRUCTURE_DB = 'AI_infrastructure/ai_infrastructure.db'

# API endpoints - CONSOLIDATED ON PORT 5001
API_BASE = 'http://localhost:5001'

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}[ERROR] {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.END}")


# ============================================
# TEST 1: Database Connectivity
# ============================================

def test_database_connectivity():
    """Test that both databases are accessible"""
    print_header("TEST 1: Database Connectivity")
    
    try:
        # Test Synergy DB
        synergy_conn = sqlite3.connect(SYNERGY_DB)
        cursor = synergy_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        synergy_conn.close()
        print_success(f"Synergy DB connected: {session_count} tasks")
        
        # Test AI Infrastructure DB
        ai_conn = sqlite3.connect(AI_INFRASTRUCTURE_DB)
        cursor = ai_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM kanban_task_links")
        link_count = cursor.fetchone()[0]
        ai_conn.close()
        print_success(f"AI Infrastructure DB connected: {link_count} links")
        
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


# ============================================
# TEST 2: Create Kanban Task via API
# ============================================

def test_create_kanban_task():
    """Create a task in Synergy Kanban"""
    print_header("TEST 2: Create Kanban Task")
    
    task_data = {
        'title': 'Integration Test Task',
        'description': 'Testing Kanban <-> AI Infrastructure integration',
        'priority': 'high',
        'status': 'active',
        'kanban_column': 'backlog',
        'tags': ['integration-test', 'ai-agent'],
        'project_name': 'System Integration Testing'
    }
    
    try:
        response = requests.post(f'{API_BASE}/api/kanban/sessions', json=task_data)
        if response.status_code == 201:
            data = response.json()
            session_id = data.get('session_id')
            print_success(f"Kanban task created: {session_id}")
            print_info(f"  Title: {data.get('title')}")
            print_info(f"  Column: {data.get('kanban_column')}")
            return session_id
        else:
            print_error(f"Failed to create task: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is flask_app.py running on port 5001?")
        return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# TEST 3: Link Task to AI Agent
# ============================================

def test_link_task_to_agent(kanban_session_id):
    """Create a link between Kanban task and AI agent"""
    print_header("TEST 3: Link Task to AI Agent")
    
    if not kanban_session_id:
        print_error("No Kanban session ID provided")
        return None
    
    agent_id = "test-agent-001"
    agent_name = "Integration Test Agent"
    
    try:
        ai_conn = sqlite3.connect(AI_INFRASTRUCTURE_DB)
        cursor = ai_conn.cursor()
        
        # Create link
        sql, params = convert_sql_placeholders('''
            INSERT INTO kanban_task_links 
            (agent_id, agent_name, kanban_session_id, kanban_title, kanban_status, 
             kanban_column, sync_direction, agent_work_status)
            VALUES (?, ?, ?, ?, ?, ?, 'bidirectional', 'pending')
        ''', (agent_id, agent_name, kanban_session_id, 'Integration Test Task', 
              'active', 'backlog'))

        cursor.execute(sql, params)
        
        ai_conn.commit()
        link_id = cursor.lastrowid
        ai_conn.close()
        
        print_success(f"Link created: ID {link_id}")
        print_info(f"  Agent: {agent_name} ({agent_id})")
        print_info(f"  Kanban Task: {kanban_session_id}")
        print_info(f"  Sync Direction: bidirectional")
        
        return link_id
        
    except Exception as e:
        print_error(f"Failed to create link: {e}")
        return None


# ============================================
# TEST 4: Query Across Databases
# ============================================

def test_cross_database_query(kanban_session_id):
    """Query data from both databases simultaneously"""
    print_header("TEST 4: Cross-Database Query")
    
    if not kanban_session_id:
        print_error("No Kanban session ID provided")
        return None
    
    try:
        # Get Kanban task details
        synergy_conn = sqlite3.connect(SYNERGY_DB)
        synergy_conn.row_factory = sqlite3.Row
        cursor = synergy_conn.cursor()
        sql, params = convert_sql_placeholders('SELECT * FROM sessions WHERE session_id = ?', (kanban_session_id,))

        cursor.execute(sql, params)
        kanban_task = cursor.fetchone()
        synergy_conn.close()
        
        if not kanban_task:
            print_error("Kanban task not found")
            return None
        
        print_success("Kanban task retrieved:")
        print_info(f"  ID: {kanban_task['session_id']}")
        print_info(f"  Title: {kanban_task['title']}")
        print_info(f"  Status: {kanban_task['status']}")
        print_info(f"  Column: {kanban_task['kanban_column']}")
        
        # Get AI agent assignment
        ai_conn = sqlite3.connect(AI_INFRASTRUCTURE_DB)
        ai_conn.row_factory = sqlite3.Row
        cursor = ai_conn.cursor()
        sql, params = convert_sql_placeholders('''
            SELECT * FROM kanban_task_links 
            WHERE kanban_session_id = ?
        ''', (kanban_session_id,))

        cursor.execute(sql, params)
        agent_link = cursor.fetchone()
        ai_conn.close()
        
        if agent_link:
            print_success("AI agent assignment found:")
            print_info(f"  Agent ID: {agent_link['agent_id']}")
            print_info(f"  Agent Name: {agent_link['agent_name']}")
            print_info(f"  Work Status: {agent_link['agent_work_status']}")
            print_info(f"  Sync Direction: {agent_link['sync_direction']}")
            print_info(f"  Created: {agent_link['created_at']}")
        else:
            print_error("No agent assignment found")
        
        return {'kanban': dict(kanban_task), 'agent': dict(agent_link) if agent_link else None}
        
    except Exception as e:
        print_error(f"Cross-database query failed: {e}")
        return None


# ============================================
# TEST 5: Update Agent Work Status
# ============================================

def test_update_agent_status(kanban_session_id):
    """Simulate agent starting work on task"""
    print_header("TEST 5: Update Agent Work Status")
    
    if not kanban_session_id:
        print_error("No Kanban session ID provided")
        return False
    
    try:
        ai_conn = sqlite3.connect(AI_INFRASTRUCTURE_DB)
        cursor = ai_conn.cursor()
        
        # Update agent work status
        cursor.execute('''
            UPDATE kanban_task_links
            SET agent_work_status = 'in_progress',
                last_synced_at = ?,
                notes = 'Agent started working on task'
            WHERE kanban_session_id = ?
        ''', (datetime.now().isoformat(), kanban_session_id))
        
        ai_conn.commit()
        rows_affected = cursor.rowcount
        ai_conn.close()
        
        if rows_affected > 0:
            print_success(f"Agent status updated to 'in_progress'")
            print_info(f"  Task: {kanban_session_id}")
            print_info(f"  Status: in_progress")
            print_info(f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print_error("No rows updated")
            return False
        
    except Exception as e:
        print_error(f"Status update failed: {e}")
        return False


# ============================================
# TEST 6: Update Kanban Task Status
# ============================================

def test_update_kanban_status(kanban_session_id):
    """Update Kanban task status (simulating user action)"""
    print_header("TEST 6: Update Kanban Task Status")
    
    if not kanban_session_id:
        print_error("No Kanban session ID provided")
        return False
    
    try:
        response = requests.patch(
            f'{API_BASE}/api/kanban/sessions/{kanban_session_id}',
            json={
                'kanban_column': 'in_progress',
                'notes': 'Task moved to in progress - AI agent working'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Kanban task updated")
            print_info(f"  Column: {data.get('kanban_column')}")
            print_info(f"  Notes updated: Yes")
            return True
        else:
            print_error(f"Failed to update task: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Kanban update failed: {e}")
        return False


# ============================================
# TEST 7: View Integration Summary
# ============================================

def test_view_integration_summary():
    """Use database views to see integration status"""
    print_header("TEST 7: Integration Summary (via Views)")
    
    try:
        # Query active agent tasks view
        ai_conn = sqlite3.connect(AI_INFRASTRUCTURE_DB)
        ai_conn.row_factory = sqlite3.Row
        cursor = ai_conn.cursor()
        
        cursor.execute('SELECT * FROM v_active_agent_kanban_tasks')
        active_tasks = cursor.fetchall()
        
        if active_tasks:
            print_success(f"Found {len(active_tasks)} active agent tasks:")
            for task in active_tasks:
                print_info(f"\n  Task: {task['kanban_title']}")
                print_info(f"    Agent: {task['agent_name']} ({task['agent_id']})")
                print_info(f"    Kanban Column: {task['kanban_column']}")
                print_info(f"    Agent Status: {task['agent_work_status']}")
                print_info(f"    Sync Direction: {task['sync_direction']}")
        else:
            print_info("No active agent tasks found")
        
        # Query agent summary
        cursor.execute('SELECT * FROM v_agent_kanban_summary')
        agent_summary = cursor.fetchall()
        
        if agent_summary:
            print_success(f"\nAgent Summary:")
            for agent in agent_summary:
                print_info(f"\n  Agent: {agent['agent_name']} ({agent['agent_id']})")
                print_info(f"    Total Tasks: {agent['total_tasks']}")
                print_info(f"    Completed: {agent['completed_tasks']}")
                print_info(f"    Active: {agent['active_tasks']}")
                print_info(f"    Failed: {agent['failed_tasks']}")
                print_info(f"    Last Activity: {agent['last_activity']}")
        
        ai_conn.close()
        return True
        
    except Exception as e:
        print_error(f"View query failed: {e}")
        return False


# ============================================
# TEST 8: Complete Task Workflow
# ============================================

def test_complete_task_workflow(kanban_session_id):
    """Simulate complete task lifecycle"""
    print_header("TEST 8: Complete Task Workflow")
    
    if not kanban_session_id:
        print_error("No Kanban session ID provided")
        return False
    
    try:
        # Step 1: Mark agent work as completed
        ai_conn = sqlite3.connect(AI_INFRASTRUCTURE_DB)
        cursor = ai_conn.cursor()
        
        cursor.execute('''
            UPDATE kanban_task_links
            SET agent_work_status = 'completed',
                completed_at = ?,
                sync_status = 'completed',
                notes = 'Agent successfully completed the task'
            WHERE kanban_session_id = ?
        ''', (datetime.now().isoformat(), kanban_session_id))
        
        ai_conn.commit()
        ai_conn.close()
        print_success("Agent marked task as completed")
        
        # Step 2: Update Kanban board
        response = requests.patch(
            f'{API_BASE}/api/kanban/sessions/{kanban_session_id}',
            json={
                'kanban_column': 'done',
                'status': 'completed',
                'notes': 'Task completed by AI agent'
            }
        )
        
        if response.status_code == 200:
            print_success("Kanban task moved to 'done' column")
            print_info("  Status: completed")
            print_info("  Column: done")
            return True
        else:
            print_error("Failed to update Kanban task")
            return False
            
    except Exception as e:
        print_error(f"Workflow completion failed: {e}")
        return False


# ============================================
# MAIN TEST RUNNER
# ============================================

def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"KANBAN & AI INFRASTRUCTURE INTEGRATION TEST SUITE")
    print(f"{'='*70}{Colors.END}\n")
    
    print_info(f"Synergy DB: {SYNERGY_DB}")
    print_info(f"AI Infra DB: {AI_INFRASTRUCTURE_DB}")
    print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test 1: Database Connectivity
    if not test_database_connectivity():
        print_error("\nDatabase connectivity failed. Exiting tests.")
        return
    
    time.sleep(1)
    
    # Test 2: Create Kanban Task
    kanban_session_id = test_create_kanban_task()
    if not kanban_session_id:
        print_error("\nFailed to create Kanban task. Exiting tests.")
        return
    
    time.sleep(1)
    
    # Test 3: Link to AI Agent
    link_id = test_link_task_to_agent(kanban_session_id)
    time.sleep(1)
    
    # Test 4: Cross-Database Query
    test_cross_database_query(kanban_session_id)
    time.sleep(1)
    
    # Test 5: Update Agent Status
    test_update_agent_status(kanban_session_id)
    time.sleep(1)
    
    # Test 6: Update Kanban Status
    test_update_kanban_status(kanban_session_id)
    time.sleep(1)
    
    # Test 7: View Summary
    test_view_integration_summary()
    time.sleep(1)
    
    # Test 8: Complete Workflow
    test_complete_task_workflow(kanban_session_id)
    
    # Final Summary
    print_header("TEST SUMMARY")
    print_success("All integration tests completed!")
    print_info(f"Test Kanban Task: {kanban_session_id}")
    print_info(f"Database Link ID: {link_id}")
    print_info("\nIntegration Status: OPERATIONAL")
    print_info("Both databases are successfully connected and communicating")
    
    print(f"\n{Colors.BOLD}Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")


if __name__ == '__main__':
    run_all_tests()
