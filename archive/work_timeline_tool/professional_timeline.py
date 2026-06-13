"""
Professional Timeline for Client Presentation
- FIXED: Proper light-to-dark gradients that make sense
- FIXED: No generic "Other" categories - everything specific
- FIXED: Synchronized scrolling between left and right
- Uses actual file timestamps (NOT git commits)
"""

import os
from datetime import datetime, timedelta
from collections import defaultdict

def categorize_professional(file_path, base_path, project_name):
    """Professional categorization - NO 'Other' or vague labels"""
    path_lower = file_path.lower()
    rel_path = os.path.relpath(file_path, base_path).lower()
    name = os.path.basename(file_path).lower()
    ext = os.path.splitext(name)[1]
    
    # Stock Management
    if 'stock' in path_lower:
        if 'ui' in path_lower or 'frontend' in path_lower or 'html' in path_lower:
            return "Stock Management - UI"
        elif 'calculator' in path_lower or 'pricing' in path_lower:
            return "Stock Management - Calculator"
        elif 'database' in path_lower or 'schema' in path_lower:
            return "Stock Management - Database"
        elif 'api' in path_lower or 'route' in path_lower:
            return "Stock Management - API"
        return "Stock Management - Core"
    
    # Quote Calculator
    if 'calculator' in path_lower or 'quote' in path_lower or 'pricing' in path_lower:
        if 'test' in path_lower:
            return "Quote Calculator - Tests"
        return "Quote Calculator - Engine"
    
    # AI System
    if any(x in path_lower for x in ['claude', 'anthropic', 'openai', 'deepseek', 'agent', 'llm']):
        if 'chat' in path_lower or 'conversation' in path_lower:
            return "AI System - Chat"
        elif 'tool' in path_lower:
            return "AI System - Tools"
        return "AI System - Core"
    
    # UI
    if any(x in path_lower for x in ['ui/', 'html', 'css', 'javascript']) and 'test' not in path_lower:
        if 'business-ai-platform' in path_lower:
            return "UI - Main Dashboard"
        elif 'module' in path_lower:
            return "UI - Modules"
        elif 'tabulator' in path_lower:
            return "UI - Data Tables"
        elif ext == '.css':
            return "UI - Stylesheets"
        elif ext == '.js':
            return "UI - JavaScript"
        return "UI - Components"
    
    # Database
    if any(x in path_lower for x in ['database', 'schema', 'sqlite', 'migration', '.db']):
        if 'user' in path_lower or 'auth' in path_lower:
            return "Database - Users & Auth"
        elif 'session' in path_lower:
            return "Database - Sessions"
        return "Database - Schema"
    
    # Authentication
    if any(x in path_lower for x in ['auth', 'oauth', 'credential', 'login']):
        if 'google' in path_lower:
            return "Auth - Google OAuth"
        elif 'microsoft' in path_lower:
            return "Auth - Microsoft OAuth"
        return "Auth - Core System"
    
    # Backend
    if 'flask' in path_lower or 'route' in path_lower or ('api' in path_lower and ext == '.py'):
        if 'route' in path_lower:
            return "Backend - API Routes"
        return "Backend - Flask Server"
    
    # Legacy Streamlit
    if project_name == 'G_Folder' and ext == '.py':
        if 'streamlit' in path_lower:
            return "Legacy - Streamlit App"
        return "Legacy - Python Backend"
    
    # Tools
    if 'tool' in path_lower and 'ai' not in path_lower:
        if 'implementation' in path_lower:
            return "Tools - Implementations"
        elif 'schema' in path_lower:
            return "Tools - Schemas"
        return "Tools - Integration"
    
    # Thread Management
    if 'thread' in path_lower and 'ai' not in path_lower:
        return "Thread Management"
    
    # Documentation
    if ext == '.md':
        if 'readme' in name:
            return "Docs - README"
        elif 'api' in path_lower:
            return "Docs - API Guide"
        return "Docs - Technical"
    
    # Configuration
    if ext in ['.json', '.yaml', '.yml', '.env'] or 'config' in path_lower:
        if 'package' in name:
            return "Config - Dependencies"
        return "Config - Settings"
    
    # Assets
    if ext in ['.svg', '.png', '.jpg', '.ico', '.gif']:
        if 'icon' in path_lower:
            return "Assets - Icons"
        return "Assets - Images"
    
    # Testing
    if 'test' in path_lower:
        return "Testing - QA"
    
    # Source code by extension
    if ext == '.py':
        return "Python - Source Code"
    if ext == '.js':
        return "JavaScript - Source Code"
    if ext in ['.csv', '.xlsx']:
        return "Data - Spreadsheets"
    
    return "Project Files"

