"""
Create Example Synergy Sessions with Milestones

FILE: tools/testing/create_example_synergy_sessions.py
PURPOSE: Generate realistic example Synergy sessions to populate the database with diverse project types

DESCRIPTION:
    This script demonstrates the synergy_smart_project_tracker tool with milestone-based structure.
    Creates 5 different project types:
    1. E-commerce Platform Development (4 milestones, CRITICAL priority)
    2. Customer Database Migration (3 milestones, HIGH priority)
    3. Marketing Campaign Automation (3 milestones, HIGH priority)
    4. Employee Onboarding Automation (3 milestones, MEDIUM priority)
    5. Stripe Payment API Integration (3 milestones, CRITICAL priority)

USAGE:
    From project root:
        python tools/testing/create_example_synergy_sessions.py
    
    Or from tools/testing directory:
        python create_example_synergy_sessions.py

FEATURES DEMONSTRATED:
    - use_milestones=True parameter for milestone-based structure
    - initial_milestones array with complete milestone definitions
    - Task and subtask structures
    - Milestone dependencies (depends_on_milestone_id)
    - Priority levels (critical, high, medium)
    - Due dates and time estimates
    - Tags and platform associations
    - Different Kanban starting columns (in_progress, backlog)

EXPECTED OUTPUT:
    - 5 Synergy sessions created in synergy_sessions.synergy_sessions table
    - 16 total milestones across all sessions
    - Sessions visible at http://localhost:5001

REQUIREMENTS:
    - Flask server running (for milestone creation API)
    - Supabase database configured
    - Tool registry loaded with synergy tools

NOTES:
    - Session IDs are auto-generated with format: sess_YYYYMMDD_HHMM_title_slug
    - uses_milestones flag should be set to True in database
    - Milestones are created via POST to /api/synergy/milestone/create

LAST MODIFIED: 2025-11-24 - Initial creation with 5 diverse examples
"""

import sys
import os

# Add project root to path to access tools/registry_v3.py
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from tools.registry_v3 import RegistryV3

# Initialize registry
registry = RegistryV3()

print('=' * 70)
print('CREATING EXAMPLE SYNERGY SESSIONS WITH MILESTONES')
print('=' * 70)
print()

# Example 1: E-commerce Platform Development
print('Creating Example 1: E-commerce Platform Development...')
result1 = registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='E-commerce Platform Development',
    description='Build complete online store with product catalog, shopping cart, and payment integration',
    platforms_involved=['shopify', 'stripe', 'gmail', 'sheets', 'slack'],
    priority='critical',
    start_in_column='in_progress',
    tags=['ecommerce', 'development', 'multi-phase'],
    use_milestones=True,
    initial_milestones=[
        {
            'milestone_name': 'Phase 1: Store Setup & Design',
            'description': 'Configure Shopify store and design theme',
            'tasks': [
                {
                    'task': 'Shopify store configuration',
                    'subtasks': [
                        'Create Shopify account',
                        'Select and customize theme',
                        'Configure store settings'
                    ]
                },
                'Upload brand assets and logo',
                'Set up navigation and menu structure'
            ],
            'priority': 'critical',
            'due_date': '2025-12-05',
            'estimated_hours': 16,
            'tags': ['shopify', 'design']
        },
        {
            'milestone_name': 'Phase 2: Product Catalog',
            'description': 'Add products and inventory management',
            'tasks': [
                'Create product categories',
                {
                    'task': 'Add products with details',
                    'subtasks': [
                        'Write product descriptions',
                        'Upload product images',
                        'Set pricing and variants'
                    ]
                },
                'Configure inventory tracking',
                'Set up product collections'
            ],
            'priority': 'high',
            'due_date': '2025-12-12',
            'estimated_hours': 24,
            'tags': ['shopify', 'inventory'],
            'depends_on_milestone_id': 1
        },
        {
            'milestone_name': 'Phase 3: Payment & Checkout',
            'description': 'Integrate Stripe and configure checkout flow',
            'tasks': [
                'Connect Stripe payment gateway',
                'Configure shipping rates',
                'Set up tax calculations',
                'Customize checkout page',
                'Test payment processing'
            ],
            'priority': 'critical',
            'due_date': '2025-12-18',
            'estimated_hours': 12,
            'tags': ['stripe', 'payments'],
            'depends_on_milestone_id': 2
        },
        {
            'milestone_name': 'Phase 4: Automation & Launch',
            'description': 'Set up email automation and launch store',
            'tasks': [
                'Configure order confirmation emails',
                'Set up abandoned cart recovery',
                'Create customer notification triggers',
                'Connect analytics tracking',
                'Final testing and launch'
            ],
            'priority': 'high',
            'due_date': '2025-12-22',
            'estimated_hours': 10,
            'tags': ['automation', 'gmail'],
            'depends_on_milestone_id': 3
        }
    ],
    _user_id=1,
    _injected_credentials=True
)
print(f'Success: {result1.get("message")}')
print(f'   Session ID: {result1.get("session_id")}')
print(f'   Milestones: {result1.get("milestone_count")}')
print()

