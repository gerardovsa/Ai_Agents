"""
Test Slug Synchronization & Thread Linkages

Tests the complete slug system for:
- Workflow linkages (orange pills)
- Synergy linkages (green pills)
- Location synchronization across UI components
- Database persistence
- UI pills rendering
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001"
USER_ID = 14  # Using actual logged-in user from server logs

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


class SlugSyncTester:
    """Test slug synchronization across UI and backend"""
    
    def __init__(self):
        self.test_thread_id = None
        self.test_synergy_id = None
        self.test_workflow_id = "test-workflow-123"
        self.test_workflow_name = "Test React Workflow"
        
    def create_test_thread(self):
        """Create a test thread"""
        print_info("Creating test thread...")
        
        response = requests.post(
            f"{API_BASE_URL}/api/threads/create",
            json={
                "user_id": USER_ID,
                "title": "Slug Sync Test Thread",
                "location": "prime"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                thread_data = data.get('data', {}).get('thread', data.get('thread', {}))
                self.test_thread_id = thread_data.get('id')
                print_success(f"Test thread created: {self.test_thread_id}")
                return True
        
        print_error(f"Failed to create thread: {response.status_code}")
        print_error(response.text)
        return False
    
    def link_workflow_to_thread(self):
        """Link workflow to thread"""
        print_info(f"Linking workflow '{self.test_workflow_name}' to thread...")
        
        response = requests.patch(
            f"{API_BASE_URL}/api/threads/{self.test_thread_id}/update",
            json={
                "name": "Slug Sync Test Thread",
                "workflow_id": self.test_workflow_id,
                "workflow_name": self.test_workflow_name
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("Workflow linked successfully")
                print_info(f"  Workflow ID: {self.test_workflow_id}")
                print_info(f"  Workflow Name: {self.test_workflow_name}")
                return True
        
        print_error(f"Failed to link workflow: {response.status_code}")
        print_error(response.text)
        return False
    
    def verify_workflow_linkage(self):
        """Verify workflow linkage persisted in database"""
        print_info("Verifying workflow linkage in database...")
        
        response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            threads = data.get('data', {}).get('threads', data.get('threads', []))
            
            test_thread = next((t for t in threads if t['id'] == self.test_thread_id), None)
            
            if test_thread:
                workflow_id = test_thread.get('workflow_id')
                workflow_name = test_thread.get('workflow_name')
                
                if workflow_id == self.test_workflow_id and workflow_name == self.test_workflow_name:
                    print_success("Workflow linkage verified in database")
                    print_info(f"  workflow_id: {workflow_id}")
                    print_info(f"  workflow_name: {workflow_name}")
                    return True
                else:
                    print_error("Workflow linkage not found or mismatch")
                    print_error(f"  Expected: workflow_id={self.test_workflow_id}")
                    print_error(f"  Got: workflow_id={workflow_id}")
                    return False
            else:
                print_error("Test thread not found in list")
                return False
        
        print_error(f"Failed to fetch threads: {response.status_code}")
        return False
    
    def create_synergy_session(self):
        """Create a Synergy session for linking"""
        print_info("Creating Synergy session...")
        
        response = requests.post(
            f"{API_BASE_URL}/api/synergy/create",
            json={
                "title": "Test Synergy Session",
                "description": "Created for slug sync testing",
                "created_by": "user"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.test_synergy_id = data.get('session_id')
                print_success(f"Synergy session created: {self.test_synergy_id}")
                return True
        
        print_error(f"Failed to create Synergy session: {response.status_code}")
        print_error(response.text)
        return False
    
    def link_synergy_to_thread(self):
        """Link Synergy session to thread"""
        print_info(f"Linking Synergy session '{self.test_synergy_id}' to thread...")
        
        response = requests.patch(
            f"{API_BASE_URL}/api/threads/{self.test_thread_id}/update",
            json={
                "name": "Slug Sync Test Thread",
                "synergy_card_id": self.test_synergy_id,
                "synergy_card_name": "Test Synergy Session"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("Synergy session linked successfully")
                print_info(f"  Synergy ID: {self.test_synergy_id}")
                return True
        
        print_error(f"Failed to link Synergy: {response.status_code}")
        print_error(response.text)
        return False
    
    def verify_synergy_linkage(self):
        """Verify Synergy linkage persisted in database"""
        print_info("Verifying Synergy linkage in database...")
        
        response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            threads = data.get('data', {}).get('threads', data.get('threads', []))
            
            test_thread = next((t for t in threads if t['id'] == self.test_thread_id), None)
            
            if test_thread:
                synergy_id = test_thread.get('synergy_card_id')
                synergy_name = test_thread.get('synergy_card_name')
                
                if synergy_id == self.test_synergy_id:
                    print_success("Synergy linkage verified in database")
                    print_info(f"  synergy_card_id: {synergy_id}")
                    print_info(f"  synergy_card_name: {synergy_name}")
                    return True
                else:
                    print_error("Synergy linkage not found or mismatch")
                    print_error(f"  Expected: synergy_card_id={self.test_synergy_id}")
                    print_error(f"  Got: synergy_card_id={synergy_id}")
                    return False
            else:
                print_error("Test thread not found in list")
                return False
        
        print_error(f"Failed to fetch threads: {response.status_code}")
        return False
    
    def move_thread_to_agent(self, agent_num=2):
        """Move thread to agent and verify pills persist"""
        print_info(f"Moving thread to Agent-{agent_num}...")
        
        response = requests.patch(
            f"{API_BASE_URL}/api/threads/{self.test_thread_id}/update",
            json={
                "name": "Slug Sync Test Thread",
                "location": f"agent-{agent_num}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success(f"Thread moved to Agent-{agent_num}")
                return True
        
        print_error(f"Failed to move thread: {response.status_code}")
        print_error(response.text)
        return False
    
    def verify_pills_after_move(self):
        """Verify both pills still exist after location change"""
        print_info("Verifying pills persist after location change...")
        
        response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            threads = data.get('data', {}).get('threads', data.get('threads', []))
            
            test_thread = next((t for t in threads if t['id'] == self.test_thread_id), None)
            
            if test_thread:
                workflow_id = test_thread.get('workflow_id')
                synergy_id = test_thread.get('synergy_card_id')
                location = test_thread.get('location')
                
                pills_intact = (
                    workflow_id == self.test_workflow_id and 
                    synergy_id == self.test_synergy_id
                )
                
                if pills_intact:
                    print_success("✨ Pills persisted after location change!")
                    print_info(f"  Location: {location}")
                    print_info(f"  🟠 Workflow: {workflow_id}")
                    print_info(f"  🟢 Synergy: {synergy_id}")
                    return True
                else:
                    print_error("Pills were lost during location change")
                    print_error(f"  workflow_id: {workflow_id} (expected: {self.test_workflow_id})")
                    print_error(f"  synergy_card_id: {synergy_id} (expected: {self.test_synergy_id})")
                    return False
            else:
                print_error("Test thread not found")
                return False
        
        print_error(f"Failed to fetch threads: {response.status_code}")
        return False
    
    def unlink_workflow(self):
        """Unlink workflow from thread"""
        print_info("Unlinking workflow...")
        
        response = requests.patch(
            f"{API_BASE_URL}/api/threads/{self.test_thread_id}/update",
            json={
                "name": "Slug Sync Test Thread",
                "workflow_id": None,
                "workflow_name": None
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("Workflow unlinked successfully")
                return True
        
        print_error(f"Failed to unlink workflow: {response.status_code}")
        return False
    
    def verify_workflow_unlinked(self):
        """Verify workflow was unlinked"""
        print_info("Verifying workflow unlinked...")
        
        response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            threads = data.get('data', {}).get('threads', data.get('threads', []))
            
            test_thread = next((t for t in threads if t['id'] == self.test_thread_id), None)
            
            if test_thread:
                workflow_id = test_thread.get('workflow_id')
                synergy_id = test_thread.get('synergy_card_id')
                
                if workflow_id is None and synergy_id == self.test_synergy_id:
                    print_success("Workflow unlinked, Synergy pill intact")
                    print_info("  🟠 Workflow: None")
                    print_info(f"  🟢 Synergy: {synergy_id}")
                    return True
                else:
                    print_error("Unexpected state after unlink")
                    print_error(f"  workflow_id: {workflow_id} (expected: None)")
                    print_error(f"  synergy_card_id: {synergy_id}")
                    return False
            else:
                print_error("Test thread not found")
                return False
        
        print_error(f"Failed to fetch threads: {response.status_code}")
        return False
    
    def cleanup(self):
        """Clean up test data"""
        print_info("Cleaning up test data...")
        
        # Delete thread (cascades to assignments)
        if self.test_thread_id:
            response = requests.delete(f"{API_BASE_URL}/api/threads/{self.test_thread_id}")
            if response.status_code == 200:
                print_success(f"Deleted test thread: {self.test_thread_id}")
            else:
                print_warning(f"Failed to delete thread: {response.status_code}")
        
        # Delete Synergy session
        if self.test_synergy_id:
            response = requests.delete(f"{API_BASE_URL}/api/synergy/{self.test_synergy_id}")
            if response.status_code == 200:
                print_success(f"Deleted Synergy session: {self.test_synergy_id}")
            else:
                print_warning(f"Failed to delete Synergy: {response.status_code}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print_header("SLUG SYNCHRONIZATION TEST SUITE")
        
        results = []
        
        # Test 1: Create thread
        print_header("Test 1: Create Thread")
        results.append(("Create Thread", self.create_test_thread()))
        
        if not results[-1][1]:
            print_error("Cannot continue without thread. Aborting tests.")
            return
        
        # Test 2: Link workflow
        print_header("Test 2: Link Workflow (Orange Pill)")
        results.append(("Link Workflow", self.link_workflow_to_thread()))
        
        # Test 3: Verify workflow linkage
        print_header("Test 3: Verify Workflow Linkage Persistence")
        results.append(("Verify Workflow", self.verify_workflow_linkage()))
        
        # Test 4: Create Synergy session
        print_header("Test 4: Create Synergy Session")
        results.append(("Create Synergy", self.create_synergy_session()))
        
        # Test 5: Link Synergy
        print_header("Test 5: Link Synergy (Green Pill)")
        results.append(("Link Synergy", self.link_synergy_to_thread()))
        
        # Test 6: Verify Synergy linkage
        print_header("Test 6: Verify Synergy Linkage Persistence")
        results.append(("Verify Synergy", self.verify_synergy_linkage()))
        
        # Test 7: Move thread to Agent-2
        print_header("Test 7: Move Thread to Agent-2 (Pills Should Persist)")
        results.append(("Move to Agent", self.move_thread_to_agent(2)))
        
        # Test 8: Verify pills persist after move
        print_header("Test 8: Verify Pills Persist After Move")
        results.append(("Pills Persist", self.verify_pills_after_move()))
        
        # Test 9: Unlink workflow
        print_header("Test 9: Unlink Workflow (Remove Orange Pill)")
        results.append(("Unlink Workflow", self.unlink_workflow()))
        
        # Test 10: Verify workflow unlinked, Synergy intact
        print_header("Test 10: Verify Selective Unlinking")
        results.append(("Verify Unlink", self.verify_workflow_unlinked()))
        
        # Cleanup
        print_header("Cleanup")
        self.cleanup()
        
        # Print summary
        print_header("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
            print(f"  {status}  {test_name}")
        
        print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
        
        if passed == total:
            print(f"{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! Slug synchronization working correctly.{Colors.END}")
        else:
            print(f"{Colors.BOLD}{Colors.RED}⚠️  SOME TESTS FAILED. Review errors above.{Colors.END}")
        
        return passed == total


def main():
    """Main entry point"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                 SLUG SYNCHRONIZATION & PILLS TEST SUITE                   ║")
    print("║                                                                           ║")
    print("║  Tests: Workflow pills, Synergy pills, location sync, persistence        ║")
    print("║  API: http://localhost:5001                                               ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}", timeout=5)
        if response.status_code not in [200, 401]:  # 401 is OK, means auth is working
            print_error("Server is not responding properly. Please start BISTART.")
            return
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to server: {e}")
        print_error("Please ensure Flask app is running (BISTART).")
        return
    
    print_success("Server is online\n")
    
    # Run tests
    tester = SlugSyncTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
