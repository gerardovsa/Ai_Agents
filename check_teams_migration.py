#!/usr/bin/env python3
"""Check if migration 038 (teams table) exists"""

from AI_infrastructure.shared.database_utils import execute_query

try:
    result = execute_query(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'ai_infrastructure' AND table_name = 'teams'",
        fetch_mode='one'
    )
    
    if result:
        print('✅ Teams table EXISTS - Migration 038 has been applied')
        
        # Check for columns
        cols = execute_query(
            """SELECT column_name FROM information_schema.columns 
               WHERE table_schema = 'ai_infrastructure' AND table_name = 'teams' 
               ORDER BY ordinal_position""",
            fetch_mode='all'
        )
        col_names = [c[0] if isinstance(c, tuple) else c.get('column_name', c) for c in cols]
        print(f'Columns found: {col_names}')
        
        # Check team_id on threads
        thread_team_id = execute_query(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = 'sessions' AND table_name = 'threads' AND column_name = 'team_id'",
            fetch_mode='one'
        )
        if thread_team_id:
            print('✅ team_id column EXISTS on sessions.threads')
        else:
            print('❌ team_id column MISSING on sessions.threads')
            
    else:
        print('❌ Teams table DOES NOT exist - Migration 038 NOT applied')
        
except Exception as e:
    print(f'Error checking database: {e}')
    import traceback
    traceback.print_exc()
