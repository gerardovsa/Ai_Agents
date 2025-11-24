"""
Test Milestone Creation After Fix

Tests that milestones can now be created successfully after fixing the
missing cursor.execute() calls in synergy_routes.py
"""

import sys
import os

# Add project root to path to access tools/registry_v3.py
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from tools.registry_v3 import RegistryV3

registry = RegistryV3()

print('=' * 70)
print('TESTING MILESTONE CREATION FIX')
print('=' * 70)
print()

print('Creating test session with 2 milestones...')
result = registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='Test Milestone Creation Fix',
    description='Testing that milestones now create successfully',
    platforms_involved=['sheets', 'gmail'],
    priority='medium',
    start_in_column='in_progress',
    tags=['test', 'milestone-fix'],
    use_milestones=True,
    initial_milestones=[
        {
            'milestone_name': 'Phase 1: Setup',
            'description': 'Initial setup phase',
            'tasks': [
                'Configure environment',
                {
                    'task': 'Install dependencies',
                    'subtasks': ['Install Python packages', 'Install Node modules']
                }
            ],
            'priority': 'high',
            'due_date': '2025-12-01',
            'estimated_hours': 4,
            'tags': ['setup']
        },
        {
            'milestone_name': 'Phase 2: Testing',
            'description': 'Run tests and validate',
            'tasks': [
                'Run unit tests',
                'Run integration tests',
                'Verify results'
            ],
            'priority': 'medium',
            'due_date': '2025-12-05',
            'estimated_hours': 3,
            'tags': ['testing']
        }
    ],
    _user_id=1,
    _injected_credentials=True
)

print()
print('=' * 70)
print('RESULT:')
print('=' * 70)
print(f'Success: {result.get("success", True)}')
print(f'Message: {result.get("message")}')
print(f'Session ID: {result.get("session_id")}')
print(f'Milestones Created: {result.get("milestone_count", 0)}')
print(f'Milestones Array: {result.get("milestones_created", [])}')
print()

if result.get("milestone_count", 0) == 2:
    print('SUCCESS! Milestones created correctly!')
else:
    print('ISSUE: Expected 2 milestones, got:', result.get("milestone_count", 0))
