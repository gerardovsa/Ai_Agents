"""
Accurate File Activity Analysis Based on Filesystem Metadata
Analyzes actual file creation and modification dates from filesystem
NOT from git commits - this shows REAL work activity
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import time

def get_file_metadata(filepath):
    """Get accurate file metadata from filesystem"""
    try:
        stat = os.stat(filepath)
        return {
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'size': stat.st_size,
            'accessed': datetime.fromtimestamp(stat.st_atime)
        }
    except Exception as e:
        return None

def scan_directory_metadata(root_path, exclude_dirs=None):
    """Scan directory and get metadata for all files"""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', 
                       'venv', 'env', '.pytest_cache', '.mypy_cache',
                       'dist', 'build', '.eggs', '*.egg-info'}
    
    files_metadata = {}
    total_size = 0
    
    print(f"Scanning: {root_path}")
    file_count = 0
    
    for root, dirs, files in os.walk(root_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for filename in files:
            # Skip hidden files
            if filename.startswith('.'):
                continue
                
            filepath = os.path.join(root, filename)
            metadata = get_file_metadata(filepath)
            
            if metadata:
                rel_path = os.path.relpath(filepath, root_path)
                files_metadata[rel_path] = metadata
                total_size += metadata['size']
                file_count += 1
                
                if file_count % 1000 == 0:
                    print(f"  Processed {file_count} files...")
    
    print(f"  Total files found: {file_count}")
    print(f"  Total size: {total_size / (1024*1024):.2f} MB")
    
    return files_metadata, total_size

def group_by_date(files_metadata, date_type='created'):
    """Group files by date (created or modified)"""
    by_date = defaultdict(list)
    
    for filepath, metadata in files_metadata.items():
        if date_type in metadata:
            date = metadata[date_type].strftime('%Y-%m-%d')
            by_date[date].append({
                'path': filepath,
                'size': metadata['size'],
                'time': metadata[date_type].strftime('%H:%M:%S')
            })
    
    return dict(by_date)

def group_by_hour(files_metadata, date_type='created'):
    """Group files by hour for detailed daily breakdown"""
    by_datetime = defaultdict(list)
    
    for filepath, metadata in files_metadata.items():
        if date_type in metadata:
            datetime_key = metadata[date_type].strftime('%Y-%m-%d %H:00')
            by_datetime[datetime_key].append({
                'path': filepath,
                'size': metadata['size'],
                'time': metadata[date_type].strftime('%H:%M:%S')
            })
    
    return dict(by_datetime)

def analyze_file_types(files_metadata):
    """Analyze file types and extensions"""
    extensions = defaultdict(lambda: {'count': 0, 'size': 0})
    
    for filepath, metadata in files_metadata.items():
        ext = os.path.splitext(filepath)[1].lower() or 'no_extension'
        extensions[ext]['count'] += 1
        extensions[ext]['size'] += metadata['size']
    
    return dict(extensions)

def generate_statistics(files_metadata, created_by_date, modified_by_date):
    """Generate comprehensive statistics"""
    stats = {
        'total_files': len(files_metadata),
        'total_size_mb': sum(m['size'] for m in files_metadata.values()) / (1024*1024),
        'date_range': {
            'created': {
                'first': min(created_by_date.keys()) if created_by_date else 'N/A',
                'last': max(created_by_date.keys()) if created_by_date else 'N/A',
                'days': len(created_by_date)
            },
            'modified': {
                'first': min(modified_by_date.keys()) if modified_by_date else 'N/A',
                'last': max(modified_by_date.keys()) if modified_by_date else 'N/A',
                'days': len(modified_by_date)
            }
        },
        'busiest_days': {
            'created': max(created_by_date.items(), key=lambda x: len(x[1])) if created_by_date else ('N/A', []),
            'modified': max(modified_by_date.items(), key=lambda x: len(x[1])) if modified_by_date else ('N/A', [])
        },
        'files_per_day': {
            'created_avg': len(files_metadata) / len(created_by_date) if created_by_date else 0,
            'modified_avg': len(files_metadata) / len(modified_by_date) if modified_by_date else 0
        }
    }
    
    return stats

def generate_html_report(project_name, files_metadata, created_by_date, modified_by_date, 
                        created_by_hour, modified_by_hour, file_types, stats, output_file):
    """Generate comprehensive HTML report with hourly breakdown"""
    
    # Sort dates
    all_dates = sorted(set(list(created_by_date.keys()) + list(modified_by_date.keys())))
    created_counts = [len(created_by_date.get(date, [])) for date in all_dates]
    modified_counts = [len(modified_by_date.get(date, [])) for date in all_dates]
    
    # Get top file types
    top_extensions = sorted(file_types.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    
    # Calculate hourly data for heatmap
    hours_data = defaultdict(lambda: defaultdict(int))
    for datetime_key, files in created_by_hour.items():
        date, hour = datetime_key.split(' ')
        hour_num = int(hour.split(':')[0])
        hours_data[date][hour_num] = len(files)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{project_name} - Accurate File Activity Analysis</title>
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
            max-width: 1600px;
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
        .accuracy-notice {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
            font-weight: bold;
            text-align: center;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .stat-card h3 {{
            color: #667eea;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.85em;
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
        .heatmap-container {{
            padding: 20px;
            background: white;
            border-radius: 15px;
            margin-bottom: 30px;
        }}
        .heatmap-grid {{
            display: grid;
            grid-template-columns: 80px repeat(24, 1fr);
            gap: 2px;
            font-size: 0.75em;
        }}
        .heatmap-cell {{
            padding: 8px;
            text-align: center;
            border-radius: 3px;
            min-width: 30px;
        }}
        .heatmap-label {{
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
        }}
        .heatmap-hour {{
            font-weight: bold;
            font-size: 0.7em;
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
            cursor: pointer;
        }}
        .date-header:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%);
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
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }}
        .file-list.expanded {{
            display: block;
        }}
        .file-item {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            display: grid;
            grid-template-columns: 80px 1fr 100px;
            gap: 15px;
            font-size: 0.9em;
        }}
        .file-time {{
            color: #667eea;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }}
        .file-path {{
            color: #555;
            font-family: 'Courier New', monospace;
        }}
        .file-size {{
            color: #999;
            text-align: right;
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
        .file-types-section {{
            padding: 40px;
            background: white;
        }}
        .file-types-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }}
        .file-type-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #764ba2;
        }}
        .file-type-ext {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #764ba2;
            font-size: 1.1em;
        }}
        .file-type-count {{
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project_name}</h1>
            <div class="subtitle">Accurate File Activity Analysis (Filesystem Metadata)</div>
        </div>
        
        <div class="accuracy-notice">
            This analysis uses ACTUAL FILE TIMESTAMPS from the filesystem, NOT git commits.
            This shows your REAL work activity based on when files were created and modified.
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Files</h3>
                <div class="value">{stats['total_files']:,}</div>
                <div class="label">Tracked</div>
            </div>
            <div class="stat-card">
                <h3>Total Size</h3>
                <div class="value">{stats['total_size_mb']:.1f} MB</div>
                <div class="label">Disk space</div>
            </div>
            <div class="stat-card">
                <h3>Created Range</h3>
                <div class="value" style="font-size: 1em;">{stats['date_range']['created']['first']}</div>
                <div class="label">to {stats['date_range']['created']['last']}</div>
            </div>
            <div class="stat-card">
                <h3>Active Days</h3>
                <div class="value">{stats['date_range']['created']['days']}</div>
                <div class="label">Creation days</div>
            </div>
            <div class="stat-card">
                <h3>Busiest Create Day</h3>
                <div class="value">{len(stats['busiest_days']['created'][1])}</div>
                <div class="label">{stats['busiest_days']['created'][0]}</div>
            </div>
            <div class="stat-card">
                <h3>Busiest Modify Day</h3>
                <div class="value">{len(stats['busiest_days']['modified'][1])}</div>
                <div class="label">{stats['busiest_days']['modified'][0]}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Files/Day</h3>
                <div class="value">{stats['files_per_day']['created_avg']:.0f}</div>
                <div class="label">Created per day</div>
            </div>
            <div class="stat-card">
                <h3>Modification Days</h3>
                <div class="value">{stats['date_range']['modified']['days']}</div>
                <div class="label">Active modify days</div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-container">
                <div class="chart-title">Files Created Per Day (Real Activity)</div>
                <canvas id="createdChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Files Modified Per Day (Real Activity)</div>
                <canvas id="modifiedChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Combined Activity Timeline</div>
                <canvas id="combinedChart"></canvas>
            </div>
        </div>
        
        <div class="file-types-section">
            <div class="timeline-title">File Types Distribution</div>
            <div class="file-types-grid">
"""
    
    for ext, data in top_extensions:
        size_mb = data['size'] / (1024 * 1024)
        html += f"""
                <div class="file-type-card">
                    <div class="file-type-ext">{ext}</div>
                    <div class="file-type-count">{data['count']:,} files ({size_mb:.2f} MB)</div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="section-tabs">
            <button class="tab-button active" onclick="switchTab('created')">Created Files by Date</button>
            <button class="tab-button" onclick="switchTab('modified')">Modified Files by Date</button>
            <button class="tab-button" onclick="switchTab('hourly')">Hourly Breakdown</button>
        </div>
        
        <div class="timeline-section">
            <div id="created-timeline" class="tab-content active">
                <div class="timeline-title">Files Created by Date</div>
"""
    
    # Add created files timeline with time details
    for date in sorted(created_by_date.keys(), reverse=True):
        files = sorted(created_by_date[date], key=lambda x: x['time'])
        total_size = sum(f['size'] for f in files) / (1024 * 1024)
        html += f"""
                <div class="date-block">
                    <div class="date-header" onclick="toggleFiles(this)">
                        <span class="date">{date}</span>
                        <span class="count">{len(files)} files ({total_size:.2f} MB)</span>
                    </div>
                    <div class="file-list">
"""
        for file_info in files:
            size_kb = file_info['size'] / 1024
            html += f"""
                        <div class="file-item">
                            <span class="file-time">{file_info['time']}</span>
                            <span class="file-path">{file_info['path']}</span>
                            <span class="file-size">{size_kb:.1f} KB</span>
                        </div>
"""
        html += """                    </div>
                </div>
"""
    
    html += """            </div>
            
            <div id="modified-timeline" class="tab-content">
                <div class="timeline-title">Files Modified by Date</div>
"""
    
    # Add modified files timeline
    for date in sorted(modified_by_date.keys(), reverse=True):
        files = sorted(modified_by_date[date], key=lambda x: x['time'])
        total_size = sum(f['size'] for f in files) / (1024 * 1024)
        html += f"""
                <div class="date-block">
                    <div class="date-header" onclick="toggleFiles(this)">
                        <span class="date">{date}</span>
                        <span class="count">{len(files)} files ({total_size:.2f} MB)</span>
                    </div>
                    <div class="file-list">
"""
        for file_info in files:
            size_kb = file_info['size'] / 1024
            html += f"""
                        <div class="file-item">
                            <span class="file-time">{file_info['time']}</span>
                            <span class="file-path">{file_info['path']}</span>
                            <span class="file-size">{size_kb:.1f} KB</span>
                        </div>
"""
        html += """                    </div>
                </div>
"""
    
    html += """            </div>
            
            <div id="hourly-timeline" class="tab-content">
                <div class="timeline-title">Hourly Activity Breakdown</div>
"""
    
    # Add hourly breakdown
    for date in sorted(created_by_hour.keys(), key=lambda x: x.split()[0], reverse=True):
        if date.split()[0] != date.split()[0]:  # Group by date
            continue
        current_date = date.split()[0]
        hourly_data = [(dt, files) for dt, files in created_by_hour.items() if dt.startswith(current_date)]
        
        if hourly_data:
            total_files = sum(len(files) for _, files in hourly_data)
            html += f"""
                <div class="date-block">
                    <div class="date-header" onclick="toggleFiles(this)">
                        <span class="date">{current_date}</span>
                        <span class="count">{total_files} files across {len(hourly_data)} hours</span>
                    </div>
                    <div class="file-list">
"""
            for datetime_key, files in sorted(hourly_data):
                hour = datetime_key.split()[1]
                html += f"""
                        <div style="margin-bottom: 15px;">
                            <div style="font-weight: bold; color: #667eea; margin-bottom: 5px;">{hour} - {len(files)} files</div>
"""
                for file_info in sorted(files, key=lambda x: x['time'])[:20]:  # Show first 20
                    html += f"""
                            <div class="file-item">
                                <span class="file-time">{file_info['time']}</span>
                                <span class="file-path">{file_info['path']}</span>
                                <span class="file-size">{file_info['size']/1024:.1f} KB</span>
                            </div>
"""
                if len(files) > 20:
                    html += f'                            <div style="color: #999; padding: 5px 0;">... and {len(files)-20} more files</div>\n'
                html += """                        </div>
"""
            html += """                    </div>
                </div>
"""
    
    html += f"""            </div>
        </div>
    </div>
    
    <script>
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
                        ticks: {{ precision: 0 }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Files: ' + context.parsed.y.toLocaleString();
                            }}
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
                        ticks: {{ precision: 0 }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Files: ' + context.parsed.y.toLocaleString();
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Combined chart
        new Chart(document.getElementById('combinedChart'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'Created',
                        data: createdCounts,
                        backgroundColor: 'rgba(102, 126, 234, 0.5)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }},
                    {{
                        label: 'Modified',
                        data: modifiedCounts,
                        backgroundColor: 'rgba(118, 75, 162, 0.5)',
                        borderColor: 'rgba(118, 75, 162, 1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ precision: 0 }}
                    }}
                }},
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' files';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        function switchTab(tab) {{
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-timeline').classList.add('active');
        }}
        
        function toggleFiles(header) {{
            const fileList = header.nextElementSibling;
            fileList.classList.toggle('expanded');
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
            'output': 'ai_agents_accurate_timeline.html',
            'json_output': 'ai_agents_accurate_timeline.json'
        },
        {
            'name': 'In_House_SQL (G_Folder)',
            'path': r'c:\Users\gpoli\GIT\In_House_SQL',
            'output': 'g_folder_accurate_timeline.html',
            'json_output': 'g_folder_accurate_timeline.json'
        }
    ]
    
    for project in projects:
        print(f"\n{'='*70}")
        print(f"ANALYZING: {project['name']}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        # Scan directory for file metadata
        files_metadata, total_size = scan_directory_metadata(project['path'])
        
        print(f"\nGrouping by dates...")
        created_by_date = group_by_date(files_metadata, 'created')
        modified_by_date = group_by_date(files_metadata, 'modified')
        
        print(f"Grouping by hours...")
        created_by_hour = group_by_hour(files_metadata, 'created')
        modified_by_hour = group_by_hour(files_metadata, 'modified')
        
        print(f"Analyzing file types...")
        file_types = analyze_file_types(files_metadata)
        
        print(f"Generating statistics...")
        stats = generate_statistics(files_metadata, created_by_date, modified_by_date)
        
        # Generate HTML report
        output_path = os.path.join(project['path'], project['output'])
        print(f"Generating HTML report...")
        generate_html_report(
            project['name'],
            files_metadata,
            created_by_date,
            modified_by_date,
            created_by_hour,
            modified_by_hour,
            file_types,
            stats,
            output_path
        )
        
        # Save detailed JSON
        json_path = os.path.join(project['path'], project['json_output'])
        print(f"Saving JSON data...")
        
        # Convert datetime objects to strings for JSON
        files_metadata_json = {}
        for filepath, metadata in files_metadata.items():
            files_metadata_json[filepath] = {
                'created': metadata['created'].isoformat(),
                'modified': metadata['modified'].isoformat(),
                'size': metadata['size'],
                'accessed': metadata['accessed'].isoformat()
            }
        
        json_data = {
            'project': project['name'],
            'analysis_date': datetime.now().isoformat(),
            'statistics': stats,
            'created_by_date': {date: len(files) for date, files in created_by_date.items()},
            'modified_by_date': {date: len(files) for date, files in modified_by_date.items()},
            'file_types': file_types,
            'files_metadata': files_metadata_json
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"COMPLETED: {project['name']}")
        print(f"{'='*70}")
        print(f"Total files analyzed: {len(files_metadata):,}")
        print(f"Total size: {total_size / (1024*1024):.2f} MB")
        print(f"Active creation days: {len(created_by_date)}")
        print(f"Active modification days: {len(modified_by_date)}")
        print(f"Processing time: {elapsed:.2f} seconds")
        print(f"\nHTML Report: {output_path}")
        print(f"JSON Data: {json_path}")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
