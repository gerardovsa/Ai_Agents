"""
MASTER TIMELINE - ALL PROJECTS
Comprehensive timeline showing ALL 90,182 files across 28 projects
From July 22, 2025 to November 8, 2025
"""

import os
from datetime import datetime
from collections import defaultdict

# All main projects
MAIN_PROJECTS = [
    'AI_agents',
    'In_House_SQL',
    'In_House_FRED',
    'In_House_Print',
    'In_House_V2',
    'V7_In_House',
    'V7_MustCare',
    'V8_In_House',
    'SQL_Data_AI_UI_v5',
    'G_Folder Oct 8th',
    'G_Folder Oct 10th',
    'G_Folder Oct 14th',
    'G_Folder Oct 15th',
    'G_Folder Oct 17th',
    'Bonus Calculator',
    'Fontawesome',
    'HTML-PDF',
    'Inv-Stock',
    'Label_Printer',
    'MP3 Transcription',
    'MustCare ValorAISynergySuite',
    'MustCare_V2_Anthropic',
    'READY_TO_SEND',
    'Valor Extension Back Ups',
    'VALOR_AI_SIDEBAR_DOWNLOADER',
    'VSA_Valor_AI_V4_Release',
    'VSAValorExtension',
    'WooCommerse'
]

# Project grouping for cleaner visualization
PROJECT_GROUPS = {
    'InHouse Core': ['In_House_SQL', 'In_House_Print', 'In_House_V2', 'In_House_FRED'],
    'InHouse Versions': ['V7_In_House', 'V8_In_House', 'SQL_Data_AI_UI_v5'],
    'G_Folder Snapshots': ['G_Folder Oct 8th', 'G_Folder Oct 10th', 'G_Folder Oct 14th', 
                            'G_Folder Oct 15th', 'G_Folder Oct 17th'],
    'AI Agents': ['AI_agents'],
    'MustCare Suite': ['V7_MustCare', 'MustCare ValorAISynergySuite', 'MustCare_V2_Anthropic'],
    'VALOR AI': ['VALOR_AI_SIDEBAR_DOWNLOADER', 'VSA_Valor_AI_V4_Release', 'VSAValorExtension',
                 'Valor Extension Back Ups'],
    'Utilities': ['Bonus Calculator', 'Label_Printer', 'Inv-Stock', 'HTML-PDF', 'MP3 Transcription'],
    'Assets': ['Fontawesome', 'READY_TO_SEND', 'WooCommerse']
}

def get_project_group(project):
    """Get the group for a project"""
    for group, projects in PROJECT_GROUPS.items():
        if project in projects:
            return group
    return 'Other'

def scan_all_projects():
    """Scan all projects and return daily file counts"""
    base_path = r"C:\Users\gpoli\GIT"
    
    print("Scanning all projects...")
    
    files_by_date = defaultdict(lambda: defaultdict(int))
    total_files = 0
    
    for project in MAIN_PROJECTS:
        project_path = os.path.join(base_path, project)
        
        if not os.path.exists(project_path):
            continue
        
        print(f"  {project}...", end='', flush=True)
        count = 0
        
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 
                                                          '.vscode', 'venv', 'env', 'archive',
                                                          'dist', 'build', '.pytest_cache']]
                
                for filename in files:
                    if filename.startswith('.'):
                        continue
                    
                    filepath = os.path.join(root, filename)
                    try:
                        stats = os.stat(filepath)
                        created = datetime.fromtimestamp(stats.st_ctime)
                        date_str = created.strftime('%Y-%m-%d')
                        
                        files_by_date[date_str][project] += 1
                        count += 1
                        total_files += 1
                    except:
                        continue
            
            print(f" {count:,}")
        except Exception as e:
            print(f" ERROR: {e}")
    
    print(f"\nTotal files: {total_files:,}")
    return files_by_date

