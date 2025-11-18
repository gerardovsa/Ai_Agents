"""
Test Visual Automation Canvas - Complete Publishing Flow

This script tests the complete workflow lifecycle:
1. Create workflow (draft)
2. Save to database
3. Link to thread
4. Publish workflow
5. Check status
6. Monitor execution

Run: python test_automation_canvas_complete.py
"""

import requests
import json
from datetime import datetime
import sys

API_URL = 'http://localhost:5001/api/automation'
USER_ID = 1
HEADERS = {'Content-Type': 'application/json', 'X-User-ID': str(USER_ID)}


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_complete_workflow():
    """Test complete workflow lifecycle"""
    
    print_section("VISUAL AUTOMATION CANVAS - COMPLETE FLOW TEST")
    
    # Generate unique slug
    slug = f"workflow-test-{int(datetime.now().timestamp())}"
    thread_id = 1  # Use test thread
    
    try:
        # ============================================================
        # STEP 1: Create workflow
        # ============================================================
        print("[STEP 1] Creating draft workflow...")
        
        workflow_data = {
            "slug": slug,
            "title": "Test Email to Sheets Automation",
            "description": "Test workflow for email processing and Google Sheets integration",
            "category": "email",
            "ui_json": {
                "shapes": [
                    {
                        "id": "s1",
                        "type": "hexagon",
                        "text": "New Gmail Email",
                        "x": 100,
                        "y": 100,
                        "width": 120,
                        "height": 80
                    },
                    {
                        "id": "s2",
                        "type": "rectangle",
                        "text": "Extract Invoice Data",
                        "x": 300,
                        "y": 100,
                        "width": 150,
                        "height": 60
                    },
                    {
                        "id": "s3",
                        "type": "rectangle",
                        "text": "Save to Google Sheets",
                        "x": 500,
                        "y": 100,
                        "width": 150,
                        "height": 60
                    },
                    {
                        "id": "s4",
                        "type": "circle",
                        "text": "Complete",
                        "x": 700,
                        "y": 100,
                        "width": 80,
                        "height": 80
                    }
                ],
                "connections": [
                    {"from": "s1", "to": "s2", "id": "c1"},
                    {"from": "s2", "to": "s3", "id": "c2"},
                    {"from": "s3", "to": "s4", "id": "c3"}
                ]
            },
            "execution_json": {
                "steps": [
                    {
                        "tool": "gmail_list_messages",
                        "params": {"max_results": 10}
                    },
                    {
                        "tool": "ai_extract_invoice",
                        "params": {"text": "{{email.body}}"}
                    },
                    {
                        "tool": "google_sheets_append_row",
                        "params": {
                            "spreadsheet_id": "test_sheet",
                            "data": "{{invoice}}"
                        }
                    }
                ]
            },
            "status": "draft"
        }
        
        response = requests.post(
            f'{API_URL}/save',
            json=workflow_data,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"Error creating workflow: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"Workflow creation failed: {result}")
            return False
        
        print(f"SUCCESS - Workflow created")
        print(f"  Slug: {slug}")
        print(f"  ID: {result['automation_id']}")
        print(f"  Shapes: {len(workflow_data['ui_json']['shapes'])}")
        print(f"  Connections: {len(workflow_data['ui_json']['connections'])}")
        
        
        # ============================================================
        # STEP 2: Link to thread
        # ============================================================
        print(f"\n[STEP 2] Linking workflow to thread {thread_id}...")
        
        link_data = {
            "thread_id": thread_id,
            "workflow_slug": slug,
            "workflow_title": workflow_data['title']
        }
        
        response = requests.post(
            f'{API_URL}/link-to-thread',
            json=link_data,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Error linking to thread: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"Thread linking failed: {result}")
            return False
        
        print(f"SUCCESS - Linked to thread")
        print(f"  Thread ID: {result['thread_id']}")
        print(f"  Workflow: {result['workflow_slug']}")
        
        
        # ============================================================
        # STEP 3: Publish workflow
        # ============================================================
        print(f"\n[STEP 3] Publishing workflow...")
        
        publish_data = {
            "thread_id": thread_id,
            "automation_title": "Test Email Automation (Live)",
            "schedule_cron": "0 */1 * * *",  # Hourly
            "timezone": "UTC"
        }
        
        response = requests.post(
            f'{API_URL}/{slug}/publish',
            json=publish_data,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 400:
            # Validation failed
            result = response.json()
            print("VALIDATION FAILED")
            validation = result.get('validation', {})
            if validation.get('errors'):
                print(f"  Errors:")
                for error in validation['errors']:
                    print(f"    - {error}")
            if validation.get('warnings'):
                print(f"  Warnings:")
                for warning in validation['warnings']:
                    print(f"    - {warning}")
            return False
        
        if response.status_code != 200:
            print(f"Error publishing workflow: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"Publishing failed: {result}")
            return False
        
        print(f"SUCCESS - Workflow published")
        print(f"  Automation slug: {result['automation_slug']}")
        print(f"  Title: {result['automation_title']}")
        print(f"  Validation: PASSED")
        
        validation = result.get('validation', {})
        if validation.get('warnings'):
            print(f"  Warnings ({len(validation['warnings'])}):")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        
        if result.get('scheduled'):
            print(f"  Scheduled: YES")
            print(f"  Next run: {result.get('next_run')}")
            print(f"  Task ID: {result.get('task_id')}")
        else:
            print(f"  Scheduled: NO (manual execution only)")
        
        if result.get('thread_linked'):
            print(f"  Thread linked: YES (ID: {result.get('thread_id')})")
        
        
        # ============================================================
        # STEP 4: Check status
        # ============================================================
        print(f"\n[STEP 4] Checking workflow status...")
        
        response = requests.get(
            f'{API_URL}/{slug}/status',
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 404:
            print(f"Workflow not found: {slug}")
            return False
        
        if response.status_code != 200:
            print(f"Error getting status: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"Status check failed: {result}")
            return False
        
        workflow = result['workflow']
        exec_status = result['execution_status']
        
        print(f"SUCCESS - Status retrieved")
        print(f"\nWorkflow Info:")
        print(f"  Slug: {workflow['slug']}")
        print(f"  Title: {workflow['title']}")
        print(f"  Status: {workflow['status']}")
        print(f"  Is scheduled: {workflow['is_scheduled']}")
        if workflow.get('schedule_cron'):
            print(f"  Schedule: {workflow['schedule_cron']}")
        if workflow.get('next_run'):
            print(f"  Next run: {workflow['next_run']}")
        print(f"  Created: {workflow['created_at']}")
        print(f"  Updated: {workflow['updated_at']}")
        
        print(f"\nExecution Stats:")
        print(f"  Currently running: {exec_status['currently_running']}")
        print(f"  Total executions: {exec_status['total_executions']}")
        success_rate = exec_status['success_rate'] * 100
        print(f"  Success rate: {success_rate:.1f}%")
        
        if exec_status.get('last_execution'):
            last_exec = exec_status['last_execution']
            print(f"\nLast Execution:")
            print(f"  ID: {last_exec['execution_id']}")
            print(f"  Started: {last_exec['started_at']}")
            print(f"  Status: {last_exec['status']}")
            if last_exec.get('completed_at'):
                print(f"  Completed: {last_exec['completed_at']}")
            if last_exec.get('duration_ms'):
                print(f"  Duration: {last_exec['duration_ms']}ms")
            if last_exec.get('error_message'):
                print(f"  Error: {last_exec['error_message']}")
        else:
            print(f"\n  (No executions yet)")
        
        
        # ============================================================
        # STEP 5: Verify workflow retrieval by slug
        # ============================================================
        print(f"\n[STEP 5] Verifying workflow retrieval...")
        
        response = requests.get(
            f'{API_URL}/list',
            params={'slug': slug},
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Error retrieving workflow: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"Retrieval failed: {result}")
            return False
        
        workflows = result.get('workflows', [])
        if len(workflows) == 0:
            print(f"Workflow not found in list")
            return False
        
        workflow = workflows[0]
        print(f"SUCCESS - Workflow retrieved")
        print(f"  Found: {len(workflows)} workflow(s)")
        print(f"  ID: {workflow['id']}")
        print(f"  Slug: {workflow['slug']}")
        print(f"  Title: {workflow['title']}")
        print(f"  Status: {workflow['status']}")
        
        
        # ============================================================
        # SUCCESS
        # ============================================================
        print_section("ALL TESTS PASSED!")
        
        print(f"Test Summary:")
        print(f"  Workflow slug: {slug}")
        print(f"  Thread ID: {thread_id}")
        print(f"  Status: Published and active")
        print(f"  Scheduled: Hourly (0 */1 * * *)")
        print(f"\nYou can now:")
        print(f"  1. Check thread {thread_id} for workflow pills")
        print(f"  2. Monitor execution history")
        print(f"  3. Edit workflow in canvas")
        print(f"  4. View automation logs")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to API server")
        print("Make sure Flask server is running:")
        print("  cd C:\\Users\\gpoli\\GIT\\AI_agents\\AI_infrastructure")
        print("  python flask_app.py")
        return False
        
    except Exception as e:
        print(f"\nERROR: Unexpected exception")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print("\nVisual Automation Canvas - Complete Flow Test")
    print(f"Testing against: {API_URL}")
    print(f"User ID: {USER_ID}")
    
    success = test_complete_workflow()
    
    if success:
        print("\nStatus: SUCCESS")
        sys.exit(0)
    else:
        print("\nStatus: FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
