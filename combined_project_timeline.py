"""
Create combined horizontal timeline showing project evolution
G_Folder (Streamlit) → AI_agents integration as one continuous journey
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

def categorize_unified(file_path, base_path, project_name):
    """Unified categorization showing technology evolution"""
    path_lower = file_path.lower()
    name = os.path.basename(file_path).lower()
    
    # Streamlit/Flask evolution
    if 'streamlit' in path_lower or '.py' in name and project_name == 'G_Folder':
        if 'app' in name or 'main' in name:
            return "🐍 Streamlit Frontend"
        return "🐍 Python Backend"
    
    # Flask evolution
    if 'flask' in path_lower:
        return "🌶️ Flask Backend"
    
    # AI Integration attempts
    if any(x in path_lower for x in ['claude', 'anthropic', 'openai', 'deepseek', 'agent', 'llm']):
        return "🤖 AI Integration"
    
    # Stock/Calculator (core feature across both)
    if any(x in path_lower for x in ['stock', 'calculator', 'pricing', 'quote']):
        return "💰 Quote Calculator"
    
    # UI Evolution
    if any(x in path_lower for x in ['ui/', 'html', 'css', 'javascript', 'tabulator']):
        if 'business-ai-platform' in path_lower:
            return "🎨 AI Platform UI (New)"
        return "🎨 UI Components"
    
    # Database
    if any(x in path_lower for x in ['database', 'schema', 'sqlite', 'migration']):
        return "💾 Database"
    
    # Authentication
    if any(x in path_lower for x in ['auth', 'oauth', 'credential', 'login']):
        return "🔐 Authentication"
    
    # Tools & Integrations
    if 'tools' in path_lower or 'integration' in path_lower:
        return "🔧 Tool Integrations"
    
    # Thread/Chat
    if any(x in path_lower for x in ['thread', 'chat', 'message', 'conversation']):
        return "💬 Chat System"
    
    # Documentation
    if file_path.endswith('.md'):
        return "📚 Documentation"
    
    return "⚙️ Other"

def analyze_combined_timeline(ai_path, g_path):
    """Analyze both projects as one timeline"""
    
    print(f"\n{'='*100}")
    print("COMBINED PROJECT TIMELINE ANALYSIS")
    print("G_Folder (Streamlit) → AI_agents (Flask + AI) Integration Journey")
    print(f"{'='*100}\n")
    
    all_files = []
    
    # Scan G_Folder
    print("📊 Scanning G_Folder (In_House_SQL)...")
    for root, dirs, files in os.walk(g_path):
        skip_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                category = categorize_unified(file_path, g_path, 'G_Folder')
                
                all_files.append({
                    'project': 'G_Folder',
                    'path': os.path.relpath(file_path, g_path),
                    'category': category,
                    'created': created,
                    'size': stats.st_size
                })
            except:
                continue
    
    print(f"   Found {len([f for f in all_files if f['project'] == 'G_Folder'])} files\n")
    
    # Scan AI_agents
    print("🤖 Scanning AI_agents...")
    for root, dirs, files in os.walk(ai_path):
        skip_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                category = categorize_unified(file_path, ai_path, 'AI_agents')
                
                all_files.append({
                    'project': 'AI_agents',
                    'path': os.path.relpath(file_path, ai_path),
                    'category': category,
                    'created': created,
                    'size': stats.st_size
                })
            except:
                continue
    
    ai_count = len([f for f in all_files if f['project'] == 'AI_agents'])
    print(f"   Found {ai_count} files\n")
    
    # Sort by date
    all_files.sort(key=lambda x: x['created'])
    
    # Build timeline
    timeline = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'projects': set()}))
    
    for file in all_files:
        date_str = file['created'].strftime('%Y-%m-%d')
        timeline[date_str][file['category']]['count'] += 1
        timeline[date_str][file['category']]['projects'].add(file['project'])
    
    return all_files, timeline

def create_horizontal_timeline_html(all_files, timeline):
    """Create horizontally scrollable timeline"""
    
    dates = sorted(timeline.keys())
    if not dates:
        return
    
    start = datetime.strptime(dates[0], '%Y-%m-%d')
    end = datetime.strptime(dates[-1], '%Y-%m-%d')
    total_days = (end - start).days + 1
    
    # Get all categories
    categories = set()
    for date_data in timeline.values():
        categories.update(date_data.keys())
    categories = sorted(list(categories))
    
    # Calculate project transition point
    g_files = [f for f in all_files if f['project'] == 'G_Folder']
    ai_files = [f for f in all_files if f['project'] == 'AI_agents']
    
    g_last_date = max(f['created'] for f in g_files) if g_files else start
    ai_first_date = min(f['created'] for f in ai_files) if ai_files else end
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Combined Project Timeline - Evolution Journey</title>
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
            margin-bottom: 15px;
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.95;
            margin-bottom: 20px;
        }}
        
        .timeline-info {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            font-size: 1.1em;
        }}
        
        .info-box {{
            background: rgba(255,255,255,0.2);
            padding: 15px 30px;
            border-radius: 10px;
        }}
        
        .info-box strong {{
            display: block;
            font-size: 1.5em;
            margin-bottom: 5px;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 30px;
            background: #f8f9fa;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.1em;
        }}
        
        .legend-bar {{
            width: 40px;
            height: 25px;
            border-radius: 5px;
        }}
        
        .timeline-scroll {{
            overflow-x: auto;
            overflow-y: visible;
            padding: 40px;
            background: white;
        }}
        
        .timeline-container {{
            min-width: {total_days * 60}px;
            position: relative;
            padding: 20px 0;
        }}
        
        .date-axis {{
            display: flex;
            position: relative;
            height: 50px;
            margin-bottom: 30px;
            border-bottom: 3px solid #667eea;
        }}
        
        .date-marker {{
            position: absolute;
            width: 2px;
            height: 100%;
            background: #ddd;
        }}
        
        .date-marker.major {{
            background: #667eea;
            width: 3px;
        }}
        
        .date-label {{
            position: absolute;
            bottom: -25px;
            transform: translateX(-50%);
            font-size: 0.85em;
            font-weight: bold;
            white-space: nowrap;
        }}
        
        .date-label.major {{
            font-size: 1em;
            color: #667eea;
        }}
        
        .project-marker {{
            position: absolute;
            top: -40px;
            padding: 8px 20px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 1.1em;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transform: translateX(-50%);
        }}
        
        .project-marker.g-folder {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .project-marker.ai-agents {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        
        .categories-container {{
            position: relative;
        }}
        
        .category-row {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            position: relative;
        }}
        
        .category-label {{
            width: 250px;
            padding: 10px 15px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
            border-radius: 10px 0 0 10px;
            font-size: 1em;
        }}
        
        .category-timeline {{
            flex: 1;
            height: 50px;
            position: relative;
            background: #f8f9fa;
            border-radius: 0 10px 10px 0;
        }}
        
        .activity-bar {{
            position: absolute;
            height: 100%;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .activity-bar:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
            z-index: 10;
        }}
        
        .activity-bar.g-folder {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .activity-bar.ai-agents {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .activity-bar.both {{
            background: linear-gradient(135deg, #f093fb 0%, #4facfe 100%);
            border: 2px solid #fff;
        }}
        
        .tooltip {{
            display: none;
            position: absolute;
            bottom: 110%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.95);
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.9em;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        
        .activity-bar:hover .tooltip {{
            display: block;
        }}
        
        .transition-marker {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 4px;
            background: repeating-linear-gradient(
                45deg,
                #f5576c,
                #f5576c 10px,
                #4facfe 10px,
                #4facfe 20px
            );
            z-index: 5;
        }}
        
        .transition-label {{
            position: absolute;
            top: 50%;
            left: 10px;
            transform: translateY(-50%);
            background: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            border: 3px solid #667eea;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-box {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 4px solid #667eea;
        }}
        
        .stat-box h3 {{
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-box .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}
        
        .stat-box .label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .weekend {{
            background: rgba(255, 107, 107, 0.05);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Project Evolution Timeline</h1>
            <div class="subtitle">From Streamlit Prototype → Full AI Agent Platform</div>
            <div class="timeline-info">
                <div class="info-box">
                    <strong>{start.strftime('%b %d, %Y')}</strong>
                    <span>Start Date</span>
                </div>
                <div class="info-box">
                    <strong>{total_days} Days</strong>
                    <span>Development Period</span>
                </div>
                <div class="info-box">
                    <strong>{end.strftime('%b %d, %Y')}</strong>
                    <span>End Date</span>
                </div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-bar" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"></div>
                <span>G_Folder (Streamlit)</span>
            </div>
            <div class="legend-item">
                <div class="legend-bar" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"></div>
                <span>AI_agents (Flask + AI)</span>
            </div>
            <div class="legend-item">
                <div class="legend-bar" style="background: linear-gradient(135deg, #f093fb 0%, #4facfe 100%); border: 2px solid #fff;"></div>
                <span>Both Projects</span>
            </div>
        </div>
        
        <div class="timeline-scroll">
            <div class="timeline-container">
                <div class="date-axis">
"""
    
    # Add date markers
    for i in range(total_days):
        current_date = start + timedelta(days=i)
        left_pos = (i / total_days) * 100
        
        is_major = current_date.day == 1 or current_date.weekday() == 0  # First of month or Monday
        marker_class = "major" if is_major else ""
        label_class = "major" if is_major else ""
        
        if is_major or i == 0 or i == total_days - 1:
            html += f"""
                    <div class="date-marker {marker_class}" style="left: {left_pos}%;"></div>
                    <div class="date-label {label_class}" style="left: {left_pos}%;">
                        {current_date.strftime('%b %d')}
                    </div>
"""
    
    # Add project markers
    g_folder_end = ((g_last_date - start).days / total_days) * 100
    ai_agents_start = ((ai_first_date - start).days / total_days) * 100
    
    html += f"""
                    <div class="project-marker g-folder" style="left: {g_folder_end/2}%;">
                        📊 G_Folder Phase<br><small>Streamlit + Python</small>
                    </div>
                    <div class="project-marker ai-agents" style="left: {(ai_agents_start + 100)/2}%;">
                        🤖 AI_agents Phase<br><small>Flask + AI Integration</small>
                    </div>
"""
    
    html += """
                </div>
                
                <div class="categories-container">
"""
    
    # Add transition marker if there's overlap
    if ai_agents_start <= g_folder_end:
        transition_pos = ((ai_agents_start + g_folder_end) / 2)
        html += f"""
                    <div class="transition-marker" style="left: {transition_pos}%;"></div>
                    <div class="transition-label" style="left: {transition_pos}%;">
                        🔄 Integration<br>Attempt
                    </div>
"""
    
    # Add category rows
    for category in categories:
        html += f"""
                    <div class="category-row">
                        <div class="category-label">{category}</div>
                        <div class="category-timeline">
"""
        
        # Add activity bars for this category
        for date_str in dates:
            if category in timeline[date_str]:
                data = timeline[date_str][category]
                count = data['count']
                projects = data['projects']
                
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                days_from_start = (date_obj - start).days
                left_pos = (days_from_start / total_days) * 100
                width = (1 / total_days) * 100
                
                # Determine which project(s)
                if len(projects) > 1:
                    bar_class = "both"
                    project_label = "Both Projects"
                elif 'G_Folder' in projects:
                    bar_class = "g-folder"
                    project_label = "G_Folder"
                else:
                    bar_class = "ai-agents"
                    project_label = "AI_agents"
                
                html += f"""
                            <div class="activity-bar {bar_class}" style="left: {left_pos}%; width: {width}%;">
                                {count if count > 5 else ''}
                                <div class="tooltip">
                                    {date_obj.strftime('%b %d, %Y')}<br>
                                    {project_label}<br>
                                    <strong>{count} files</strong>
                                </div>
                            </div>
"""
        
        html += """
                        </div>
                    </div>
"""
    
    html += """
                </div>
            </div>
        </div>
        
        <div class="stats">
"""
    
    # Calculate stats
    g_count = len([f for f in all_files if f['project'] == 'G_Folder'])
    ai_count = len([f for f in all_files if f['project'] == 'AI_agents'])
    g_dates = set(f['created'].strftime('%Y-%m-%d') for f in all_files if f['project'] == 'G_Folder')
    ai_dates = set(f['created'].strftime('%Y-%m-%d') for f in all_files if f['project'] == 'AI_agents')
    
    html += f"""
            <div class="stat-box">
                <h3>G_Folder Files</h3>
                <div class="value">{g_count:,}</div>
                <div class="label">Streamlit Phase</div>
            </div>
            <div class="stat-box">
                <h3>AI_agents Files</h3>
                <div class="value">{ai_count:,}</div>
                <div class="label">Flask + AI Phase</div>
            </div>
            <div class="stat-box">
                <h3>Total Files</h3>
                <div class="value">{len(all_files):,}</div>
                <div class="label">Combined Projects</div>
            </div>
            <div class="stat-box">
                <h3>G_Folder Days</h3>
                <div class="value">{len(g_dates)}</div>
                <div class="label">Active Days</div>
            </div>
            <div class="stat-box">
                <h3>AI_agents Days</h3>
                <div class="value">{len(ai_dates)}</div>
                <div class="label">Active Days</div>
            </div>
            <div class="stat-box">
                <h3>Categories</h3>
                <div class="value">{len(categories)}</div>
                <div class="label">Development Areas</div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    output_file = 'combined_project_timeline.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Combined timeline created: {output_file}")
    return output_file

if __name__ == "__main__":
    ai_path = r"c:\Users\gpoli\GIT\AI_agents"
    g_path = r"c:\Users\gpoli\GIT\In_House_SQL"
    
    all_files, timeline = analyze_combined_timeline(ai_path, g_path)
    create_horizontal_timeline_html(all_files, timeline)
    
    print(f"\n{'='*100}")
    print("✅ COMPLETE! Open combined_project_timeline.html to see the full journey")
    print(f"{'='*100}\n")
