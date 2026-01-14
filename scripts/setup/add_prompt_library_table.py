"""
Add prompt_library table to ai_infrastructure.db
from shared.database_utils import convert_sql_placeholders

This migration adds support for the prompt library feature with:
- User-specific prompts
- Workspace-level sharing
- Quick actions vs full prompts
- Category organization
- Search and usage tracking
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def create_prompt_library_table():
    """Create the prompt_library table"""
    
    # Use correct database path
    db_path = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'
    
    print(f"Connecting to database: {db_path}")
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Create prompt_library table
        print("\nCreating prompt_library table...")
        sql, params = convert_sql_placeholders("""
            CREATE TABLE IF NOT EXISTS prompt_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workspace_id INTEGER,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(50) NOT NULL,
                type VARCHAR(20) NOT NULL DEFAULT 'quick_action',
                description TEXT,
                prompt_text TEXT NOT NULL,
                tags TEXT,
                visibility VARCHAR(20) NOT NULL DEFAULT 'private',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_user_id 
            ON prompt_library(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_workspace_id 
            ON prompt_library(workspace_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_category 
            ON prompt_library(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_visibility 
            ON prompt_library(visibility)
        """)
        
        # Insert default prompts for all users
        print("Inserting default prompts...")
        
        # Get all user IDs
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        default_prompts = [
            {
                'name': 'Expert Coder',
                'category': 'development',
                'type': 'quick_action',
                'description': 'Production-ready code with error handling and best practices',
                'prompt_text': '''CODING EXPERT MODE ACTIVATED:
- Write production-ready code with comprehensive error handling
- Include detailed docstrings and type hints
- Follow best practices and design patterns
- Consider edge cases and performance
- Add inline comments for complex logic''',
                'tags': 'coding,python,javascript,best-practices',
                'visibility': 'public'
            },
            {
                'name': 'Code Reviewer',
                'category': 'development',
                'type': 'quick_action',
                'description': 'Analyze code for bugs, security issues, and improvements',
                'prompt_text': '''CODE REVIEW MODE ACTIVATED:
- Systematically analyze code for bugs and security vulnerabilities
- Check for code smells and anti-patterns
- Suggest refactoring opportunities
- Verify error handling and edge cases
- Provide specific, actionable feedback''',
                'tags': 'review,security,quality,refactoring',
                'visibility': 'public'
            },
            {
                'name': 'Debugger',
                'category': 'development',
                'type': 'quick_action',
                'description': 'Step-by-step debugging and issue resolution',
                'prompt_text': '''DEBUG MODE ACTIVATED:
- Analyze the issue systematically step-by-step
- Check error messages, stack traces, and logs
- Verify data flow and state at each step
- Test hypotheses methodically
- Provide clear explanation of root cause and solution''',
                'tags': 'debug,troubleshooting,errors',
                'visibility': 'public'
            },
            {
                'name': 'SQL Expert',
                'category': 'data',
                'type': 'quick_action',
                'description': 'Optimized SQL queries with performance analysis',
                'prompt_text': '''SQL EXPERT MODE ACTIVATED:
- Write optimized, performant SQL queries
- Use proper indexing strategies
- Include query execution plans (EXPLAIN)
- Consider database-specific features
- Add comments explaining complex joins and subqueries''',
                'tags': 'sql,database,optimization,queries',
                'visibility': 'public'
            },
            {
                'name': 'Data Analyst',
                'category': 'data',
                'type': 'quick_action',
                'description': 'Data analysis with insights and visualizations',
                'prompt_text': '''DATA ANALYST MODE ACTIVATED:
- Analyze data patterns and trends
- Provide statistical insights
- Suggest appropriate visualizations
- Identify correlations and anomalies
- Present findings clearly with actionable recommendations''',
                'tags': 'data,analysis,statistics,insights',
                'visibility': 'public'
            },
            {
                'name': 'Concise',
                'category': 'style',
                'type': 'quick_action',
                'description': 'Short, direct answers without extra explanation',
                'prompt_text': '''CONCISE MODE ACTIVATED:
- Provide brief, direct answers
- Avoid lengthy explanations unless specifically requested
- Get straight to the point
- Use bullet points for clarity
- No unnecessary preamble or conclusions''',
                'tags': 'brief,short,quick,concise',
                'visibility': 'public'
            },
            {
                'name': 'Detailed Analysis',
                'category': 'analysis',
                'type': 'full_prompt',
                'description': 'Comprehensive in-depth analysis with data and evidence',
                'prompt_text': '''DETAILED ANALYSIS MODE ACTIVATED:
You are now in comprehensive analysis mode. Your responses should:

DEPTH:
- Provide in-depth, thorough analysis
- Break down complex topics into components
- Explore multiple perspectives and scenarios
- Consider edge cases and implications

EVIDENCE:
- Use data and evidence to support conclusions
- Reference specific examples
- Include relevant statistics or metrics
- Cite sources when applicable

STRUCTURE:
- Use clear headings and sections
- Include visualizations or tables where helpful
- Provide executive summary for long analyses
- Add actionable recommendations

QUALITY:
- Verify accuracy of information
- Acknowledge uncertainties
- Provide balanced viewpoints
- Connect insights to broader context''',
                'tags': 'analysis,detailed,comprehensive,thorough',
                'visibility': 'public'
            },
            {
                'name': 'System Architect',
                'category': 'development',
                'type': 'full_prompt',
                'description': 'High-level system design and architecture expertise',
                'prompt_text': '''SYSTEM ARCHITECT MODE ACTIVATED:
You are a senior system architect with 15+ years of experience designing scalable, distributed systems.

FOCUS AREAS:
- System architecture and design patterns
- Scalability and performance optimization
- Security and reliability considerations
- Technology stack recommendations
- Trade-off analysis for architectural decisions

DELIVERABLES:
- High-level system diagrams (ASCII or Mermaid)
- Component interaction flows
- Data flow models
- Scalability strategies
- Best practices and patterns
- Security considerations
- Disaster recovery plans

APPROACH:
- Start with requirements analysis
- Consider non-functional requirements (scalability, security, performance)
- Propose multiple architectural options
- Analyze trade-offs explicitly
- Provide concrete recommendations with justification
- Include migration strategies for existing systems''',
                'tags': 'architecture,design,scalability,systems,patterns',
                'visibility': 'public'
            }
        ]
        
        # Insert default prompts for each user
        for user_id in user_ids:
            for prompt in default_prompts:
                cursor.execute("""
                    INSERT INTO prompt_library 
                    (user_id, name, category, type, description, prompt_text, tags, visibility)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    prompt['name'],
                    prompt['category'],
                    prompt['type'],
                    prompt['description'],
                    prompt['prompt_text'],
                    prompt['tags'],
                    prompt['visibility']
                ))

        cursor.execute(sql, params)
        
        conn.commit()
        
        # Verify table creation
        sql, params = convert_sql_placeholders("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='prompt_library'
        """)
        
        if cursor.fetchone():
            print("\nSUCCESS: prompt_library table created!")
            
            # Show table info
            cursor.execute("PRAGMA table_info(prompt_library)")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Show prompt count
            cursor.execute("SELECT COUNT(*) FROM prompt_library")
            count = cursor.fetchone()[0]
            print(f"\nInserted {count} default prompts ({len(default_prompts)} prompts × {len(user_ids)} users)")
            
            # Show sample prompts
            cursor.execute("""
                SELECT name, category, type 
                FROM prompt_library 
                WHERE user_id = ? 
                ORDER BY category, name
            """, (user_ids[0] if user_ids else 1,))

        cursor.execute(sql, params)
            
            print("\nSample prompts for first user:")
            for row in cursor.fetchall():
                print(f"  - {row[0]} ({row[1]}/{row[2]})")
            
            return True
        else:
            print("ERROR: Table creation verification failed")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("PROMPT LIBRARY TABLE MIGRATION")
    print("=" * 60)
    
    success = create_prompt_library_table()
    
    if success:
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("MIGRATION FAILED")
        print("=" * 60)
        sys.exit(1)
