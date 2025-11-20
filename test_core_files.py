"""
Core Files Test Suite
Tests all 20 core files in AI_infrastructure/core/

Priority:
P0 - unified_session_manager, combined_agent_worker, agent_state_manager
P1 - unified_ai_client, prompt_injection_manager, unified_anthropic_client
P2 - confirmation_manager, context_aware_ai, sync_manager
P3 - Specialized/utility files
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
sys.path.insert(0, str(Path(__file__).parent))

# Test results tracking
test_results = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_header(file_name, priority):
    """Print test header"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing: {file_name} ({priority})")
    print(f"{'='*80}")

def test_import(module_path, class_name=None):
    """Test if module can be imported"""
    try:
        module = __import__(module_path, fromlist=[class_name] if class_name else [])
        if class_name:
            cls = getattr(module, class_name)
            print(f"✅ Import successful: {module_path}.{class_name}")
            return cls
        else:
            print(f"✅ Import successful: {module_path}")
            return module
    except Exception as e:
        print(f"❌ Import failed: {module_path} - {str(e)}")
        return None

# ============================================================================
# P0 - CRITICAL TESTS
# ============================================================================

def test_unified_session_manager():
    """Test unified_session_manager.py"""
    test_header("unified_session_manager.py", "P0 - CRITICAL")
    
    try:
        from core.unified_session_manager import UnifiedSessionManager, session_manager
        
        # Test 1: Global instance exists
        assert session_manager is not None
        print("✅ Global session_manager instance exists")
        
        # Test 2: Can create session
        session_id = session_manager.create_session(
            ui_context='test',
            agent_id='test_agent',
            source='test'
        )
        assert session_id is not None
        print(f"✅ Session created: {session_id}")
        
        # Test 3: Can get session
        session_data = session_manager.get_session(session_id)
        assert session_data is not None
        assert session_data['session_id'] == session_id
        print(f"✅ Session retrieved: {session_data['ui_context']}")
        
        # Test 4: Queue exists
        queue = session_manager.get_queue(session_id)
        assert queue is not None
        print("✅ SSE queue exists")
        
        test_results['passed'].append('unified_session_manager.py')
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f'unified_session_manager.py: {str(e)}')
        return False


def test_combined_agent_worker():
    """Test combined_agent_worker.py"""
    test_header("combined_agent_worker.py", "P0 - CRITICAL")
    
    try:
        from core.combined_agent_worker import (
            run_agent_worker,
            run_simple_agent_worker,
            agent_worker,
            execute_streaming_request,
            prune_conversation_for_context_limit
        )
        
        # Test 1: Functions exist
        assert callable(run_agent_worker)
        assert callable(run_simple_agent_worker)
        assert callable(agent_worker)
        assert callable(execute_streaming_request)
        assert callable(prune_conversation_for_context_limit)
        print("✅ All 5 functions imported successfully")
        
        # Test 2: Prune conversation (basic test)
        test_conversation = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'}
        ]
        pruned = prune_conversation_for_context_limit(test_conversation, max_estimated_tokens=100000)
        assert len(pruned) == 2
        print("✅ prune_conversation_for_context_limit works")
        
        test_results['passed'].append('combined_agent_worker.py')
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f'combined_agent_worker.py: {str(e)}')
        return False


def test_agent_state_manager():
    """Test agent_state_manager.py"""
    test_header("agent_state_manager.py", "P0 - CRITICAL")
    
    try:
        from core.agent_state_manager import agent_state_manager
        
        # Test 1: Global instance exists
        assert agent_state_manager is not None
        print("✅ Global agent_state_manager instance exists")
        
        # Test 2: Create state
        state = agent_state_manager.get_or_create_state(
            agent_id='test_agent',
            thread_id='test_thread_123',
            context='test'
        )
        assert state is not None
        assert state['status'] == 'idle'
        print(f"✅ State created: {state['agent_name']}")
        
        # Test 3: Get lock
        lock = agent_state_manager.get_lock('test_agent', 'test_thread_123')
        assert lock is not None
        print("✅ Execution lock retrieved")
        
        # Test 4: Get queue
        queue = agent_state_manager.get_queue('test_agent', 'test_thread_123')
        assert queue is not None
        print("✅ SSE queue retrieved")
        
        test_results['passed'].append('agent_state_manager.py')
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f'agent_state_manager.py: {str(e)}')
        return False


# ============================================================================
# P1 - HIGH PRIORITY TESTS
# ============================================================================

def test_unified_ai_client():
    """Test unified_ai_client.py"""
    test_header("unified_ai_client.py", "P1 - HIGH")
    
    try:
        from core.unified_ai_client import initialize_ai_client, UnifiedAIClient
        
        # Test 1: Can import
        assert UnifiedAIClient is not None
        assert callable(initialize_ai_client)
        print("✅ Classes and functions imported")
        
        # Note: Can't test API calls without credentials
        print("⚠️  API call tests skipped (requires credentials)")
        
        test_results['passed'].append('unified_ai_client.py')
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f'unified_ai_client.py: {str(e)}')
        return False


