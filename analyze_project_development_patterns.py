"""
Analyze Project Development Patterns
Examines file names, types, and creation dates to identify development phases and modules
"""

import os
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import re

def categorize_file(file_path):
    """Categorize files based on path and name patterns"""
    path_lower = file_path.lower()
    name = os.path.basename(file_path).lower()
    
    # Module/Feature categories
    categories = {
        'Authentication & OAuth': [
            'auth', 'oauth', 'login', 'credential', 'token', 'microsoft365', 'google_auth'
        ],
        'AI Infrastructure': [
            'agent', 'anthropic', 'claude', 'openai', 'deepseek', 'model', 'prompt', 'llm'
        ],
        'Database & Storage': [
            'database', 'db_', 'sqlite', 'schema', 'migration', 'sessions'
        ],
        'API Integrations': [
            'gmail', 'google_docs', 'google_sheets', 'slack', 'stripe', 'github', 'notion'
        ],
        'UI & Frontend': [
            'ui/', 'html', 'css', 'javascript', 'tabulator', 'chart', 'business-ai-platform'
        ],
        'Tools & Registry': [
            'tools/', 'registry', 'tool_', 'implementations/', 'schemas/'
        ],
        'Thread Management': [
            'thread', 'conversation', 'message', 'chat'
        ],
        'Task & Sync': [
            'task', 'sync', 'universal', 'calendar', 'todoist'
        ],
        'Stock Management': [
            'stock', 'inventory', 'pricing', 'calculator'
        ],
        'Flask Backend': [
            'flask', 'routes/', 'api/', 'endpoint'
        ],
        'Testing & Scripts': [
            'test_', 'check_', 'setup_', 'analyze_', 'scripts/'
        ],
        'Documentation': [
            '.md', 'readme', 'documentation', 'changelog', 'notes'
        ],
        'Configuration': [
            'config', '.json', '.yaml', '.env', 'requirements.txt', 'package.json'
        ]
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in path_lower or keyword in name:
                return category
    
    return 'Other'

def extract_module_name(file_path):
    """Extract specific module/feature name from path"""
    path_parts = file_path.split(os.sep)
    
    # Check for specific module directories
    if 'modules' in path_parts:
        idx = path_parts.index('modules')
        if idx + 1 < len(path_parts):
            return path_parts[idx + 1]
    
    if 'routes' in path_parts:
        name = os.path.basename(file_path)
        if name.endswith('_routes.py'):
            return name.replace('_routes.py', '').replace('_', ' ').title()
    
    if 'tools' in path_parts and 'implementations' in path_parts:
        name = os.path.basename(file_path)
        if name.endswith('.py'):
            return name.replace('.py', '').replace('_', ' ').title() + ' Tools'
    
    # Extract from filename
    name = os.path.basename(file_path)
    if '_' in name:
        parts = name.split('_')
        if len(parts) > 1:
            return ' '.join(parts[:2]).title()
    
    return None

def analyze_project_development(base_path):
    """Analyze project development patterns"""
    
    print(f"\n{'='*80}")
    print("PROJECT DEVELOPMENT PATTERN ANALYSIS")
    print(f"{'='*80}\n")
    
    files_data = []
    category_stats = defaultdict(lambda: {'files': 0, 'dates': set(), 'modules': set()})
    module_timeline = defaultdict(lambda: defaultdict(int))
    daily_activity = defaultdict(lambda: defaultdict(int))
    
    # Scan all files
    print("Scanning files...")
    for root, dirs, files in os.walk(base_path):
        # Skip certain directories
        skip_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_path)
            
            try:
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                modified = datetime.fromtimestamp(stats.st_mtime)
                
                category = categorize_file(rel_path)
                module = extract_module_name(rel_path)
                ext = os.path.splitext(file)[1]
                
                files_data.append({
                    'path': rel_path,
                    'name': file,
                    'category': category,
                    'module': module,
                    'extension': ext,
                    'created': created,
                    'modified': modified,
                    'size': stats.st_size
                })
                
                # Update stats
                date_str = created.strftime('%Y-%m-%d')
                category_stats[category]['files'] += 1
                category_stats[category]['dates'].add(date_str)
                if module:
                    category_stats[category]['modules'].add(module)
                
                # Track module timeline
                if module:
                    module_timeline[module][date_str] += 1
                
                # Daily activity by category
                daily_activity[date_str][category] += 1
                
            except Exception as e:
                continue
    
    print(f"Analyzed {len(files_data)} files\n")
    
    # Sort by creation date
    files_data.sort(key=lambda x: x['created'])
    
    # Analysis Results
    print(f"\n{'='*80}")
    print("CATEGORY BREAKDOWN")
    print(f"{'='*80}\n")
    
    sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['files'], reverse=True)
    
    for category, stats in sorted_categories:
        print(f"📁 {category}")
        print(f"   Files: {stats['files']}")
        print(f"   Active Days: {len(stats['dates'])}")
        if stats['modules']:
            print(f"   Modules: {', '.join(sorted(stats['modules'])[:5])}")
        print()
    
    # Module Development Timeline
    print(f"\n{'='*80}")
    print("MODULE DEVELOPMENT TIMELINE")
    print(f"{'='*80}\n")
    
    # Find modules with significant development
    module_totals = {mod: sum(dates.values()) for mod, dates in module_timeline.items()}
    top_modules = sorted(module_totals.items(), key=lambda x: x[1], reverse=True)[:15]
    
    for module, total in top_modules:
        dates = module_timeline[module]
        date_list = sorted(dates.keys())
        first_date = date_list[0] if date_list else 'Unknown'
        last_date = date_list[-1] if date_list else 'Unknown'
        active_days = len(date_list)
        
        print(f"🔧 {module}")
        print(f"   Files: {total}")
        print(f"   First: {first_date}  →  Last: {last_date}")
        print(f"   Active Days: {active_days}")
        
        # Show work pattern
        if active_days > 1:
            pattern = []
            for date in date_list[:5]:  # Show first 5 days
                pattern.append(f"{date} ({dates[date]} files)")
            print(f"   Pattern: {', '.join(pattern)}")
        print()
    
    # Development Phases Analysis
    print(f"\n{'='*80}")
    print("DEVELOPMENT PHASES (BY DATE)")
    print(f"{'='*80}\n")
    
    # Group by date and find phases
    sorted_dates = sorted(daily_activity.keys())
    
    current_phase = None
    phase_start = None
    phases = []
    
    for date in sorted_dates:
        categories = daily_activity[date]
        top_category = max(categories, key=categories.get)
        file_count = sum(categories.values())
        
        # Detect phase changes (when primary focus shifts)
        if top_category != current_phase:
            if current_phase:
                phases.append({
                    'phase': current_phase,
                    'start': phase_start,
                    'end': sorted_dates[sorted_dates.index(date) - 1] if sorted_dates.index(date) > 0 else date,
                    'dates': [d for d in sorted_dates[sorted_dates.index(phase_start):sorted_dates.index(date)] if d in sorted_dates]
                })
            current_phase = top_category
            phase_start = date
    
    # Add last phase
    if current_phase:
        phases.append({
            'phase': current_phase,
            'start': phase_start,
            'end': sorted_dates[-1],
            'dates': [d for d in sorted_dates if d >= phase_start]
        })
    
    for i, phase in enumerate(phases, 1):
        duration = len(phase['dates'])
        print(f"Phase {i}: {phase['phase']}")
        print(f"   Duration: {phase['start']} → {phase['end']} ({duration} days)")
        
        # Show what was built
        phase_files = [f for f in files_data if f['created'].strftime('%Y-%m-%d') in phase['dates'] and f['category'] == phase['phase']]
        if phase_files:
            modules_in_phase = set(f['module'] for f in phase_files if f['module'])
            if modules_in_phase:
                print(f"   Modules: {', '.join(sorted(modules_in_phase)[:5])}")
        print()
    
    # File Type Analysis
    print(f"\n{'='*80}")
    print("FILE TYPE DISTRIBUTION")
    print(f"{'='*80}\n")
    
    ext_stats = defaultdict(int)
    for f in files_data:
        ext_stats[f['extension']] += 1
    
    sorted_exts = sorted(ext_stats.items(), key=lambda x: x[1], reverse=True)[:15]
    for ext, count in sorted_exts:
        ext_name = ext if ext else '(no extension)'
        print(f"   {ext_name:20} {count:>5} files")
    
    # Work Pattern Analysis
    print(f"\n{'='*80}")
    print("WORK PATTERN INSIGHTS")
    print(f"{'='*80}\n")
    
    # Find revisited modules
    revisited = {}
    for module, dates in module_timeline.items():
        date_list = sorted(dates.keys())
        if len(date_list) > 3:  # Module worked on multiple days
            # Check for gaps (revisiting)
            date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in date_list]
            gaps = []
            for i in range(1, len(date_objects)):
                gap = (date_objects[i] - date_objects[i-1]).days
                if gap > 3:  # More than 3 days gap
                    gaps.append(gap)
            
            if gaps:
                revisited[module] = {
                    'total_days': len(date_list),
                    'gaps': gaps,
                    'max_gap': max(gaps)
                }
    
    if revisited:
        print("📌 MODULES WITH MULTIPLE DEVELOPMENT SESSIONS:\n")
        sorted_revisited = sorted(revisited.items(), key=lambda x: x[1]['total_days'], reverse=True)
        
        for module, data in sorted_revisited[:10]:
            print(f"   {module}")
            print(f"      Active Days: {data['total_days']}")
            print(f"      Longest Gap: {data['max_gap']} days")
            print(f"      Total Gaps: {len(data['gaps'])}")
            print()
    
    # Save detailed JSON
    output = {
        'analysis_date': datetime.now().isoformat(),
        'total_files': len(files_data),
        'categories': {cat: {
            'file_count': stats['files'],
            'active_days': len(stats['dates']),
            'modules': sorted(stats['modules'])
        } for cat, stats in category_stats.items()},
        'top_modules': {mod: {
            'file_count': total,
            'dates': sorted(module_timeline[mod].keys())
        } for mod, total in top_modules},
        'development_phases': phases,
        'revisited_modules': revisited
    }
    
    output_file = 'project_development_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"✅ Analysis complete! Detailed data saved to: {output_file}")
    print(f"{'='*80}\n")
    
    return files_data, module_timeline, daily_activity

if __name__ == "__main__":
    # Analyze AI_agents project
    print("\n🔍 ANALYZING AI_AGENTS PROJECT...")
    ai_agents_path = r"c:\Users\gpoli\GIT\AI_agents"
    analyze_project_development(ai_agents_path)
    
    print("\n" + "="*80)
    print("Analysis complete! Check the output above for insights.")
    print("="*80)
