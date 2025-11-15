"""
Create detailed Gantt chart visualization for project development
Analyzes both AI_agents and G_Folder projects with granular module tracking
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import re

def categorize_file_granular(file_path, base_path):
    """More granular categorization based on actual file structure"""
    path_lower = file_path.lower()
    name = os.path.basename(file_path).lower()
    rel_path = os.path.relpath(file_path, base_path)
    parts = rel_path.split(os.sep)
    
    # Very specific categorization
    
    # UI Modules
    if 'ui' in parts and 'modules' in parts:
        try:
            module_idx = parts.index('modules') + 1
            if module_idx < len(parts):
                return f"UI Module: {parts[module_idx]}"
        except:
            pass
    
    # Flask Routes
    if 'routes' in parts and file_path.endswith('.py'):
        route_name = os.path.basename(file_path).replace('_routes.py', '').replace('_', ' ').title()
        return f"Flask Route: {route_name}"
    
    # Tools Implementation
    if 'tools' in parts and 'implementations' in parts and file_path.endswith('.py'):
        tool_name = os.path.basename(file_path).replace('.py', '').replace('_', ' ').title()
        return f"Tools: {tool_name}"
    
    # Tools Schemas
    if 'tools' in parts and 'schemas' in parts and file_path.endswith('.json'):
        schema_name = os.path.basename(file_path).replace('_tools.json', '').replace('_', ' ').title()
        return f"Tool Schema: {schema_name}"
    
    # Authentication
    if any(x in path_lower for x in ['auth', 'oauth', 'credential', 'login']):
        if 'microsoft' in path_lower or '365' in path_lower:
            return "Auth: Microsoft 365"
        elif 'google' in path_lower:
            return "Auth: Google Workspace"
        else:
            return "Auth: Core System"
    
    # Database
    if any(x in path_lower for x in ['database', 'schema', 'migration', 'sqlite']):
        if 'migration' in path_lower:
            return "Database: Migrations"
        elif 'schema' in path_lower:
            return "Database: Schema"
        else:
            return "Database: Core"
    
    # AI/Agent
    if any(x in path_lower for x in ['agent', 'claude', 'anthropic', 'openai', 'deepseek']):
        if 'worker' in path_lower:
            return "AI: Agent Worker"
        elif 'route' in path_lower:
            return "AI: Agent Routes"
        elif 'prompt' in path_lower:
            return "AI: Prompts"
        else:
            return "AI: Core Infrastructure"
    
    # Thread Management
    if any(x in path_lower for x in ['thread', 'conversation', 'message']):
        return "Threads: Management"
    
    # Task/Calendar Sync
    if any(x in path_lower for x in ['task', 'sync', 'calendar', 'todoist']):
        return "Integration: Task Sync"
    
    # Stock Management / Calculator
    if 'stock' in path_lower or 'calculator' in path_lower or 'pricing' in path_lower:
        if 'calculator' in path_lower:
            return "Stock: Quote Calculator"
        elif 'api' in path_lower:
            return "Stock: API Integration"
        else:
            return "Stock: Management System"
    
    # Specific files
    if 'flask_app' in name:
        return "Flask: Main Application"
    if 'registry' in name:
        return "Tools: Registry System"
    if 'business-ai-platform' in name:
        return "UI: Main Platform"
    
    # Documentation
    if file_path.endswith('.md'):
        if 'readme' in name:
            return "Docs: README"
        elif any(x in name for x in ['template', 'guide', 'specification']):
            return "Docs: Templates/Guides"
        else:
            return "Docs: Project Documentation"
    
    # Scripts
    if any(x in parts for x in ['scripts', 'testing']):
        if 'test' in name or 'check' in name:
            return "Scripts: Testing"
        elif 'setup' in name:
            return "Scripts: Setup"
        else:
            return "Scripts: Utilities"
    
    # Configuration
    if file_path.endswith(('.json', '.yaml', '.yml', '.env', '.toml')):
        return "Config: Settings"
    
    return "Other"

def analyze_granular(base_path, project_name):
    """Detailed analysis with hour-level granularity"""
    
    print(f"\n{'='*80}")
    print(f"ANALYZING: {project_name}")
    print(f"{'='*80}\n")
    
    files_data = []
    category_timeline = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'size': 0}))
    hourly_activity = defaultdict(lambda: defaultdict(int))
    
    # Scan files
    print("Scanning files...")
    for root, dirs, files in os.walk(base_path):
        skip_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive', '.next']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                
                category = categorize_file_granular(file_path, base_path)
                
                date_str = created.strftime('%Y-%m-%d')
                hour_str = created.strftime('%Y-%m-%d %H:00')
                
                files_data.append({
                    'path': os.path.relpath(file_path, base_path),
                    'category': category,
                    'created': created,
                    'size': stats.st_size
                })
                
                category_timeline[category][date_str]['count'] += 1
                category_timeline[category][date_str]['size'] += stats.st_size
                
                hourly_activity[category][hour_str] += 1
                
            except Exception as e:
                continue
    
    print(f"Analyzed {len(files_data)} files\n")
    
    return files_data, category_timeline, hourly_activity

def create_gantt_html(ai_data, g_folder_data):
    """Create interactive Gantt chart HTML"""
    
    ai_files, ai_timeline, ai_hourly = ai_data
    g_files, g_timeline, g_hourly = g_folder_data
    
    # Combine all dates
    all_dates = set()
    for timeline in [ai_timeline, g_timeline]:
        for category, dates in timeline.items():
            all_dates.update(dates.keys())
    
    date_list = sorted(list(all_dates))
    
    if not date_list:
        return
    
    start_date = datetime.strptime(date_list[0], '%Y-%m-%d')
    end_date = datetime.strptime(date_list[-1], '%Y-%m-%d')
    
    # Get all unique categories
    ai_categories = sorted(ai_timeline.keys())
    g_categories = sorted(g_timeline.keys())
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Development Gantt Chart</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 98%;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .project-section {{
            padding: 40px;
        }}
        
        .project-title {{
            font-size: 2em;
            color: #667eea;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .gantt-container {{
            overflow-x: auto;
            margin-bottom: 50px;
        }}
        
        .gantt-chart {{
            min-width: 1200px;
            border: 1px solid #ddd;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .gantt-header {{
            display: grid;
            grid-template-columns: 300px repeat(auto-fill, minmax(40px, 1fr));
            background: #f8f9fa;
            border-bottom: 2px solid #667eea;
        }}
        
        .gantt-header-cell {{
            padding: 10px 5px;
            text-align: center;
            font-size: 0.85em;
            font-weight: bold;
            border-right: 1px solid #ddd;
        }}
        
        .gantt-header-cell.category-label {{
            text-align: left;
            padding-left: 15px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 1em;
        }}
        
        .gantt-row {{
            display: grid;
            grid-template-columns: 300px repeat({len(date_list)}, minmax(40px, 1fr));
            border-bottom: 1px solid #eee;
        }}
        
        .gantt-row:hover {{
            background: #f8f9fa;
        }}
        
        .gantt-cell {{
            padding: 15px 5px;
            text-align: center;
            border-right: 1px solid #eee;
            position: relative;
        }}
        
        .gantt-cell.category {{
            text-align: left;
            padding-left: 15px;
            font-weight: bold;
            color: #333;
            background: #f8f9fa;
        }}
        
        .gantt-bar {{
            height: 25px;
            border-radius: 5px;
            position: relative;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .gantt-bar:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .gantt-bar.low {{
            background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);
        }}
        
        .gantt-bar.medium {{
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .gantt-bar.high {{
            background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .gantt-bar-label {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 0.75em;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .tooltip {{
            display: none;
            position: absolute;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 0.85em;
            z-index: 1000;
            white-space: nowrap;
        }}
        
        .gantt-bar:hover .tooltip {{
            display: block;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 30px;
            height: 20px;
            border-radius: 5px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .weekend {{
            background: rgba(255, 107, 107, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Project Development Gantt Chart</h1>
            <div class="subtitle">Detailed Timeline Analysis: AI_agents & G_Folder Projects</div>
            <div style="margin-top: 20px; font-size: 1.1em;">
                {start_date.strftime('%B %d, %Y')} → {end_date.strftime('%B %d, %Y')} 
                ({(end_date - start_date).days + 1} days)
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);"></div>
                <span>Low Activity (1-5 files)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);"></div>
                <span>Medium Activity (6-20 files)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);"></div>
                <span>High Activity (21+ files)</span>
            </div>
        </div>
"""
    
    # AI_agents section
    html += f"""
        <div class="project-section">
            <h2 class="project-title">🤖 AI_agents Project</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Files</h3>
                    <div class="value">{len(ai_files):,}</div>
                </div>
                <div class="stat-card">
                    <h3>Categories</h3>
                    <div class="value">{len(ai_categories)}</div>
                </div>
                <div class="stat-card">
                    <h3>Active Days</h3>
                    <div class="value">{len([d for d in date_list if any(d in dates for dates in ai_timeline.values())])}</div>
                </div>
                <div class="stat-card">
                    <h3>Period</h3>
                    <div class="value" style="font-size: 1.2em;">17 days</div>
                </div>
            </div>
            
            <div class="gantt-container">
                <div class="gantt-chart">
                    <div class="gantt-header">
                        <div class="gantt-header-cell category-label">Module/Category</div>
"""
    
    # Date headers
    for date_str in date_list:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        is_weekend = date_obj.weekday() >= 5
        weekend_class = 'weekend' if is_weekend else ''
        html += f'<div class="gantt-header-cell {weekend_class}">{date_obj.strftime("%m/%d")}<br>{date_obj.strftime("%a")}</div>\n'
    
    html += """
                    </div>
"""
    
    # AI_agents rows
    for category in ai_categories:
        html += f"""
                    <div class="gantt-row">
                        <div class="gantt-cell category">{category}</div>
"""
        
        for date_str in date_list:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            is_weekend = date_obj.weekday() >= 5
            weekend_class = 'weekend' if is_weekend else ''
            
            if date_str in ai_timeline[category]:
                count = ai_timeline[category][date_str]['count']
                
                if count <= 5:
                    intensity = 'low'
                elif count <= 20:
                    intensity = 'medium'
                else:
                    intensity = 'high'
                
                html += f"""
                        <div class="gantt-cell {weekend_class}">
                            <div class="gantt-bar {intensity}">
                                <span class="gantt-bar-label">{count}</span>
                                <div class="tooltip">{count} files created</div>
                            </div>
                        </div>
"""
            else:
                html += f'<div class="gantt-cell {weekend_class}"></div>\n'
        
        html += """
                    </div>
"""
    
    html += """
                </div>
            </div>
        </div>
"""
    
    # G_Folder section
    html += f"""
        <div class="project-section">
            <h2 class="project-title">📊 G_Folder Project</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Files</h3>
                    <div class="value">{len(g_files):,}</div>
                </div>
                <div class="stat-card">
                    <h3>Categories</h3>
                    <div class="value">{len(g_categories)}</div>
                </div>
                <div class="stat-card">
                    <h3>Active Days</h3>
                    <div class="value">{len([d for d in date_list if any(d in dates for dates in g_timeline.values())])}</div>
                </div>
                <div class="stat-card">
                    <h3>Period</h3>
                    <div class="value" style="font-size: 1.2em;">26 days</div>
                </div>
            </div>
            
            <div class="gantt-container">
                <div class="gantt-chart">
                    <div class="gantt-header">
                        <div class="gantt-header-cell category-label">Module/Category</div>
"""
    
    # Date headers again
    for date_str in date_list:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        is_weekend = date_obj.weekday() >= 5
        weekend_class = 'weekend' if is_weekend else ''
        html += f'<div class="gantt-header-cell {weekend_class}">{date_obj.strftime("%m/%d")}<br>{date_obj.strftime("%a")}</div>\n'
    
    html += """
                    </div>
"""
    
    # G_Folder rows
    for category in g_categories:
        html += f"""
                    <div class="gantt-row">
                        <div class="gantt-cell category">{category}</div>
"""
        
        for date_str in date_list:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            is_weekend = date_obj.weekday() >= 5
            weekend_class = 'weekend' if is_weekend else ''
            
            if date_str in g_timeline[category]:
                count = g_timeline[category][date_str]['count']
                
                if count <= 5:
                    intensity = 'low'
                elif count <= 20:
                    intensity = 'medium'
                else:
                    intensity = 'high'
                
                html += f"""
                        <div class="gantt-cell {weekend_class}">
                            <div class="gantt-bar {intensity}">
                                <span class="gantt-bar-label">{count}</span>
                                <div class="tooltip">{count} files created</div>
                            </div>
                        </div>
"""
            else:
                html += f'<div class="gantt-cell {weekend_class}"></div>\n'
        
        html += """
                    </div>
"""
    
    html += """
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    output_file = 'project_gantt_chart.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Gantt chart created: {output_file}")
    return output_file

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CREATING DETAILED PROJECT GANTT CHARTS")
    print("="*80)
    
    # Analyze AI_agents
    ai_path = r"c:\Users\gpoli\GIT\AI_agents"
    ai_data = analyze_granular(ai_path, "AI_agents")
    
    # Analyze G_Folder
    g_path = r"c:\Users\gpoli\GIT\In_House_SQL"
    g_data = analyze_granular(g_path, "G_Folder (In_House_SQL)")
    
    # Create visualization
    print("\nGenerating Gantt chart HTML...")
    output = create_gantt_html(ai_data, g_data)
    
    print(f"\n{'='*80}")
    print(f"✅ Complete! Open the file to view the interactive Gantt chart.")
    print(f"{'='*80}\n")