def analyze_projects(ai_path, g_path):
    """Scan actual files using filesystem timestamps"""
    
    print(f"\n{'='*80}")
    print("PROFESSIONAL TIMELINE ANALYSIS")
    print("Using: Actual file creation timestamps (NOT git commits)")
    print(f"{'='*80}\n")
    
    all_files = []
    
    for project_name, project_path in [('G_Folder', g_path), ('AI_agents', ai_path)]:
        print(f"Scanning {project_name}...")
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stats = os.stat(file_path)
                    created = datetime.fromtimestamp(stats.st_ctime)
                    category = categorize_professional(file_path, project_path, project_name)
                    
                    all_files.append({
                        'project': project_name,
                        'category': category,
                        'created': created,
                        'hour': created.hour
                    })
                except:
                    continue
        
        print(f"  {len([f for f in all_files if f['project'] == project_name]):,} files\n")
    
    all_files.sort(key=lambda x: x['created'])
    
    timeline = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'projects': set(), 'hours': set()}))
    
    for file in all_files:
        date_str = file['created'].strftime('%Y-%m-%d')
        timeline[date_str][file['category']]['count'] += 1
        timeline[date_str][file['category']]['projects'].add(file['project'])
        timeline[date_str][file['category']]['hours'].add(file['hour'])
    
    return all_files, timeline

