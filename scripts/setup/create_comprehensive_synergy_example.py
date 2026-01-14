"""
Create Comprehensive Synergy Card Example
Shows all available features and sections
"""
from shared.database_utils import convert_sql_placeholders

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import sqlite3
from datetime import datetime, timedelta
import json

def get_db_path():
    """Get the correct database path"""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, 'data', 'synergy_sessions.db')

def create_comprehensive_example():
    """Create a comprehensive example synergy card with all features"""
    
    db_path = get_db_path()
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the comprehensive example session
    session_id = 'sess_comprehensive_example_2025'
    title = 'Complete Project Management Example'
    description = '''This is a **comprehensive example** showing all Synergy Card features:

- Multiple document types (internal docs and external links)
- Next steps with subtasks and sub-checklists
- Checklist items with nested subtasks
- Links to external resources
- Tags and metadata
- Activity log entries
- Assigned agents
- Due dates and priorities

*Use this as a reference for how to structure complex projects!*'''

    # Create main session
    now = datetime.now().isoformat()
    due_date = (datetime.now() + timedelta(days=14)).isoformat()
    
    cursor.execute("""
        INSERT OR REPLACE INTO synergy_sessions (
            session_id, title, description, priority, status,
            kanban_column, last_active, created_at, due_date, 
            tags, assigned_agents
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        title,
        description,
        'high',
        'active',
        'in_progress',
        now,
        now,
        due_date,
        json.dumps(['example', 'demo', 'comprehensive', 'reference', 'tutorial']),
        json.dumps(['Primary AI Agent', 'Secondary AI Agent', 'Research Agent'])
    ))
    
    print(f"Created synergy session: {session_id}")
    
    # Create next steps with sub-checklists
    next_steps = [
        {
            "description": "Complete project requirements documentation",
            "completed": True,
            "due_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "priority": "high",
            "assigned_to": "Primary AI Agent",
            "sub_checklist": [
                {"task": "Define functional requirements", "completed": True},
                {"task": "Define technical specifications", "completed": True},
                {"task": "Create wireframes and mockups", "completed": True},
                {"task": "Get stakeholder approval", "completed": True}
            ]
        },
        {
            "description": "Set up development environment and infrastructure",
            "completed": True,
            "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "priority": "high",
            "assigned_to": "Secondary AI Agent",
            "sub_checklist": [
                {"task": "Configure local development setup", "completed": True},
                {"task": "Set up staging environment", "completed": True},
                {"task": "Configure CI/CD pipeline", "completed": True}
            ]
        },
        {
            "description": "Implement core backend API endpoints",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "priority": "high",
            "assigned_to": "Primary AI Agent",
            "sub_checklist": [
                {"task": "Design database schema", "completed": True},
                {"task": "Create authentication system", "completed": True},
                {"task": "Build user management API", "completed": False},
                {"task": "Implement data validation layer", "completed": False},
                {"task": "Write unit tests for endpoints", "completed": False}
            ]
        },
        {
            "description": "Design and implement frontend UI components",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "priority": "medium",
            "assigned_to": "Research Agent",
            "sub_checklist": [
                {"task": "Create component library", "completed": False},
                {"task": "Build dashboard interface", "completed": False},
                {"task": "Implement responsive design", "completed": False},
                {"task": "Add accessibility features", "completed": False}
            ]
        },
        {
            "description": "Integration testing and quality assurance",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=8)).isoformat(),
            "priority": "high",
            "assigned_to": "Secondary AI Agent",
            "sub_checklist": [
                {"task": "Write integration test suite", "completed": False},
                {"task": "Perform security audit", "completed": False},
                {"task": "Load testing and optimization", "completed": False},
                {"task": "User acceptance testing", "completed": False}
            ]
        },
        {
            "description": "Documentation and deployment preparation",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=12)).isoformat(),
            "priority": "medium",
            "assigned_to": "Primary AI Agent",
            "sub_checklist": [
                {"task": "Write API documentation", "completed": False},
                {"task": "Create user guides", "completed": False},
                {"task": "Prepare deployment scripts", "completed": False},
                {"task": "Set up monitoring and alerts", "completed": False}
            ]
        },
        {
            "description": "Production deployment and monitoring",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "priority": "critical",
            "assigned_to": "All Agents",
            "sub_checklist": [
                {"task": "Deploy to production", "completed": False},
                {"task": "Monitor initial performance", "completed": False},
                {"task": "Gather user feedback", "completed": False}
            ]
        },
        {
            "description": "Post-launch optimization and support",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=21)).isoformat(),
            "priority": "low",
            "assigned_to": "Research Agent",
            "sub_checklist": [
                {"task": "Analyze usage metrics", "completed": False},
                {"task": "Address user feedback", "completed": False},
                {"task": "Plan feature enhancements", "completed": False}
            ]
        }
    ]
    
    cursor.execute("""
        UPDATE synergy_sessions 
        SET next_steps = ?
        WHERE session_id = ?
    """, (json.dumps(next_steps), session_id))
    
    print(f"Added {len(next_steps)} next steps with sub-checklists")
    
    # Create checklist items with subtasks
    checklist = [
        {
            "item": "Code review completed",
            "completed": True,
            "subtasks": [
                {"task": "Backend code reviewed", "completed": True},
                {"task": "Frontend code reviewed", "completed": True},
                {"task": "Security review completed", "completed": True}
            ]
        },
        {
            "item": "All tests passing",
            "completed": True,
            "subtasks": [
                {"task": "Unit tests: 245/245 passed", "completed": True},
                {"task": "Integration tests: 67/67 passed", "completed": True},
                {"task": "E2E tests: 23/23 passed", "completed": True}
            ]
        },
        {
            "item": "Documentation up to date",
            "completed": False,
            "subtasks": [
                {"task": "API documentation complete", "completed": True},
                {"task": "User guide updated", "completed": False},
                {"task": "Installation guide verified", "completed": False}
            ]
        },
        {
            "item": "Performance benchmarks met",
            "completed": False,
            "subtasks": [
                {"task": "API response time < 200ms", "completed": True},
                {"task": "Page load time < 2s", "completed": False},
                {"task": "Database queries optimized", "completed": False}
            ]
        },
        {
            "item": "Security requirements satisfied",
            "completed": False,
            "subtasks": [
                {"task": "Authentication implemented", "completed": True},
                {"task": "Authorization rules defined", "completed": True},
                {"task": "Data encryption enabled", "completed": False},
                {"task": "Penetration testing completed", "completed": False}
            ]
        }
    ]
    
    cursor.execute("""
        UPDATE synergy_sessions 
        SET checklist = ?
        WHERE session_id = ?
    """, (json.dumps(checklist), session_id))
    
    print(f"Added {len(checklist)} checklist items with subtasks")
    
    # Create links to external resources
    links = [
        {
            "title": "Project Requirements Document",
            "url": "https://docs.google.com/document/d/example123",
            "type": "google_doc",
            "description": "Complete requirements and specifications"
        },
        {
            "title": "Design Mockups",
            "url": "https://figma.com/file/example456",
            "type": "figma",
            "description": "UI/UX designs and prototypes"
        },
        {
            "title": "Project Timeline",
            "url": "https://sheets.google.com/spreadsheets/d/example789",
            "type": "google_sheet",
            "description": "Detailed project schedule"
        },
        {
            "title": "GitHub Repository",
            "url": "https://github.com/example/project",
            "type": "github",
            "description": "Source code repository"
        },
        {
            "title": "API Documentation",
            "url": "https://api.example.com/docs",
            "type": "documentation",
            "description": "Complete API reference"
        }
    ]
    
    cursor.execute("""
        UPDATE synergy_sessions 
        SET links = ?
        WHERE session_id = ?
    """, (json.dumps(links), session_id))
    
    print(f"Added {len(links)} external links")
    
    # Create activity log
    activity_log = [
        {
            "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
            "description": "Session created",
            "type": "creation",
            "user": "Primary AI Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=6)).isoformat(),
            "description": "Requirements document attached",
            "type": "document_added",
            "user": "Primary AI Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "description": "Design mockups linked",
            "type": "link_added",
            "user": "Research Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=4)).isoformat(),
            "description": "Development environment setup completed",
            "type": "step_completed",
            "user": "Secondary AI Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
            "description": "Backend API implementation started",
            "type": "step_started",
            "user": "Primary AI Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "description": "Authentication system completed",
            "type": "milestone",
            "user": "Primary AI Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "description": "Unit tests added - 245 tests passing",
            "type": "quality",
            "user": "Secondary AI Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=12)).isoformat(),
            "description": "Frontend component library created",
            "type": "progress",
            "user": "Research Agent"
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
            "description": "Code review completed - approved",
            "type": "review",
            "user": "All Agents"
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "description": "Integration testing in progress",
            "type": "progress",
            "user": "Secondary AI Agent"
        }
    ]
    
    cursor.execute("""
        UPDATE synergy_sessions 
        SET recent_activity = ?
        WHERE session_id = ?
    """, (json.dumps(activity_log), session_id))
    
    print(f"Added {len(activity_log)} activity log entries")
    
    # Create internal documents
    internal_docs = [
        {
            "title": "Technical Architecture Document",
            "doc_type": "richtext",
            "content": "<h1>System Architecture Overview</h1><p>This document outlines the complete technical architecture...</p>",
            "description": "Complete system architecture and design decisions"
        },
        {
            "title": "API Endpoints Specification",
            "doc_type": "spreadsheet",
            "content_json": [
                ["Endpoint", "Method", "Description", "Status"],
                ["/api/users", "GET", "List all users", "Complete"],
                ["/api/users/{id}", "GET", "Get user details", "Complete"],
                ["/api/users", "POST", "Create new user", "In Progress"],
                ["/api/auth/login", "POST", "User login", "Complete"],
                ["/api/auth/logout", "POST", "User logout", "Complete"]
            ],
            "description": "Complete list of API endpoints with specifications"
        },
        {
            "title": "Meeting Notes - Sprint Planning",
            "doc_type": "richtext",
            "content": "<h2>Sprint Planning Meeting</h2><p><strong>Date:</strong> Last week</p><p><strong>Attendees:</strong> All team members</p><h3>Key Decisions:</h3><ul><li>Focus on backend completion</li><li>Parallel frontend development</li><li>Weekly code reviews</li></ul>",
            "description": "Notes from sprint planning session"
        }
    ]
    
    for doc in internal_docs:
        doc_id = f"doc_{session_id}_{doc['title'].lower().replace(' ', '_')}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO synergy_internal_docs (
                doc_id, session_id, title, content, content_json, 
                format, doc_type, created_by, created_at, updated_at, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            session_id,
            doc['title'],
            doc.get('content', ''),
            json.dumps(doc.get('content_json', [])) if 'content_json' in doc else None,
            'html',
            doc['doc_type'],
            'AI Agent',
            now,
            now,
            1
        ))
    
    print(f"Created {len(internal_docs)} internal documents")
    
    conn.commit()
    conn.close()
    
    print(f"\n SUCCESS! Comprehensive example synergy card created!")
    print(f"\nSession ID: {session_id}")
    print(f"Title: {title}")
    print(f"\nFeatures included:")
    print(f"  - {len(next_steps)} next steps with sub-checklists")
    print(f"  - {len(checklist)} checklist items with subtasks")
    print(f"  - {len(links)} external resource links")
    print(f"  - {len(activity_log)} activity log entries")
    print(f"  - {len(internal_docs)} internal documents")
    print(f"  - Tags, priorities, due dates")
    print(f"  - Assigned agents")
    print(f"  - Rich markdown description")
    print(f"\nRefresh your Synergy board to see it!")

if __name__ == "__main__":
    create_comprehensive_example()