def test_prompt_injection_manager():
    """Test prompt_injection_manager.py"""
    test_header("prompt_injection_manager.py", "P1 - HIGH")
    
    try:
        from core.prompt_injection_manager import get_prompt_manager
        
        # Test 1: Can get manager
        manager = get_prompt_manager()
        assert manager is not None
        print("✅ Prompt manager retrieved")
        
        # Test 2: Can list quick actions
        quick_actions = manager.list_quick_actions()
        print(f"✅ Quick actions available: {len(quick_actions)} total")
        
        # Test 3: Can list library prompts
        library_prompts = manager.list_library_prompts()
        print(f"✅ Library prompts available: {len(library_prompts)} total")
        
        test_results['passed'].append('prompt_injection_manager.py')
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f'prompt_injection_manager.py: {str(e)}')
        return False


def test_unified_anthropic_client():
    """Test unified_anthropic_client.py"""
    test_header("unified_anthropic_client.py", "P1 - HIGH")
    
    try:
        from core.unified_anthropic_client import UnifiedAnthropicClient, anthropic_client
        
        # Test 1: Can import
        assert UnifiedAnthropicClient is not None
        print("✅ UnifiedAnthropicClient imported")
        
        # Note: Can't test API calls without credentials
        print("⚠️  API call tests skipped (requires Anthropic API key)")
        
        test_results['passed'].append('unified_anthropic_client.py')
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f'unified_anthropic_client.py: {str(e)}')
        return False


# ============================================================================
# P2 - MEDIUM PRIORITY TESTS
# ============================================================================

def test_import_only(module_path, class_name, file_name, priority):
    """Generic import test"""
    test_header(file_name, priority)
    
    try:
        result = test_import(module_path, class_name)
        if result:
            test_results['passed'].append(file_name)
            return True
        else:
            test_results['failed'].append(f"{file_name}: Import failed")
            return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        test_results['failed'].append(f"{file_name}: {str(e)}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests in priority order"""
    print("\n" + "="*80)
    print("🚀 CORE FILES TEST SUITE")
    print("="*80)
    print(f"Testing 20 files in AI_infrastructure/core/")
    print()
    
    # P0 - Critical
    print("\n" + "="*80)
    print("P0 - CRITICAL TESTS")
    print("="*80)
    test_unified_session_manager()
    test_combined_agent_worker()
    test_agent_state_manager()
    
    # P1 - High Priority
    print("\n" + "="*80)
    print("P1 - HIGH PRIORITY TESTS")
    print("="*80)
    test_unified_ai_client()
    test_prompt_injection_manager()
    test_unified_anthropic_client()
    
    # P2 - Medium Priority (import only)
    print("\n" + "="*80)
    print("P2 - MEDIUM PRIORITY TESTS (Import Only)")
    print("="*80)
    test_import_only('core.confirmation_manager', 'ConfirmationManager', 'confirmation_manager.py', 'P2')
    test_import_only('core.context_aware_ai', None, 'context_aware_ai.py', 'P2')
    test_import_only('core.sync_manager', 'KanbanSyncManager', 'sync_manager.py', 'P2')
    test_import_only('core.task_card_manager', None, 'task_card_manager.py', 'P2')
    
    # P3 - Low Priority (import only)
    print("\n" + "="*80)
    print("P3 - LOW PRIORITY TESTS (Import Only)")
    print("="*80)
    test_import_only('core.context_engine', None, 'context_engine.py', 'P3')
    test_import_only('core.event_triggers', None, 'event_triggers.py', 'P3')
    test_import_only('core.email_parser', None, 'email_parser.py', 'P3')
    test_import_only('core.email_to_pdf_converter', None, 'email_to_pdf_converter.py', 'P3')
    test_import_only('core.ip_location', 'get_location_dict', 'ip_location.py', 'P3')
    test_import_only('core.tool_result_limits', None, 'tool_result_limits.py', 'P3')
    test_import_only('core.module_blueprint_loader', None, 'module_blueprint_loader.py', 'P3')
    test_import_only('core.session_orchestrator', None, 'session_orchestrator.py', 'P3')
    test_import_only('core.tool_executor', 'ToolExecutor', 'tool_executor.py', 'P3')
    test_import_only('core.tool_processor', 'ToolCallProcessor', 'tool_processor.py', 'P3')
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {len(test_results['passed'])} files")
    print(f"❌ Failed: {len(test_results['failed'])} files")
    print(f"⏭️  Skipped: {len(test_results['skipped'])} files")
    
    if test_results['passed']:
        print(f"\n✅ PASSED ({len(test_results['passed'])}):")
        for file in test_results['passed']:
            print(f"  - {file}")
    
    if test_results['failed']:
        print(f"\n❌ FAILED ({len(test_results['failed'])}):")
        for file in test_results['failed']:
            print(f"  - {file}")
    
    if test_results['skipped']:
        print(f"\n⏭️  SKIPPED ({len(test_results['skipped'])}):")
        for file in test_results['skipped']:
            print(f"  - {file}")
    
    # Calculate success rate
    total = len(test_results['passed']) + len(test_results['failed'])
    if total > 0:
        success_rate = (len(test_results['passed']) / total) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)
    
    return len(test_results['failed']) == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
