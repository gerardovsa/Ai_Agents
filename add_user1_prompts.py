"""Add prompts for user_id=1"""
import sqlite3
from datetime import datetime
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

prompts = [
    ('Expert Coder', 'development', 'quick_action', 'Production-ready code with error handling and best practices', 
     'You are an expert software developer. Write production-ready code with proper error handling, type hints, documentation, and following best practices.', 
     'coding,python,javascript,best-practices', 'public'),
    
    ('SQL Expert', 'data', 'full_prompt', 'Database query optimization expert', 
     'You are a database expert specializing in SQL optimization and complex query design. Provide efficient, well-structured queries.', 
     'sql,database,optimization,postgresql', 'public'),
    
    ('Debugger', 'development', 'quick_action', 'Debug and fix code issues', 
     'You are a debugging expert. Analyze code systematically to identify root causes and provide clear fixes.', 
     'debug,troubleshooting,errors,fixes', 'public'),
    
    ('Data Analyst', 'data', 'full_prompt', 'Data analysis and visualization expert', 
     'You are a data analyst skilled in statistical analysis, data visualization, and deriving insights from data.', 
     'data,analysis,statistics,visualization', 'public'),
    
    ('Code Reviewer', 'development', 'quick_action', 'Review code for best practices', 
     'Review this code for best practices, security issues, performance optimizations, and suggest improvements.', 
     'review,security,quality,refactoring', 'public'),
    
    ('Concise', 'analysis', 'quick_action', 'Get brief, concise responses', 
     'Provide a brief, concise answer without unnecessary details. Focus on the key points only.', 
     'concise,brief,short,summary', 'public'),
    
    ('Detailed Analysis', 'analysis', 'quick_action', 'Get comprehensive analysis', 
     'Provide a detailed, comprehensive analysis covering all aspects, including examples and edge cases.', 
     'detailed,comprehensive,thorough,examples', 'public'),
    
    ('System Architect', 'development', 'full_prompt', 'System design and architecture expert', 
     'You are a system architect specializing in scalable, distributed systems. Design robust, maintainable architectures.', 
     'architecture,design,scalability,systems', 'public')
]

now = datetime.now().isoformat()

for name, category, ptype, description, prompt_text, tags, visibility in prompts:
    cursor.execute('''
        INSERT INTO prompt_library 
        (user_id, name, category, type, description, prompt_text, tags, visibility, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (1, name, category, ptype, description, prompt_text, tags, visibility, now, now))

conn.commit()
print(f'✅ Added {len(prompts)} prompts for user_id=1')

# Verify
cursor.execute('SELECT COUNT(*) FROM prompt_library WHERE user_id = 1')
count = cursor.fetchone()[0]
print(f'✅ Total prompts for user_id=1: {count}')

conn.close()