# Example 2: Customer Database Migration
print('Creating Example 2: Customer Database Migration...')
result2 = registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='Customer Database Migration',
    description='Migrate 5000+ customer records from legacy CRM to Google Sheets with validation',
    platforms_involved=['sheets', 'forms', 'gmail', 'drive'],
    priority='high',
    start_in_column='backlog',
    tags=['migration', 'database', 'data-processing'],
    use_milestones=True,
    initial_milestones=[
        {
            'milestone_name': 'Phase 1: Database Design',
            'description': 'Design new database schema and structure',
            'tasks': [
                {
                    'task': 'Create Google Sheet template',
                    'subtasks': [
                        'Define customer data fields',
                        'Set up data validation rules',
                        'Create reference lookup tables'
                    ]
                },
                'Design data relationships',
                'Set up access permissions'
            ],
            'priority': 'critical',
            'due_date': '2025-11-30',
            'estimated_hours': 8,
            'tags': ['sheets', 'design']
        },
        {
            'milestone_name': 'Phase 2: Data Export & Cleaning',
            'description': 'Export data from legacy system and clean',
            'tasks': [
                'Connect to legacy CRM',
                'Export customer records to CSV',
                'Export transaction history',
                'Clean and format data',
                'Validate data integrity'
            ],
            'priority': 'high',
            'due_date': '2025-12-07',
            'estimated_hours': 16,
            'tags': ['data-processing', 'migration']
        },
        {
            'milestone_name': 'Phase 3: Data Import',
            'description': 'Import cleaned data into Google Sheets',
            'tasks': [
                'Import customer records',
                'Import transaction history',
                'Verify data relationships',
                'Run validation checks',
                'Fix import errors'
            ],
            'priority': 'critical',
            'due_date': '2025-12-14',
            'estimated_hours': 12,
            'tags': ['sheets', 'import']
        }
    ],
    _user_id=1,
    _injected_credentials=True
)
print(f'Success: {result2.get("message")}')
print(f'   Session ID: {result2.get("session_id")}')
print(f'   Milestones: {result2.get("milestone_count")}')
print()

# Example 3: Marketing Campaign Automation
print('Creating Example 3: Marketing Campaign Automation...')
result3 = registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='Q4 Marketing Campaign Automation',
    description='Automated email marketing campaign with forms, tracking, and analytics',
    platforms_involved=['gmail', 'forms', 'sheets', 'calendar'],
    priority='high',
    start_in_column='in_progress',
    tags=['marketing', 'automation', 'campaign'],
    use_milestones=True,
    initial_milestones=[
        {
            'milestone_name': 'Phase 1: Campaign Planning',
            'description': 'Define campaign strategy and content',
            'tasks': [
                'Define campaign objectives',
                'Identify target audience segments',
                'Create content calendar',
                'Write email copy drafts',
                'Design email templates'
            ],
            'priority': 'high',
            'due_date': '2025-11-28',
            'estimated_hours': 10,
            'tags': ['planning', 'content']
        },
        {
            'milestone_name': 'Phase 2: Lead Capture Setup',
            'description': 'Create forms and landing pages',
            'tasks': [
                {
                    'task': 'Create Google Forms',
                    'subtasks': [
                        'Design signup form',
                        'Create feedback form',
                        'Set up conditional logic'
                    ]
                },
                'Connect form to tracking sheet',
                'Set up auto-responder emails'
            ],
            'priority': 'critical',
            'due_date': '2025-12-03',
            'estimated_hours': 8,
            'tags': ['forms', 'gmail']
        },
        {
            'milestone_name': 'Phase 3: Email Sequences',
            'description': 'Build automated email sequences',
            'tasks': [
                'Create welcome email series',
                'Build promotional email sequence',
                'Set up follow-up triggers',
                'Test email delivery',
                'Configure tracking and analytics'
            ],
            'priority': 'high',
            'due_date': '2025-12-10',
            'estimated_hours': 12,
            'tags': ['gmail', 'automation']
        }
    ],
    _user_id=1,
    _injected_credentials=True
)
print(f'Success: {result3.get("message")}')
print(f'   Session ID: {result3.get("session_id")}')
print(f'   Milestones: {result3.get("milestone_count")}')
print()