def create_master_timeline_html(files_by_date):
    """Create comprehensive master timeline HTML"""
    
    # Sort dates
    dates = sorted(files_by_date.keys())
    
    # Get all unique projects
    all_projects = set()
    for date_data in files_by_date.values():
        all_projects.update(date_data.keys())
    
    # Group projects
    grouped_projects = defaultdict(list)
    for project in sorted(all_projects):
        group = get_project_group(project)
        grouped_projects[group].append(project)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Project Timeline - All Work (July 22 - Nov 8, 2025)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .timeline-container {{
            padding: 30px;
            display: flex;
            gap: 20px;
        }}
        
        .sidebar {{
            width: 250px;
            flex-shrink: 0;
            overflow-y: auto;
            max-height: 600px;
            border-right: 2px solid #ecf0f1;
            padding-right: 20px;
        }}
        
        .project-group {{
            margin-bottom: 20px;
        }}
        
        .group-title {{
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
            border-bottom: 2px solid #3498db;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .project-item {{
            padding: 8px 0;
            font-size: 0.85em;
            color: #555;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .project-color {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
            display: inline-block;
        }}
        
        .timeline {{
            flex: 1;
            overflow-x: auto;
            overflow-y: auto;
            max-height: 600px;
        }}
        
        .timeline-header {{
            display: flex;
            margin-bottom: 10px;
            font-weight: bold;
            font-size: 0.85em;
            color: #2c3e50;
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .date-column {{
            width: 120px;
            flex-shrink: 0;
        }}
        
        .bars-column {{
            flex: 1;
            min-width: 800px;
        }}
        
        .timeline-row {{
            display: flex;
            margin-bottom: 2px;
            align-items: center;
            height: 30px;
        }}
        
        .timeline-row:hover {{
            background: #f8f9fa;
        }}
        
        .date-label {{
            width: 120px;
            flex-shrink: 0;
            font-size: 0.85em;
            color: #555;
            padding-right: 10px;
        }}
        
        .date-label .day {{
            color: #999;
            font-size: 0.8em;
        }}
        
        .bars-container {{
            flex: 1;
            display: flex;
            gap: 2px;
            min-width: 800px;
        }}
        
        .project-bar {{
            height: 24px;
            border-radius: 4px;
            position: relative;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .project-bar:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .project-bar .tooltip {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.75em;
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1000;
            margin-bottom: 5px;
        }}
        
        .project-bar:hover .tooltip {{
            opacity: 1;
        }}
        
        .legend {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-top: 2px solid #ecf0f1;
        }}
        
        .legend-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 0.85em;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Master Project Timeline</h1>
            <div class="subtitle">Complete Work History: July 22 - November 8, 2025</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="value">{sum(len(files_by_date[d]) for d in dates):,}</div>
                <div class="label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(dates)}</div>
                <div class="label">Work Days</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(all_projects)}</div>
                <div class="label">Projects</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(grouped_projects)}</div>
                <div class="label">Project Groups</div>
            </div>
        </div>
        
        <div class="timeline-container">
            <div class="sidebar">"""
    
    # Project colors
    colors = {
        'InHouse Core': '#3498db',
        'InHouse Versions': '#2980b9',
        'G_Folder Snapshots': '#9b59b6',
        'AI Agents': '#e74c3c',
        'MustCare Suite': '#1abc9c',
        'VALOR AI': '#f39c12',
        'Utilities': '#16a085',
        'Assets': '#95a5a6'
    }
    
    # Sidebar with project groups
    for group in sorted(grouped_projects.keys()):
        projects = grouped_projects[group]
        color = colors.get(group, '#95a5a6')
        
        html += f"""
                <div class="project-group">
                    <div class="group-title">{group}</div>"""
        
        for project in projects:
            # Count total files for this project
            total = sum(files_by_date[d].get(project, 0) for d in dates)
            html += f"""
                    <div class="project-item">
                        <span><span class="project-color" style="background: {color}"></span>{project}</span>
                        <span style="color: #999;">{total:,}</span>
                    </div>"""
        
        html += """
                </div>"""
    
    html += """
            </div>
            
            <div class="timeline">
                <div class="timeline-header">
                    <div class="date-column">Date</div>
                    <div class="bars-column">Activity</div>
                </div>"""
    
    # Timeline rows
    for date_str in dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%a')
        display_date = date_obj.strftime('%b %d')
        
        date_projects = files_by_date[date_str]
        total_files = sum(date_projects.values())
        
        html += f"""
                <div class="timeline-row">
                    <div class="date-label">
                        {display_date} <span class="day">{day_name}</span>
                    </div>
                    <div class="bars-container">"""
        
        # Create bars for each project
        for project, count in sorted(date_projects.items(), key=lambda x: x[1], reverse=True):
            group = get_project_group(project)
            color = colors.get(group, '#95a5a6')
            
            # Width based on file count (logarithmic scale for better visualization)
            import math
            width = min(100, max(20, math.log(count + 1) * 30))
            
            html += f"""
                        <div class="project-bar" style="width: {width}px; background: {color};">
                            <div class="tooltip">{project}<br>{count:,} files</div>
                        </div>"""
        
        html += f"""
                    </div>
                </div>"""
    
    html += """
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-title">Project Groups</div>
            <div class="legend-grid">"""
    
    for group, color in sorted(colors.items()):
        project_count = len(grouped_projects.get(group, []))
        html += f"""
                <div class="legend-item">
                    <div class="legend-color" style="background: {color}"></div>
                    <span>{group} ({project_count})</span>
                </div>"""
    
    html += """
            </div>
        </div>
    </div>
    
    <script>
        // Synchronize scrolling
        const sidebar = document.querySelector('.sidebar');
        const timeline = document.querySelector('.timeline');
        
        timeline.addEventListener('scroll', () => {
            sidebar.scrollTop = timeline.scrollTop;
        });
    </script>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    print("Creating master timeline...")
    
    # Scan all projects
    files_by_date = scan_all_projects()
    
    # Create HTML
    html = create_master_timeline_html(files_by_date)
    
    # Save
    output_file = 'master_timeline_all_projects.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nDONE - Master timeline saved to: {output_file}")
    print(f"Total dates with activity: {len(files_by_date)}")
    print(f"\nOpen {output_file} in your browser to view the complete timeline")
