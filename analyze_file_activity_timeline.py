"""
File Activity Timeline Analysis
Generates detailed timeline of file creation/modification activity with visualizations
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import subprocess

def get_git_file_history(repo_path):
    """Get file creation and modification dates from git history"""
    try:
        os.chdir(repo_path)
        
        # Get all files with their creation and last modification dates
        cmd = [
            'git', 'log', '--all', '--pretty=format:%aI|%s', '--name-only', '--diff-filter=A'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"Git command failed: {result.stderr}")
            return {}
        
        files_data = {}
        current_date = None
        
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue
            
            if '|' in line:
                current_date = line.split('|')[0]
            elif current_date and line.strip():
                filename = line.strip()
                if filename not in files_data:
                    files_data[filename] = {
                        'created': current_date,
                        'path': filename
                    }
        
        # Get last modification dates
        cmd_mod = [
            'git', 'log', '--all', '--pretty=format:%aI', '--name-only'
        ]
        
        result_mod = subprocess.run(cmd_mod, capture_output=True, text=True, encoding='utf-8')
        
        if result_mod.returncode == 0:
            current_date = None
            for line in result_mod.stdout.split('\n'):
                if not line.strip():
                    continue
                
                # Check if line is a date
                if line.count('-') >= 2 and line.count(':') >= 2:
                    current_date = line
                elif current_date and line.strip():
                    filename = line.strip()
                    if filename in files_data:
                        if 'modified' not in files_data[filename]:
                            files_data[filename]['modified'] = current_date
        
        return files_data
        
    except Exception as e:
        print(f"Error getting git history: {e}")
        return {}

def get_filesystem_dates(repo_path):
    """Get file dates from filesystem (fallback)"""
    files_data = {}
    
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden and system directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                stat = os.stat(filepath)
                rel_path = os.path.relpath(filepath, repo_path)
                
                files_data[rel_path] = {
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'path': rel_path,
                    'size': stat.st_size
                }
            except Exception as e:
                continue
    
    return files_data

def analyze_activity_by_date(files_data):
    """Analyze file activity grouped by date"""
    created_by_date = defaultdict(list)
    modified_by_date = defaultdict(list)
    
    for filepath, data in files_data.items():
        if 'created' in data:
            try:
                date = data['created'][:10]  # YYYY-MM-DD
                created_by_date[date].append(filepath)
            except:
                pass
        
        if 'modified' in data:
            try:
                date = data['modified'][:10]  # YYYY-MM-DD
                modified_by_date[date].append(filepath)
            except:
                pass
    
    return dict(created_by_date), dict(modified_by_date)

def generate_html_report(project_name, files_data, created_by_date, modified_by_date, output_file):
    """Generate HTML report with interactive charts"""
    
    # Sort dates
    all_dates = sorted(set(list(created_by_date.keys()) + list(modified_by_date.keys())))
    
    # Prepare data for charts
    created_counts = [len(created_by_date.get(date, [])) for date in all_dates]
    modified_counts = [len(modified_by_date.get(date, [])) for date in all_dates]
    
    # Calculate statistics
    total_files = len(files_data)
    date_range = f"{all_dates[0]} to {all_dates[-1]}" if all_dates else "N/A"
    busiest_create_date = max(created_by_date.items(), key=lambda x: len(x[1])) if created_by_date else ("N/A", [])
    busiest_modify_date = max(modified_by_date.items(), key=lambda x: len(x[1])) if modified_by_date else ("N/A", [])
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{project_name} - File Activity Timeline</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            max-width: 1400px;
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
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .stat-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .chart-section {{
            padding: 40px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 40px;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        .timeline-section {{
            padding: 40px;
            background: #f8f9fa;
        }}
        .timeline-title {{
            font-size: 2em;
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }}
        .date-block {{
            background: white;
            margin-bottom: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .date-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .date-header .date {{
            font-size: 1.2em;
        }}
        .date-header .count {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
        }}
        .file-list {{
            padding: 20px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .file-item {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            color: #555;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .section-tabs {{
            display: flex;
            background: #667eea;
            justify-content: center;
            gap: 10px;
            padding: 10px;
        }}
        .tab-button {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }}
        .tab-button:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .tab-button.active {{
            background: white;
            color: #667eea;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project_name}</h1>
            <div class="subtitle">File Activity Timeline Analysis</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Files Tracked</h3>
                <div class="value">{total_files:,}</div>
                <div class="label">In repository</div>
            </div>
            <div class="stat-card">
                <h3>Date Range</h3>
                <div class="value" style="font-size: 1.2em;">{date_range}</div>
                <div class="label">Activity period</div>
            </div>
            <div class="stat-card">
                <h3>Busiest Create Day</h3>
                <div class="value">{len(busiest_create_date[1])}</div>
                <div class="label">{busiest_create_date[0]}</div>
            </div>
            <div class="stat-card">
                <h3>Busiest Modify Day</h3>
                <div class="value">{len(busiest_modify_date[1])}</div>
                <div class="label">{busiest_modify_date[0]}</div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-container">
                <div class="chart-title">Files Created Per Day</div>
                <canvas id="createdChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Files Modified Per Day</div>
                <canvas id="modifiedChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Combined Activity (Stacked)</div>
                <canvas id="combinedChart"></canvas>
            </div>
        </div>
        
        <div class="section-tabs">
            <button class="tab-button active" onclick="switchTab('created')">Created Files</button>
            <button class="tab-button" onclick="switchTab('modified')">Modified Files</button>
        </div>
        
        <div class="timeline-section">
            <div id="created-timeline" class="tab-content active">
                <div class="timeline-title">Files Created by Date</div>
"""
    
    # Add created files timeline
    for date in sorted(created_by_date.keys(), reverse=True):
        files = created_by_date[date]
        html += f"""
                <div class="date-block">
                    <div class="date-header">
                        <span class="date">{date}</span>
                        <span class="count">{len(files)} files</span>
                    </div>
                    <div class="file-list">
"""
        for filepath in sorted(files):
            html += f'                        <div class="file-item">{filepath}</div>\n'
        
        html += """                    </div>
                </div>
"""
    
    html += """            </div>
            
            <div id="modified-timeline" class="tab-content">
                <div class="timeline-title">Files Modified by Date</div>
"""
    
    # Add modified files timeline
    for date in sorted(modified_by_date.keys(), reverse=True):
        files = modified_by_date[date]
        html += f"""
                <div class="date-block">
                    <div class="date-header">
                        <span class="date">{date}</span>
                        <span class="count">{len(files)} files</span>
                    </div>
                    <div class="file-list">
"""
        for filepath in sorted(files):
            html += f'                        <div class="file-item">{filepath}</div>\n'
        
        html += """                    </div>
                </div>
"""
    
    html += f"""            </div>
        </div>
    </div>
    
    <script>
        // Chart.js configuration
        const dates = {json.dumps(all_dates)};
        const createdCounts = {json.dumps(created_counts)};
        const modifiedCounts = {json.dumps(modified_counts)};
        
        // Created files chart
        new Chart(document.getElementById('createdChart'), {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Files Created',
                    data: createdCounts,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }}
                }}
            }}
        }});
        
        // Modified files chart
        new Chart(document.getElementById('modifiedChart'), {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Files Modified',
                    data: modifiedCounts,
                    backgroundColor: 'rgba(118, 75, 162, 0.8)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }}
                }}
            }}
        }});
        
        // Combined stacked chart
        new Chart(document.getElementById('combinedChart'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'Files Created',
                        data: createdCounts,
                        backgroundColor: 'rgba(102, 126, 234, 0.5)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2,
                        fill: true
                    }},
                    {{
                        label: 'Files Modified',
                        data: modifiedCounts,
                        backgroundColor: 'rgba(118, 75, 162, 0.5)',
                        borderColor: 'rgba(118, 75, 162, 1)',
                        borderWidth: 2,
                        fill: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            precision: 0
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'index',
                    intersect: false
                }}
            }}
        }});
        
        // Tab switching
        function switchTab(tab) {{
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-timeline').classList.add('active');
        }}
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    projects = [
        {
            'name': 'AI_agents',
            'path': r'c:\Users\gpoli\GIT\AI_agents',
            'output': 'ai_agents_timeline.html'
        },
        {
            'name': 'In_House_SQL (G_Folder)',
            'path': r'c:\Users\gpoli\GIT\In_House_SQL',
            'output': 'g_folder_timeline.html'
        }
    ]
    
    for project in projects:
        print(f"\n{'='*60}")
        print(f"Analyzing: {project['name']}")
        print(f"{'='*60}")
        
        # Try git history first
        print("Getting git history...")
        files_data = get_git_file_history(project['path'])
        
        if not files_data:
            print("Git history not available, using filesystem dates...")
            files_data = get_filesystem_dates(project['path'])
        
        print(f"Found {len(files_data)} files")
        
        # Analyze activity
        created_by_date, modified_by_date = analyze_activity_by_date(files_data)
        
        print(f"Files created on {len(created_by_date)} different dates")
        print(f"Files modified on {len(modified_by_date)} different dates")
        
        # Generate report
        output_path = os.path.join(project['path'], project['output'])
        generate_html_report(
            project['name'],
            files_data,
            created_by_date,
            modified_by_date,
            output_path
        )
        
        print(f"\nReport generated: {output_path}")
        
        # Save JSON data
        json_path = os.path.join(project['path'], project['output'].replace('.html', '.json'))
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'project': project['name'],
                'total_files': len(files_data),
                'created_by_date': {k: len(v) for k, v in created_by_date.items()},
                'modified_by_date': {k: len(v) for k, v in modified_by_date.items()},
                'files_detail': files_data
            }, f, indent=2)
        
        print(f"JSON data saved: {json_path}")

if __name__ == '__main__':
    main()
