"""
Load Agent Specialization Prompts from .github/prompts/ into Database

This script scans .github/prompts/ for .prompt.md files and loads them
into the prompt_library table so they appear in the UI and can be selected.
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from pathlib import Path
from datetime import datetime
from shared.database_utils import get_database_connection

# Prompt file to database mapping
PROMPT_MAPPINGS = {
    'Debugging Detective.prompt.md': {
        'name': 'Debugging Detective',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Systematically hunt down bugs using forensic analysis, trace error propagation, and suggest defensive coding patterns.',
        'icon': 'fa-bug',
        'tags': 'debugging, forensics, error-tracing, root-cause-analysis'
    },
    'Code Archeology.prompt.md': {
        'name': 'Code Archeologist',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Excavate legacy codebases, understand historical context, and document undocumented systems.',
        'icon': 'fa-search',
        'tags': 'legacy, documentation, code-analysis, reverse-engineering'
    },
    'Documentation Generator.prompt.md': {
        'name': 'Documentation Generator',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Generate comprehensive documentation for code, APIs, and systems with proper structure and examples.',
        'icon': 'fa-book',
        'tags': 'documentation, api-docs, comments, readme'
    },
    'Feature Flag Engineer.prompt.md': {
        'name': 'Feature Flag Engineer',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Design and implement feature flag systems for controlled rollouts and A/B testing.',
        'icon': 'fa-flag',
        'tags': 'feature-flags, rollout, deployment, testing'
    },
    'Performance Optimization.prompt.md': {
        'name': 'Performance Optimizer',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Analyze performance bottlenecks, optimize algorithms, and improve system efficiency.',
        'icon': 'fa-tachometer-alt',
        'tags': 'performance, optimization, profiling, efficiency'
    },
    'Refactoring Strategist.prompt.md': {
        'name': 'Refactoring Strategist',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Plan and execute code refactoring with minimal risk, improve maintainability and design patterns.',
        'icon': 'fa-tools',
        'tags': 'refactoring, code-quality, design-patterns, clean-code'
    },
    'System Integration Architect.prompt.md': {
        'name': 'System Integration Architect',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Design integration strategies between systems, APIs, and services with proper error handling.',
        'icon': 'fa-plug',
        'tags': 'integration, api, services, architecture'
    },
    'System_Architexture.prompt.md': {
        'name': 'System Architect',
        'type': 'full_prompt',
        'category': 'development',
        'visibility': 'public',
        'description': 'Design scalable system architectures, choose appropriate technologies, and plan infrastructure.',
        'icon': 'fa-sitemap',
        'tags': 'architecture, design, scalability, infrastructure'
    },
    'UI-UX Consistency Architect.prompt.md': {
        'name': 'UI/UX Consistency Architect',
        'type': 'full_prompt',
        'category': 'creative',
        'visibility': 'public',
        'description': 'Ensure UI/UX consistency across applications, design systems, and user experience patterns.',
        'icon': 'fa-palette',
        'tags': 'ui, ux, design-system, consistency, accessibility'
    }
}

def load_prompts():
    """Load all .prompt.md files into database"""
    
    prompts_dir = Path('.github/prompts')
    
    if not prompts_dir.exists():
        print(f"ERROR: {prompts_dir} not found!")
        return
    
    conn = get_database_connection('ai_infrastructure')
    cur = conn.cursor()
    
    print("\n=== LOADING AGENT SPECIALIZATION PROMPTS ===\n")
    
    # Get next available ID
    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM prompt_library")
    next_id = cur.fetchone()['next_id']
    
    loaded_count = 0
    skipped_count = 0
    
    for prompt_file in prompts_dir.glob('*.prompt.md'):
        filename = prompt_file.name
        
        if filename not in PROMPT_MAPPINGS:
            print(f"SKIP: {filename} (no mapping)")
            skipped_count += 1
            continue
        
        # Read prompt content
        prompt_text = prompt_file.read_text(encoding='utf-8')
        
        # Get metadata
        metadata = PROMPT_MAPPINGS[filename]
        
        # Check if already exists
        cur.execute("""
            SELECT id FROM prompt_library
            WHERE name = %s AND type = %s
            LIMIT 1
        """, (metadata['name'], metadata['type']))
        
        existing = cur.fetchone()
        
        if existing:
            # Update existing
            cur.execute("""
                UPDATE prompt_library
                SET prompt_text = %s,
                    description = %s,
                    category = %s,
                    visibility = %s,
                    tags = %s,
                    updated_at = %s
                WHERE id = %s
            """, (
                prompt_text,
                metadata['description'],
                metadata['category'],
                metadata['visibility'],
                metadata['tags'],
                datetime.now(),
                existing['id']
            ))
            print(f"✓ UPDATED: {metadata['name']} (ID: {existing['id']})")
        else:
            # Insert new with explicit ID
            cur.execute("""
                INSERT INTO prompt_library (
                    id, user_id, workspace_id, name, prompt_text, description,
                    category, type, visibility, tags,
                    created_at, updated_at
                ) VALUES (
                    %s, 1, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                next_id,
                metadata['name'],
                prompt_text,
                metadata['description'],
                metadata['category'],
                metadata['type'],
                metadata['visibility'],
                metadata['tags'],
                datetime.now(),
                datetime.now()
            ))
            print(f"✓ INSERTED: {metadata['name']} (ID: {next_id})")
            next_id += 1
        
        loaded_count += 1
    
    # Commit changes
    conn.commit()
    
    print(f"\n=== SUMMARY ===")
    print(f"Loaded: {loaded_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Total .prompt.md files: {len(list(prompts_dir.glob('*.prompt.md')))}")
    
    # Show all full_prompt entries
    print(f"\n=== FULL PROMPTS IN DATABASE ===\n")
    cur.execute("""
        SELECT id, name, category, visibility, created_at
        FROM prompt_library
        WHERE type = %s
        ORDER BY name
    """, ('full_prompt',))
    
    full_prompts = cur.fetchall()
    for prompt in full_prompts:
        print(f"  {prompt['id']:3d}. {prompt['name']} ({prompt['category']}, {prompt['visibility']})")
    
    print(f"\nTotal full_prompt entries: {len(full_prompts)}")
    
    conn.close()

if __name__ == '__main__':
    load_prompts()