# Example 4: Team Onboarding System
print('Creating Example 4: Team Onboarding System...')
result4 = registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='Employee Onboarding Automation',
    description='Streamlined onboarding process with document generation and task tracking',
    platforms_involved=['docs', 'sheets', 'gmail', 'calendar', 'drive'],
    priority='medium',
    start_in_column='backlog',
    tags=['hr', 'onboarding', 'automation'],
    use_milestones=True,
    initial_milestones=[
        {
            'milestone_name': 'Phase 1: Document Templates',
            'description': 'Create standardized onboarding documents',
            'tasks': [
                {
                    'task': 'Create Google Docs templates',
                    'subtasks': [
                        'Employee handbook template',
                        'Welcome letter template',
                        'Equipment checklist template'
                    ]
                },
                'Create training schedule template',
                'Set up document sharing permissions'
            ],
            'priority': 'medium',
            'due_date': '2025-12-01',
            'estimated_hours': 6,
            'tags': ['docs', 'templates']
        },
        {
            'milestone_name': 'Phase 2: Tracking System',
            'description': 'Build onboarding progress tracker',
            'tasks': [
                'Create tracking spreadsheet',
                'Set up new hire data entry form',
                'Configure status tracking',
                'Add completion checkboxes',
                'Set up reminder notifications'
            ],
            'priority': 'high',
            'due_date': '2025-12-08',
            'estimated_hours': 8,
            'tags': ['sheets', 'tracking']
        },
        {
            'milestone_name': 'Phase 3: Email Automation',
            'description': 'Automate onboarding email sequences',
            'tasks': [
                'Create welcome email template',
                'Set up Day 1 checklist email',
                'Create Week 1 check-in email',
                'Configure automated reminders',
                'Test email triggers'
            ],
            'priority': 'medium',
            'due_date': '2025-12-15',
            'estimated_hours': 6,
            'tags': ['gmail', 'automation']
        }
    ],
    _user_id=1,
    _injected_credentials=True
)
print(f'Success: {result4.get("message")}')
print(f'   Session ID: {result4.get("session_id")}')
print(f'   Milestones: {result4.get("milestone_count")}')
print()

# Example 5: API Integration Project
print('Creating Example 5: API Integration Project...')
result5 = registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='Stripe Payment API Integration',
    description='Integrate Stripe payment processing with order management system',
    platforms_involved=['stripe', 'sheets', 'gmail', 'slack'],
    priority='critical',
    start_in_column='in_progress',
    tags=['api', 'integration', 'payments'],
    use_milestones=True,
    initial_milestones=[
        {
            'milestone_name': 'Phase 1: API Setup',
            'description': 'Configure Stripe API credentials and test environment',
            'tasks': [
                'Create Stripe test account',
                'Generate API keys',
                'Set up webhook endpoints',
                'Configure test payment methods',
                'Document API credentials'
            ],
            'priority': 'critical',
            'due_date': '2025-11-27',
            'estimated_hours': 4,
            'tags': ['stripe', 'setup']
        },
        {
            'milestone_name': 'Phase 2: Payment Processing',
            'description': 'Implement payment capture and processing',
            'tasks': [
                {
                    'task': 'Build payment processing logic',
                    'subtasks': [
                        'Create payment intent endpoint',
                        'Handle payment confirmations',
                        'Process refunds and disputes'
                    ]
                },
                'Test payment flows',
                'Add error handling'
            ],
            'priority': 'critical',
            'due_date': '2025-12-05',
            'estimated_hours': 16,
            'tags': ['stripe', 'development']
        },
        {
            'milestone_name': 'Phase 3: Order Tracking',
            'description': 'Connect payments to order management',
            'tasks': [
                'Create order tracking sheet',
                'Link payments to orders',
                'Set up status updates',
                'Configure email notifications',
                'Add Slack alerts for high-value orders'
            ],
            'priority': 'high',
            'due_date': '2025-12-12',
            'estimated_hours': 10,
            'tags': ['sheets', 'gmail', 'slack']
        }
    ],
    _user_id=1,
    _injected_credentials=True
)
print(f'Success: {result5.get("message")}')
print(f'   Session ID: {result5.get("session_id")}')
print(f'   Milestones: {result5.get("milestone_count")}')
print()

print('=' * 70)
print('ALL 5 EXAMPLE SESSIONS CREATED!')
print('=' * 70)
print()
print('Sessions created:')
print('  1. E-commerce Platform (4 milestones) - CRITICAL')
print('  2. Database Migration (3 milestones) - HIGH')
print('  3. Marketing Campaign (3 milestones) - HIGH')
print('  4. Team Onboarding (3 milestones) - MEDIUM')
print('  5. API Integration (3 milestones) - CRITICAL')
print()
print('Total: 16 milestones across 5 sessions')
print()
print('View dashboard at: http://localhost:5001')
