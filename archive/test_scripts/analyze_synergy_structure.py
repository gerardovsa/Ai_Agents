"""
Analyze Synergy Session Card Structure
"""

import sqlite3
import json
from pathlib import Path

# Connect to synergy database
db_path = Path('data/synergy_sessions.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("\n" + "="*80)
print("SYNERGY SESSION CARD STRUCTURE ANALYSIS")
print("="*80)

# Get table structure
cursor.execute('PRAGMA table_info(synergy_sessions)')
columns = cursor.fetchall()

print("\n1. DATABASE SCHEMA:")
print("-"*80)
for i, col in enumerate(columns, 1):
    col_name = col[1]
    col_type = col[2]
    nullable = "NOT NULL" if col[3] else "nullable"
    default = f"DEFAULT {col[4]}" if col[4] else ""
    print(f"{i:2}. {col_name:30} {col_type:10} {nullable:10} {default}")

# Get sample session
cursor.execute('SELECT * FROM synergy_sessions ORDER BY created_at DESC LIMIT 1')
row = cursor.fetchone()

if row:
    print("\n2. SAMPLE SESSION CARD:")
    print("-"*80)
    col_names = [col[0] for col in cursor.description]
    
    for col_name, value in zip(col_names, row):
        # Format value nicely
        if value and col_name in ['platforms_involved', 'tags', 'documents', 'links', 
                                   'thread_ids', 'assigned_agents', 'checklist']:
            try:
                parsed = json.loads(value)
                value_str = json.dumps(parsed, indent=2)[:100] + "..." if len(str(parsed)) > 100 else json.dumps(parsed, indent=2)
            except:
                value_str = str(value)[:100]
        else:
            value_str = str(value)[:100] if value else "NULL"
        
        print(f"{col_name:30} = {value_str}")

# Get statistics
cursor.execute('SELECT COUNT(*) FROM synergy_sessions')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM synergy_sessions WHERE status = "active"')
active = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM synergy_sessions WHERE status = "completed"')
completed = cursor.fetchone()[0]

print("\n3. DATABASE STATISTICS:")
print("-"*80)
print(f"Total sessions:      {total}")
print(f"Active sessions:     {active}")
print(f"Completed sessions:  {completed}")

# Get column usage
cursor.execute('SELECT kanban_column, COUNT(*) FROM synergy_sessions GROUP BY kanban_column')
columns_data = cursor.fetchall()

print("\n4. KANBAN COLUMNS:")
print("-"*80)
for col, count in columns_data:
    print(f"{col if col else 'NULL':20} = {count} sessions")

# Analyze AI-related fields
print("\n5. AI AGENT INTEGRATION:")
print("-"*80)

cursor.execute('SELECT COUNT(*) FROM synergy_sessions WHERE assigned_agents IS NOT NULL AND assigned_agents != "[]"')
with_agents = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM synergy_sessions WHERE thread_ids IS NOT NULL AND thread_ids != "[]"')
with_threads = cursor.fetchone()[0]

print(f"Sessions with assigned agents:  {with_agents}")
print(f"Sessions with conversation threads: {with_threads}")

# Get a session with AI data
cursor.execute('''
    SELECT session_id, title, assigned_agents, thread_ids, platforms_involved 
    FROM synergy_sessions 
    WHERE (assigned_agents IS NOT NULL AND assigned_agents != "[]") 
       OR (thread_ids IS NOT NULL AND thread_ids != "[]")
    LIMIT 1
''')
ai_session = cursor.fetchone()

if ai_session:
    print("\n6. AI-ENABLED SESSION EXAMPLE:")
    print("-"*80)
    print(f"Session ID:       {ai_session[0]}")
    print(f"Title:            {ai_session[1]}")
    print(f"Assigned Agents:  {ai_session[2]}")
    print(f"Thread IDs:       {ai_session[3]}")
    print(f"Platforms:        {ai_session[4]}")

print("\n7. KEY FEATURES FOR LONG-RUNNING AGENTS:")
print("-"*80)
print("✅ thread_ids          - Links to conversation threads (multi-round context)")
print("✅ assigned_agents     - Which AI agents are working on this")
print("✅ platforms_involved  - Which tools/platforms are used")
print("✅ next_steps          - AI-generated action items")
print("✅ recent_activity     - Activity log (tool executions, decisions)")
print("✅ documents           - Links to created documents/artifacts")
print("✅ status              - Workflow state (active/blocked/completed)")
print("✅ checklist           - Sub-tasks with completion tracking")

print("\n8. HOW SYNERGY CARDS ENABLE 30+ ROUNDS:")
print("-"*80)
print("""
Strategy 1: EXTERNAL WORKING MEMORY
- Session card = Working memory outside conversation
- Stores: documents, links, action items, state
- AI reads/updates card instead of keeping in conversation
- Result: Conversation stays small (decisions only)

Strategy 2: MULTI-THREADED CONTEXT
- thread_ids links to multiple conversation threads
- Each thread handles 10-15 rounds
- Session card coordinates between threads
- Result: 3 threads × 15 rounds = 45 total rounds

Strategy 3: STATEFUL WORKFLOW
- Kanban column = Current workflow state
- Recent_activity = Audit log of actions taken
- Checklist = Sub-tasks with completion status
- Result: AI knows where it is without re-reading history

Strategy 4: PLATFORM COORDINATION
- platforms_involved tracks which tools used
- Documents links to created artifacts
- Result: AI knows what tools were used without seeing results

Strategy 5: MULTI-AGENT COLLABORATION
- assigned_agents tracks which AIs are working
- Different agents handle different aspects
- Each agent has its own conversation thread
- Result: Distribute work across multiple contexts
""")

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("\nRecommendation: Use Synergy cards as external working memory")
print("for long-running agent workflows (30+ rounds)")
print()
