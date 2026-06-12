"""
Create Comprehensive Synergy Session Example
Shows all features: milestones, tasks, subtasks, documents, links, predictions, dependencies
"""

import json
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import get_synergy_sessions_connection

def get_connection():
    """Get connection using shared database utility (auto-detects Supabase vs SQLite)"""
    return get_synergy_sessions_connection()

def create_comprehensive_example():
    """Create a full-featured Synergy session example"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Generate unique IDs
        session_id = f"syn_demo_{int(datetime.now().timestamp())}"
        
        print("=" * 80)
        print("CREATING COMPREHENSIVE SYNERGY SESSION EXAMPLE")
        print("=" * 80)
        
        # ===================================================================
        # STEP 1: Create Synergy Session with all fields
        # ===================================================================
        print("\n[1/5] Creating Synergy Session...")
        
        session_data = {
            'session_id': session_id,
            'title': 'E-Commerce Platform Redesign',
            'description': 'Complete redesign of the online store with new features: AI recommendations, live chat support, mobile-first design, and performance optimizations.',
            'kanban_column': 'in-progress',
            'status': 'active',
            'priority': 'high',
            'tags': json.dumps(['web-development', 'ui-ux', 'e-commerce', 'mobile']),
            'assignees': json.dumps([
                {'id': 'user_1', 'name': 'Sarah Chen', 'role': 'Project Lead'},
                {'id': 'user_2', 'name': 'Michael Rodriguez', 'role': 'Frontend Dev'},
                {'id': 'user_3', 'name': 'Aisha Patel', 'role': 'UX Designer'}
            ]),
            'due_date': (datetime.now() + timedelta(days=45)).isoformat(),
            'documents': json.dumps([
                {
                    'id': 'doc_1',
                    'title': 'Project Requirements',
                    'url': 'https://docs.google.com/document/d/abc123',
                    'type': 'google_doc'
                },
                {
                    'id': 'doc_2',
                    'title': 'Design System',
                    'url': 'https://www.figma.com/file/xyz789',
                    'type': 'figma'
                },
                {
                    'id': 'doc_3',
                    'title': 'API Documentation',
                    'url': 'internal://docs/api-v2',
                    'type': 'internal'
                }
            ]),
            'links': json.dumps([
                {
                    'id': 'link_1',
                    'name': 'GitHub Repository',
                    'url': 'https://github.com/company/ecommerce-platform'
                },
                {
                    'id': 'link_2',
                    'name': 'Staging Environment',
                    'url': 'https://staging.shop.company.com'
                }
            ]),
            'recent_activity': 'Key stakeholders: VP Product (weekly updates), Marketing Team (launch coordination), Customer Support (training needed). Budget approved: $150K. Launch target: Q1 2026.',
            'uses_milestones': True,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO synergy_sessions.synergy_sessions 
            (session_id, title, description, kanban_column, status, priority, tags, assignees, 
             due_date, documents, links, recent_activity, uses_milestones, 
             created_at, last_active)
            VALUES (%(session_id)s, %(title)s, %(description)s, %(kanban_column)s, %(status)s,
                    %(priority)s, %(tags)s, %(assignees)s, %(due_date)s, 
                    %(documents)s, %(links)s, %(recent_activity)s, %(uses_milestones)s,
                    %(created_at)s, %(last_active)s)
        """, session_data)
        
        print(f"   ✓ Session created: {session_id}")
        print(f"   ✓ Title: {session_data['title']}")
        print(f"   ✓ Assignees: {len(json.loads(session_data['assignees']))} team members")
        print(f"   ✓ Session documents: {len(json.loads(session_data['documents']))}")
        print(f"   ✓ Session links: {len(json.loads(session_data['links']))}")
        
        # ===================================================================
        # STEP 2: Create Milestones with Dependencies
        # ===================================================================
        print("\n[2/5] Creating Milestones with Dependencies...")
        
        milestones = [
            {
                'milestone_id': f'mile_{session_id}_1',
                'session_id': session_id,
                'milestone_number': 1,
                'milestone_name': 'Design & Research Phase',
                'description': 'User research, competitive analysis, wireframes, and design system creation',
                'completed': True,
                'completed_at': (datetime.now() - timedelta(days=15)).isoformat(),
                'due_date': (datetime.now() - timedelta(days=10)).isoformat(),
                'estimated_hours': 80.0,
                'actual_hours': 87.5,
                'milestone_order': 1,
                'depends_on_milestone_id': None,
                'blocked': False,
                'documents': json.dumps([
                    {'id': 'doc_1_1', 'name': 'User Research Report', 'url': 'https://docs.google.com/document/d/research123', 'type': 'google_doc'},
                    {'id': 'doc_1_2', 'name': 'Wireframes v2', 'url': 'https://figma.com/wireframes', 'type': 'figma'}
                ]),
                'links': json.dumps([
                    {'id': 'link_1_1', 'name': 'Competitor Analysis Sheet', 'url': 'https://sheets.google.com/competitor-analysis'}
                ])
            },
            {
                'milestone_id': f'mile_{session_id}_2',
                'session_id': session_id,
                'milestone_number': 2,
                'milestone_name': 'Frontend Development',
                'description': 'Build React components, implement design system, responsive layouts',
                'completed': False,
                'due_date': (datetime.now() + timedelta(days=15)).isoformat(),
                'estimated_hours': 120.0,
                'actual_hours': 0.0,
                'milestone_order': 2,
                'depends_on_milestone_id': f'mile_{session_id}_1',
                'blocked': False,
                'documents': json.dumps([
                    {'id': 'doc_2_1', 'name': 'Component Library Docs', 'url': 'internal://docs/components', 'type': 'internal'}
                ]),
                'links': json.dumps([
                    {'id': 'link_2_1', 'name': 'Storybook', 'url': 'https://storybook.company.dev'},
                    {'id': 'link_2_2', 'name': 'Design Tokens', 'url': 'https://github.com/company/design-tokens'}
                ])
            },
            {
                'milestone_id': f'mile_{session_id}_3',
                'session_id': session_id,
                'milestone_number': 3,
                'milestone_name': 'Backend API Development',
                'description': 'REST API endpoints, database optimization, authentication system',
                'completed': False,
                'due_date': (datetime.now() + timedelta(days=20)).isoformat(),
                'estimated_hours': 100.0,
                'actual_hours': 0.0,
                'milestone_order': 3,
                'depends_on_milestone_id': f'mile_{session_id}_1',
                'blocked': False,
                'documents': json.dumps([
                    {'id': 'doc_3_1', 'name': 'API Specification', 'url': 'https://swagger.company.dev/api-v2', 'type': 'document'},
                    {'id': 'doc_3_2', 'name': 'Database Schema', 'url': 'internal://docs/db-schema', 'type': 'internal'}
                ]),
                'links': json.dumps([
                    {'id': 'link_3_1', 'name': 'API Docs', 'url': 'https://api-docs.company.dev'}
                ])
            },
            {
                'milestone_id': f'mile_{session_id}_4',
                'session_id': session_id,
                'milestone_number': 4,
                'milestone_name': 'Integration & Testing',
                'description': 'Connect frontend and backend, write tests, QA testing, bug fixes',
                'completed': False,
                'due_date': (datetime.now() + timedelta(days=35)).isoformat(),
                'estimated_hours': 60.0,
                'actual_hours': 0.0,
                'milestone_order': 4,
                'depends_on_milestone_id': f'mile_{session_id}_2',
                'blocked': True,
                'blocker_reason': 'Waiting for API endpoints to be deployed to staging',
                'blocked_since': datetime.now().isoformat(),
                'documents': json.dumps([
                    {'id': 'doc_4_1', 'name': 'Test Plan', 'url': 'internal://docs/test-plan', 'type': 'internal'}
                ]),
                'links': json.dumps([])
            },
            {
                'milestone_id': f'mile_{session_id}_5',
                'session_id': session_id,
                'milestone_number': 5,
                'milestone_name': 'Deployment & Launch',
                'description': 'Production deployment, monitoring setup, launch announcement',
                'completed': False,
                'due_date': (datetime.now() + timedelta(days=45)).isoformat(),
                'estimated_hours': 40.0,
                'actual_hours': 0.0,
                'milestone_order': 5,
                'depends_on_milestone_id': f'mile_{session_id}_4',
                'blocked': False,
                'documents': json.dumps([]),
                'links': json.dumps([
                    {'id': 'link_5_1', 'name': 'Production Server', 'url': 'https://shop.company.com'}
                ])
            }
        ]
        
        for milestone in milestones:
            # Ensure all optional fields are present
            milestone_insert = {
                'milestone_id': milestone['milestone_id'],
                'session_id': milestone['session_id'],
                'milestone_number': milestone['milestone_number'],
                'milestone_name': milestone['milestone_name'],
                'description': milestone['description'],
                'completed': milestone['completed'],
                'completed_at': milestone.get('completed_at'),
                'due_date': milestone.get('due_date'),
                'estimated_hours': milestone.get('estimated_hours', 0),
                'actual_hours': milestone.get('actual_hours', 0),
                'milestone_order': milestone['milestone_order'],
                'depends_on_milestone_id': milestone.get('depends_on_milestone_id'),
                'blocked': milestone.get('blocked', False),
                'blocker_reason': milestone.get('blocker_reason'),
                'blocked_since': milestone.get('blocked_since'),
                'documents': milestone.get('documents', '[]'),
                'links': milestone.get('links', '[]')
            }
            
            cursor.execute("""
                INSERT INTO synergy_sessions.milestones 
                (milestone_id, session_id, milestone_number, milestone_name, description, 
                 completed, completed_at, due_date, estimated_hours, actual_hours, milestone_order,
                 depends_on_milestone_id, blocked, blocker_reason, blocked_since,
                 documents, links, created_at, updated_at)
                VALUES (%(milestone_id)s, %(session_id)s, %(milestone_number)s, %(milestone_name)s,
                        %(description)s, %(completed)s, %(completed_at)s, %(due_date)s,
                        %(estimated_hours)s, %(actual_hours)s, %(milestone_order)s,
                        %(depends_on_milestone_id)s, %(blocked)s, %(blocker_reason)s,
                        %(blocked_since)s, %(documents)s, %(links)s, NOW(), NOW())
            """, milestone_insert)
            
            status_icon = '✅' if milestone['completed'] else ('🚧' if milestone['blocked'] else '⏳')
            print(f"   {status_icon} M{milestone['milestone_number']}: {milestone['milestone_name']}")
            if milestone['depends_on_milestone_id']:
                print(f"      ⛓️  Depends on M{milestone['milestone_number']-1}")
            if milestone.get('documents'):
                doc_count = len(json.loads(milestone['documents']))
                print(f"      📄 {doc_count} milestone documents")
            if milestone.get('links'):
                link_count = len(json.loads(milestone['links']))
                print(f"      🔗 {link_count} milestone links")
        
        # ===================================================================
        # STEP 3: Create Tasks for Each Milestone
        # ===================================================================
        print("\n[3/5] Creating Tasks...")
        
        tasks_data = [
            # Milestone 1 Tasks (Completed)
            {'milestone_id': f'mile_{session_id}_1', 'task_id': f'task_{session_id}_1_1', 'task_order': 1, 'task': 'Conduct user interviews', 'completed': True},
            {'milestone_id': f'mile_{session_id}_1', 'task_id': f'task_{session_id}_1_2', 'task_order': 2, 'task': 'Create wireframes', 'completed': True},
            {'milestone_id': f'mile_{session_id}_1', 'task_id': f'task_{session_id}_1_3', 'task_order': 3, 'task': 'Design system documentation', 'completed': True},
            
            # Milestone 2 Tasks (In Progress)
            {'milestone_id': f'mile_{session_id}_2', 'task_id': f'task_{session_id}_2_1', 'task_order': 1, 'task': 'Set up React project structure', 'completed': True},
            {'milestone_id': f'mile_{session_id}_2', 'task_id': f'task_{session_id}_2_2', 'task_order': 2, 'task': 'Build component library', 'completed': False},
            {'milestone_id': f'mile_{session_id}_2', 'task_id': f'task_{session_id}_2_3', 'task_order': 3, 'task': 'Implement responsive layouts', 'completed': False},
            {'milestone_id': f'mile_{session_id}_2', 'task_id': f'task_{session_id}_2_4', 'task_order': 4, 'task': 'Add accessibility features', 'completed': False},
            
            # Milestone 3 Tasks (Not Started)
            {'milestone_id': f'mile_{session_id}_3', 'task_id': f'task_{session_id}_3_1', 'task_order': 1, 'task': 'Design database schema', 'completed': False},
            {'milestone_id': f'mile_{session_id}_3', 'task_id': f'task_{session_id}_3_2', 'task_order': 2, 'task': 'Build REST API endpoints', 'completed': False},
            {'milestone_id': f'mile_{session_id}_3', 'task_id': f'task_{session_id}_3_3', 'task_order': 3, 'task': 'Implement authentication', 'completed': False},
            
            # Milestone 4 Tasks (Blocked)
            {'milestone_id': f'mile_{session_id}_4', 'task_id': f'task_{session_id}_4_1', 'task_order': 1, 'task': 'Write integration tests', 'completed': False, 'blocked': True, 'blocker_reason': 'Waiting for API staging deployment'},
            {'milestone_id': f'mile_{session_id}_4', 'task_id': f'task_{session_id}_4_2', 'task_order': 2, 'task': 'QA testing round 1', 'completed': False, 'blocked': True, 'blocker_reason': 'Waiting for API staging deployment'},
            
            # Milestone 5 Tasks (Future)
            {'milestone_id': f'mile_{session_id}_5', 'task_id': f'task_{session_id}_5_1', 'task_order': 1, 'task': 'Set up production environment', 'completed': False},
            {'milestone_id': f'mile_{session_id}_5', 'task_id': f'task_{session_id}_5_2', 'task_order': 2, 'task': 'Deploy to production', 'completed': False},
        ]
        
        task_count = 0
        for task in tasks_data:
            cursor.execute("""
                INSERT INTO synergy_sessions.tasks
                (task_id, milestone_id, task_order, task, completed, 
                 blocked, blocker_reason, created_at, updated_at)
                VALUES (%(task_id)s, %(milestone_id)s, %(task_order)s, %(task)s,
                        %(completed)s, %(blocked)s, %(blocker_reason)s,
                        NOW(), NOW())
            """, {
                'task_id': task['task_id'],
                'milestone_id': task['milestone_id'],
                'task_order': task['task_order'],
                'task': task['task'],
                'completed': task['completed'],
                'blocked': task.get('blocked', False),
                'blocker_reason': task.get('blocker_reason')
            })
            task_count += 1
        
        print(f"   ✓ Created {task_count} tasks across 5 milestones")
        
        # ===================================================================
        # STEP 4: Create Subtasks (showing task hierarchy)
        # ===================================================================
        print("\n[4/5] Creating Subtasks...")
        
        subtasks_data = [
            # Subtasks for "Build component library"
            {'task_id': f'task_{session_id}_2_2', 'subtask_id': f'sub_{session_id}_2_2_1', 'subtask_order': 1, 'task': 'Button component', 'completed': True},
            {'task_id': f'task_{session_id}_2_2', 'subtask_id': f'sub_{session_id}_2_2_2', 'subtask_order': 2, 'task': 'Input component', 'completed': True},
            {'task_id': f'task_{session_id}_2_2', 'subtask_id': f'sub_{session_id}_2_2_3', 'subtask_order': 3, 'task': 'Card component', 'completed': False},
            {'task_id': f'task_{session_id}_2_2', 'subtask_id': f'sub_{session_id}_2_2_4', 'subtask_order': 4, 'task': 'Modal component', 'completed': False},
            
            # Subtasks for "Implement responsive layouts"
            {'task_id': f'task_{session_id}_2_3', 'subtask_id': f'sub_{session_id}_2_3_1', 'subtask_order': 1, 'task': 'Mobile breakpoints', 'completed': False},
            {'task_id': f'task_{session_id}_2_3', 'subtask_id': f'sub_{session_id}_2_3_2', 'subtask_order': 2, 'task': 'Tablet layouts', 'completed': False},
            {'task_id': f'task_{session_id}_2_3', 'subtask_id': f'sub_{session_id}_2_3_3', 'subtask_order': 3, 'task': 'Desktop optimization', 'completed': False},
            
            # Subtasks for "Build REST API endpoints"
            {'task_id': f'task_{session_id}_3_2', 'subtask_id': f'sub_{session_id}_3_2_1', 'subtask_order': 1, 'task': '/products endpoint', 'completed': False},
            {'task_id': f'task_{session_id}_3_2', 'subtask_id': f'sub_{session_id}_3_2_2', 'subtask_order': 2, 'task': '/cart endpoint', 'completed': False},
            {'task_id': f'task_{session_id}_3_2', 'subtask_id': f'sub_{session_id}_3_2_3', 'subtask_order': 3, 'task': '/checkout endpoint', 'completed': False},
        ]
        
        subtask_count = 0
        for subtask in subtasks_data:
            cursor.execute("""
                INSERT INTO synergy_sessions.subtasks
                (subtask_id, task_id, subtask_order, task, completed, created_at, updated_at)
                VALUES (%(subtask_id)s, %(task_id)s, %(subtask_order)s, %(task)s,
                        %(completed)s, NOW(), NOW())
            """, subtask)
            subtask_count += 1
        
        print(f"   ✓ Created {subtask_count} subtasks")
        
        # ===================================================================
        # STEP 5: Create Internal Documents
        # ===================================================================
        print("\n[5/5] Creating Internal Documents...")
        
        internal_docs = [
            {
                'doc_id': f'intdoc_{session_id}_1',
                'session_id': session_id,
                'title': 'Project Meeting Notes',
                'content': 'Weekly standup notes, decisions made, action items...',
                'linked_milestone_id': None,  # Session-level
                'doc_type': 'notes'
            },
            {
                'doc_id': f'intdoc_{session_id}_2',
                'session_id': session_id,
                'title': 'Design System Guidelines',
                'content': 'Color palette, typography, spacing rules, component usage...',
                'linked_milestone_id': f'mile_{session_id}_1',  # Linked to Milestone 1
                'doc_type': 'documentation'
            },
            {
                'doc_id': f'intdoc_{session_id}_3',
                'session_id': session_id,
                'title': 'Frontend Code Standards',
                'content': 'React best practices, folder structure, naming conventions...',
                'linked_milestone_id': f'mile_{session_id}_2',  # Linked to Milestone 2
                'doc_type': 'documentation'
            }
        ]
        
        for doc in internal_docs:
            cursor.execute("""
                INSERT INTO synergy_sessions.synergy_internal_docs
                (doc_id, session_id, title, content, linked_milestone_id, doc_type, created_at, updated_at)
                VALUES (%(doc_id)s, %(session_id)s, %(title)s, %(content)s,
                        %(linked_milestone_id)s, %(doc_type)s, NOW(), NOW())
            """, doc)
            
            level = "Session-level" if not doc['linked_milestone_id'] else f"Milestone {doc['linked_milestone_id'].split('_')[-1]}"
            print(f"   📄 {doc['title']} ({level})")
        
        # ===================================================================
        # COMMIT AND VERIFY
        # ===================================================================
        conn.commit()
        
        print("\n" + "=" * 80)
        print("VERIFICATION")
        print("=" * 80)
        
        # Count everything
        cursor.execute("SELECT COUNT(*) as count FROM synergy_sessions.synergy_sessions WHERE session_id = %s", (session_id,))
        session_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM synergy_sessions.milestones WHERE session_id = %s", (session_id,))
        milestone_count = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM synergy_sessions.tasks t
            JOIN synergy_sessions.milestones m ON t.milestone_id = m.milestone_id
            WHERE m.session_id = %s
        """, (session_id,))
        task_count = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM synergy_sessions.subtasks s
            JOIN synergy_sessions.tasks t ON s.task_id = t.task_id
            JOIN synergy_sessions.milestones m ON t.milestone_id = m.milestone_id
            WHERE m.session_id = %s
        """, (session_id,))
        subtask_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM synergy_sessions.synergy_internal_docs WHERE session_id = %s", (session_id,))
        doc_count = cursor.fetchone()['count']
        
        print(f"\n✅ Session ID: {session_id}")
        print(f"✅ Sessions: {session_count}")
        print(f"✅ Milestones: {milestone_count}")
        print(f"✅ Tasks: {task_count}")
        print(f"✅ Subtasks: {subtask_count}")
        print(f"✅ Internal Docs: {doc_count}")
        
        # Calculate progress
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE completed = TRUE) as completed_milestones,
                COUNT(*) as total_milestones
            FROM synergy_sessions.milestones
            WHERE session_id = %s
        """, (session_id,))
        progress_row = cursor.fetchone()
        m_completed, m_total = progress_row['completed_milestones'], progress_row['total_milestones']
        
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE t.completed = TRUE) as completed_tasks,
                COUNT(*) as total_tasks
            FROM synergy_sessions.tasks t
            JOIN synergy_sessions.milestones m ON t.milestone_id = m.milestone_id
            WHERE m.session_id = %s
        """, (session_id,))
        task_progress_row = cursor.fetchone()
        t_completed, t_total = task_progress_row['completed_tasks'], task_progress_row['total_tasks']
        
        print(f"\n📊 Progress:")
        print(f"   Milestones: {m_completed}/{m_total} ({int(m_completed/m_total*100)}%)")
        print(f"   Tasks: {t_completed}/{t_total} ({int(t_completed/t_total*100)}%)")
        
        print("\n" + "=" * 80)
        print("SUCCESS! Comprehensive Synergy example created.")
        print("=" * 80)
        print(f"\nTo view in UI, navigate to: http://localhost:5001/ui")
        print(f"Session will appear in 'In Progress' column")
        print("\n")
        
        return session_id
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_comprehensive_example()