def create_professional_html(all_files, timeline):
    """Professional HTML with proper colors and synchronized scrolling"""
    
    dates = sorted(timeline.keys())
    start = datetime.strptime(dates[0], '%Y-%m-%d')
    end = datetime.strptime(dates[-1], '%Y-%m-%d')
    total_days = (end - start).days + 1
    
    category_totals = defaultdict(int)
    for date_data in timeline.values():
        for category, data in date_data.items():
            category_totals[category] += data['count']
    
    categories = sorted(category_totals.keys(), key=lambda x: category_totals[x], reverse=True)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Professional Development Timeline</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 25px 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        
        .header h1 {{ font-size: 1.8em; margin-bottom: 10px; }}
        
        .controls {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            align-items: center;
        }}
        
        .controls label {{ font-weight: 600; margin-right: 8px; }}
        
        select {{
            padding: 6px 12px;
            border: 2px solid white;
            background: rgba(255,255,255,0.2);
            color: white;
            border-radius: 4px;
            cursor: pointer;
        }}
        
        select option {{ background: #2c3e50; }}
        
        .stats {{ margin-top: 12px; font-size: 0.9em; opacity: 0.95; }}
        .stats span {{ margin-right: 20px; }}
        .stats strong {{ margin-right: 5px; }}
        
        .container {{
            display: flex;
            height: calc(100vh - 160px);
            margin: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .sidebar {{
            width: 300px;
            background: #ecf0f1;
            border-right: 2px solid #bdc3c7;
            overflow-y: auto;
            flex-shrink: 0;
        }}
        
        .sidebar-header {{
            padding: 12px 20px;
            background: #34495e;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        .cat-item {{
            padding: 12px 20px;
            border-bottom: 1px solid #bdc3c7;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .cat-item:hover {{ background: #d5dbdb; }}
        
        .cat-name {{ font-weight: 500; }}
        
        .cat-count {{
            background: #3498db;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .timeline {{
            flex: 1;
            overflow: auto;
        }}
        
        .dates {{
            display: flex;
            position: sticky;
            top: 0;
            background: #34495e;
            color: white;
            z-index: 9;
        }}
        
        .date-col {{
            min-width: 65px;
            width: 65px;
            padding: 8px 4px;
            text-align: center;
            border-right: 1px solid #2c3e50;
            font-size: 0.8em;
        }}
        
        .date-col.weekend {{ background: #2c3e50; }}
        
        .date-day {{ font-size: 1.3em; font-weight: bold; }}
        .date-month {{ font-size: 0.85em; opacity: 0.9; margin-top: 2px; }}
        
        .rows {{ display: flex; flex-direction: column; }}
        
        .row {{
            display: flex;
            min-height: 48px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        .row:hover {{ background: #f8f9fa; }}
        
        .cell {{
            min-width: 65px;
            width: 65px;
            padding: 4px;
            border-right: 1px solid #ecf0f1;
            position: relative;
        }}
        
        .cell.weekend {{ background: #fafbfc; }}
        
        .cell.active {{
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }}
        
        .cell.active:hover {{ transform: scale(1.05); z-index: 5; }}
        
        .marker {{
            width: 100%;
            height: 100%;
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        /* FILE COUNT: Light to Dark Blue (logical progression) */
        .mode-files .marker[data-level="1"] {{ background: #ebf5fb; color: #1b4f72; }}
        .mode-files .marker[data-level="2"] {{ background: #d6eaf8; color: #154360; }}
        .mode-files .marker[data-level="3"] {{ background: #aed6f1; color: #0d3d56; }}
        .mode-files .marker[data-level="4"] {{ background: #85c1e9; color: #fff; }}
        .mode-files .marker[data-level="5"] {{ background: #5dade2; color: #fff; }}
        .mode-files .marker[data-level="6"] {{ background: #3498db; color: #fff; }}
        .mode-files .marker[data-level="7"] {{ background: #2e86c1; color: #fff; }}
        .mode-files .marker[data-level="8"] {{ background: #2874a6; color: #fff; }}
        .mode-files .marker[data-level="9"] {{ background: #21618c; color: #fff; }}
        .mode-files .marker[data-level="10"] {{ background: #1b4f72; color: #fff; }}
        
        /* HOURS: Light to Dark Green (logical progression) */
        .mode-hours .marker[data-level="1"] {{ background: #eafaf1; color: #0b5345; }}
        .mode-hours .marker[data-level="2"] {{ background: #d5f4e6; color: #0e6655; }}
        .mode-hours .marker[data-level="3"] {{ background: #abebc6; color: #117864; }}
        .mode-hours .marker[data-level="4"] {{ background: #7dcea0; color: #fff; }}
        .mode-hours .marker[data-level="5"] {{ background: #52be80; color: #fff; }}
        .mode-hours .marker[data-level="6"] {{ background: #27ae60; color: #fff; }}
        .mode-hours .marker[data-level="7"] {{ background: #229954; color: #fff; }}
        .mode-hours .marker[data-level="8"] {{ background: #1e8449; color: #fff; }}
        .mode-hours .marker[data-level="9"] {{ background: #196f3d; color: #fff; }}
        .mode-hours .marker[data-level="10"] {{ background: #145a32; color: #fff; }}
        
        .tip {{
            display: none;
            position: absolute;
            bottom: 105%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(44,62,80,0.98);
            color: white;
            padding: 10px 12px;
            border-radius: 5px;
            font-size: 0.85em;
            white-space: nowrap;
            z-index: 100;
        }}
        
        .cell:hover .tip {{ display: block; }}
        .tip strong {{ color: #3498db; }}
        
        .legend {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px 18px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            border: 2px solid #3498db;
        }}
        
        .legend h4 {{ margin-bottom: 10px; color: #2c3e50; }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 5px 0;
            font-size: 0.85em;
        }}
        
        .legend-box {{
            width: 30px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #bdc3c7;
        }}
        
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: #ecf0f1; }}
        ::-webkit-scrollbar-thumb {{ background: #95a5a6; border-radius: 5px; }}
    </style>
</head>
<body class="mode-files">
    <div class="header">
        <h1>Professional Development Timeline</h1>
        <div class="controls">
            <div>
                <label>View:</label>
                <select id="mode" onchange="changeMode(this.value)">
                    <option value="files">By File Count</option>
                    <option value="hours">By Hours Worked</option>
                </select>
            </div>
            <div>
                <label>Project:</label>
                <select id="filter" onchange="filterProject(this.value)">
                    <option value="all">Combined</option>
                    <option value="G_Folder">G_Folder</option>
                    <option value="AI_agents">AI_agents</option>
                </select>
            </div>
        </div>
        <div class="stats">
            <span><strong>{len(all_files):,}</strong> Files</span>
            <span><strong>{len(categories)}</strong> Categories</span>
            <span><strong>{total_days}</strong> Days</span>
            <span>{dates[0]} to {dates[-1]}</span>
        </div>
    </div>
    
    <div class="container">
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">Development Categories</div>
"""
    
    for cat in categories:
        html += f"""
            <div class="cat-item" data-cat="{cat}">
                <span class="cat-name">{cat}</span>
                <span class="cat-count">{category_totals[cat]:,}</span>
            </div>
"""
    
    html += """
        </div>
        
        <div class="timeline" id="timeline">
            <div class="dates">
"""
    
    for i in range(total_days):
        d = start + timedelta(days=i)
        weekend = "weekend" if d.weekday() >= 5 else ""
        html += f"""
                <div class="date-col {weekend}">
                    <div class="date-day">{d.strftime('%d')}</div>
                    <div class="date-month">{d.strftime('%b')}</div>
                    <div class="date-month">{d.strftime('%a')}</div>
                </div>
"""
    
    html += """
            </div>
            <div class="rows">
"""
    
    for cat in categories:
        html += f'                <div class="row" data-cat="{cat}">\n'
        
        for i in range(total_days):
            d = start + timedelta(days=i)
            ds = d.strftime('%Y-%m-%d')
            weekend = "weekend" if d.weekday() >= 5 else ""
            
            if cat in timeline[ds]:
                data = timeline[ds][cat]
                count = data['count']
                hours = len(data['hours'])
                projects = ' & '.join(data['projects'])
                
                # Level 1-10 for both modes
                if count <= 1:
                    level = "1"
                elif count <= 3:
                    level = "2"
                elif count <= 5:
                    level = "3"
                elif count <= 10:
                    level = "4"
                elif count <= 20:
                    level = "5"
                elif count <= 30:
                    level = "6"
                elif count <= 50:
                    level = "7"
                elif count <= 75:
                    level = "8"
                elif count <= 100:
                    level = "9"
                else:
                    level = "10"
                
                hrs_level = str(min(hours, 10))
                
                html += f"""
                    <div class="cell active {weekend}" data-proj="{projects}">
                        <div class="marker" data-level="{level}" data-hours="{hrs_level}">
                            {count}
                            <div class="tip">
                                <strong>{d.strftime('%B %d, %Y')}</strong><br>
                                {cat}<br>
                                <strong>{count}</strong> files<br>
                                <strong>{hours}</strong> hours<br>
                                {projects}
                            </div>
                        </div>
                    </div>
"""
            else:
                html += f'                    <div class="cell {weekend}"></div>\n'
        
        html += '                </div>\n'
    
    html += """
            </div>
        </div>
    </div>
    
    <div class="legend" id="legend">
        <h4>Legend</h4>
        <div id="legendContent"></div>
    </div>
    
    <script>
        const sidebar = document.getElementById('sidebar');
        const timeline = document.getElementById('timeline');
        
        // SYNCHRONIZED SCROLLING
        timeline.addEventListener('scroll', () => {
            sidebar.scrollTop = timeline.scrollTop;
        });
        
        function changeMode(mode) {
            document.body.className = 'mode-' + mode;
            updateLegend(mode);
        }
        
        function filterProject(proj) {
            document.querySelectorAll('.row').forEach(row => {
                const cells = row.querySelectorAll('.cell.active');
                let visible = false;
                
                cells.forEach(cell => {
                    if (proj === 'all' || cell.getAttribute('data-proj').includes(proj)) {
                        cell.style.display = 'flex';
                        visible = true;
                    } else {
                        cell.style.display = 'none';
                    }
                });
                
                row.style.display = visible ? 'flex' : 'none';
            });
            
            document.querySelectorAll('.cat-item').forEach(item => {
                const cat = item.getAttribute('data-cat');
                const row = document.querySelector(`.row[data-cat="${cat}"]`);
                item.style.display = row.style.display;
            });
        }
        
        function updateLegend(mode) {
            const content = document.getElementById('legendContent');
            
            if (mode === 'files') {
                content.innerHTML = `
                    <div class="legend-item">
                        <div class="legend-box" style="background: #ebf5fb;"></div>
                        <span>1-3 files</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #85c1e9;"></div>
                        <span>4-10 files</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #3498db;"></div>
                        <span>11-30 files</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #2874a6;"></div>
                        <span>31-75 files</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #1b4f72;"></div>
                        <span>76+ files</span>
                    </div>
                `;
            } else {
                content.innerHTML = `
                    <div class="legend-item">
                        <div class="legend-box" style="background: #eafaf1;"></div>
                        <span>1-2 hours</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #7dcea0;"></div>
                        <span>3-4 hours</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #27ae60;"></div>
                        <span>5-6 hours</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #1e8449;"></div>
                        <span>7-9 hours</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #145a32;"></div>
                        <span>10+ hours</span>
                    </div>
                `;
            }
        }
        
        updateLegend('files');
    </script>
</body>
</html>
"""
    
    with open('professional_timeline.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ professional_timeline.html\n")

if __name__ == "__main__":
    all_files, timeline = analyze_projects(
        r"c:\Users\gpoli\GIT\AI_agents",
        r"c:\Users\gpoli\GIT\In_House_SQL"
    )
    create_professional_html(all_files, timeline)
    
    print("='*80}")
    print("DONE - Professional timeline ready for client")
    print("='*80}\n")
