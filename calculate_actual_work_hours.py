"""
Calculate ACTUAL Work Hours from File Metadata
Analyzes hour-by-hour file creation to estimate real working hours
"""

import os
import json
from datetime import datetime, timedelta
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
            'size': stat.st_size
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
    
    print(f"Scanning: {root_path}")
    file_count = 0
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for filename in files:
            if filename.startswith('.'):
                continue
                
            filepath = os.path.join(root, filename)
            metadata = get_file_metadata(filepath)
            
            if metadata:
                rel_path = os.path.relpath(filepath, root_path)
                files_metadata[rel_path] = metadata
                file_count += 1
                
                if file_count % 1000 == 0:
                    print(f"  Processed {file_count} files...")
    
    print(f"  Total: {file_count} files")
    return files_metadata

def analyze_hourly_activity(files_metadata, date_type='created'):
    """Analyze activity by hour to calculate real work hours"""
    hourly_activity = defaultdict(lambda: {'files': [], 'count': 0})
    daily_hours = defaultdict(set)  # Track which hours had activity per day
    
    for filepath, metadata in files_metadata.items():
        if date_type in metadata:
            dt = metadata[date_type]
            date_key = dt.strftime('%Y-%m-%d')
            hour_key = dt.strftime('%Y-%m-%d %H:00')
            
            hourly_activity[hour_key]['files'].append(filepath)
            hourly_activity[hour_key]['count'] += 1
            
            # Track which hour of day had activity
            hour_of_day = dt.hour
            daily_hours[date_key].add(hour_of_day)
    
    return dict(hourly_activity), dict(daily_hours)

def calculate_work_hours(daily_hours):
    """
    Calculate actual work hours based on active hours per day
    Assumes: If files created in an hour = you worked that hour
    """
    work_stats = {}
    total_hours = 0
    
    for date, active_hours in sorted(daily_hours.items()):
        hours_worked = len(active_hours)
        total_hours += hours_worked
        
        # Determine work session type
        if hours_worked >= 16:
            session_type = "MARATHON SESSION (16+ hours)"
        elif hours_worked >= 12:
            session_type = "LONG DAY (12-16 hours)"
        elif hours_worked >= 8:
            session_type = "FULL DAY (8-12 hours)"
        elif hours_worked >= 4:
            session_type = "HALF DAY (4-8 hours)"
        else:
            session_type = "SHORT SESSION (< 4 hours)"
        
        # Get hour range
        hour_list = sorted(list(active_hours))
        start_hour = hour_list[0]
        end_hour = hour_list[-1]
        
        work_stats[date] = {
            'hours': hours_worked,
            'type': session_type,
            'start_hour': start_hour,
            'end_hour': end_hour,
            'hour_range': f"{start_hour:02d}:00 - {end_hour:02d}:59",
            'active_hours': sorted(list(active_hours))
        }
    
    return work_stats, total_hours

def analyze_work_patterns(work_stats):
    """Analyze work patterns to show intensity"""
    patterns = {
        'marathon_days': [],      # 16+ hours
        'long_days': [],          # 12-16 hours
        'full_days': [],          # 8-12 hours
        'half_days': [],          # 4-8 hours
        'short_sessions': [],     # < 4 hours
        'consecutive_days': 0,
        'weekend_work': 0,
        'late_night_hours': 0,    # 11pm - 5am
        'early_morning_hours': 0, # 5am - 9am
        'business_hours': 0,      # 9am - 5pm
        'evening_hours': 0        # 5pm - 11pm
    }
    
    for date, stats in sorted(work_stats.items()):
        hours = stats['hours']
        
        if hours >= 16:
            patterns['marathon_days'].append((date, hours))
        elif hours >= 12:
            patterns['long_days'].append((date, hours))
        elif hours >= 8:
            patterns['full_days'].append((date, hours))
        elif hours >= 4:
            patterns['half_days'].append((date, hours))
        else:
            patterns['short_sessions'].append((date, hours))
        
        # Check for weekend work
        dt = datetime.strptime(date, '%Y-%m-%d')
        if dt.weekday() >= 5:  # Saturday or Sunday
            patterns['weekend_work'] += 1
        
        # Analyze time of day
        for hour in stats['active_hours']:
            if 23 <= hour or hour < 5:
                patterns['late_night_hours'] += 1
            elif 5 <= hour < 9:
                patterns['early_morning_hours'] += 1
            elif 9 <= hour < 17:
                patterns['business_hours'] += 1
            else:  # 17-23
                patterns['evening_hours'] += 1
    
    # Calculate consecutive days
    dates = sorted(work_stats.keys())
    if dates:
        max_consecutive = 1
        current_consecutive = 1
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i-1], '%Y-%m-%d')
            curr_date = datetime.strptime(dates[i], '%Y-%m-%d')
            if (curr_date - prev_date).days == 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        patterns['consecutive_days'] = max_consecutive
    
    return patterns

def generate_detailed_report(project_name, files_metadata, work_stats, patterns, 
                           total_hours, output_file):
    """Generate detailed HTML report with hour calculations"""
    
    # Sort work stats by date
    sorted_stats = sorted(work_stats.items(), reverse=True)
    
    # Calculate cumulative hours
    cumulative = []
    running_total = 0
    for date, stats in sorted(work_stats.items()):
        running_total += stats['hours']
        cumulative.append((date, running_total))
    
    # Prepare chart data
    dates = [date for date, _ in sorted(work_stats.items())]
    hours = [stats['hours'] for _, stats in sorted(work_stats.items())]
    cumulative_hours = [total for _, total in sorted(cumulative)]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{project_name} - Actual Work Hours Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.95;
        }}
        .total-hours {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px;
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .total-hours .label {{
            font-size: 0.4em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #1e3c72;
        }}
        .stat-card.marathon {{
            border-left-color: #f5576c;
        }}
        .stat-card.long {{
            border-left-color: #f093fb;
        }}
        .stat-card.full {{
            border-left-color: #4facfe;
        }}
        .stat-card h3 {{
            color: #1e3c72;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            font-size: 2em;
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
            height: 450px;
            margin-bottom: 40px;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 1.6em;
            color: #1e3c72;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }}
        .timeline-section {{
            padding: 40px;
            background: #f8f9fa;
        }}
        .timeline-title {{
            font-size: 2em;
            color: #1e3c72;
            margin-bottom: 30px;
            text-align: center;
            font-weight: bold;
        }}
        .day-block {{
            background: white;
            margin-bottom: 15px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        }}
        .day-header {{
            padding: 20px 25px;
            font-weight: bold;
            display: grid;
            grid-template-columns: 120px 1fr 150px 200px;
            gap: 20px;
            align-items: center;
            color: white;
        }}
        .day-header.marathon {{
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        }}
        .day-header.long {{
            background: linear-gradient(135deg, #f093fb 0%, #4facfe 100%);
        }}
        .day-header.full {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .day-header.half {{
            background: linear-gradient(135deg, #00f2fe 0%, #43e97b 100%);
        }}
        .day-header.short {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            color: #333;
        }}
        .day-date {{
            font-size: 1.1em;
        }}
        .day-type {{
            font-size: 0.9em;
            opacity: 0.95;
        }}
        .day-hours {{
            font-size: 1.5em;
            text-align: right;
        }}
        .day-range {{
            font-size: 0.9em;
            text-align: right;
            opacity: 0.95;
        }}
        .hour-blocks {{
            padding: 15px 25px;
            display: flex;
            gap: 3px;
            flex-wrap: wrap;
        }}
        .hour-block {{
            width: 30px;
            height: 30px;
            background: #e0e0e0;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7em;
            font-weight: bold;
            color: #666;
        }}
        .hour-block.active {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        .hour-block.late-night {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .hour-block.early {{
            background: linear-gradient(135deg, #ffa751 0%, #ffe259 100%);
        }}
        .patterns-section {{
            padding: 40px;
            background: white;
        }}
        .patterns-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .pattern-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #1e3c72;
        }}
        .pattern-card h3 {{
            color: #1e3c72;
            margin-bottom: 15px;
        }}
        .pattern-list {{
            list-style: none;
        }}
        .pattern-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
        }}
        .pattern-list li:last-child {{
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project_name}</h1>
            <div class="subtitle">Actual Work Hours Based on File Creation Timestamps</div>
        </div>
        
        <div class="total-hours">
            <div class="label">TOTAL WORK HOURS</div>
            {total_hours:,} HOURS
        </div>
        
        <div class="stats-grid">
            <div class="stat-card marathon">
                <h3>Marathon Days (16+ hrs)</h3>
                <div class="value">{len(patterns['marathon_days'])}</div>
                <div class="label">{sum(h for _, h in patterns['marathon_days'])} total hours</div>
            </div>
            <div class="stat-card long">
                <h3>Long Days (12-16 hrs)</h3>
                <div class="value">{len(patterns['long_days'])}</div>
                <div class="label">{sum(h for _, h in patterns['long_days'])} total hours</div>
            </div>
            <div class="stat-card full">
                <h3>Full Days (8-12 hrs)</h3>
                <div class="value">{len(patterns['full_days'])}</div>
                <div class="label">{sum(h for _, h in patterns['full_days'])} total hours</div>
            </div>
            <div class="stat-card">
                <h3>Total Work Days</h3>
                <div class="value">{len(work_stats)}</div>
                <div class="label">Days with activity</div>
            </div>
            <div class="stat-card">
                <h3>Consecutive Days</h3>
                <div class="value">{patterns['consecutive_days']}</div>
                <div class="label">Longest streak</div>
            </div>
            <div class="stat-card">
                <h3>Weekend Work</h3>
                <div class="value">{patterns['weekend_work']}</div>
                <div class="label">Saturday/Sunday</div>
            </div>
            <div class="stat-card">
                <h3>Average Hours/Day</h3>
                <div class="value">{total_hours/len(work_stats):.1f}</div>
                <div class="label">Mean daily hours</div>
            </div>
            <div class="stat-card">
                <h3>Total Files</h3>
                <div class="value">{len(files_metadata):,}</div>
                <div class="label">Created/Modified</div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-container">
                <div class="chart-title">Daily Work Hours</div>
                <canvas id="hoursChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Cumulative Hours Over Time</div>
                <canvas id="cumulativeChart"></canvas>
            </div>
        </div>
        
        <div class="patterns-section">
            <div class="timeline-title">Work Pattern Analysis</div>
            <div class="patterns-grid">
                <div class="pattern-card">
                    <h3>Time of Day Distribution</h3>
                    <ul class="pattern-list">
                        <li>
                            <span>Late Night (11pm-5am)</span>
                            <strong>{patterns['late_night_hours']} hours</strong>
                        </li>
                        <li>
                            <span>Early Morning (5am-9am)</span>
                            <strong>{patterns['early_morning_hours']} hours</strong>
                        </li>
                        <li>
                            <span>Business Hours (9am-5pm)</span>
                            <strong>{patterns['business_hours']} hours</strong>
                        </li>
                        <li>
                            <span>Evening (5pm-11pm)</span>
                            <strong>{patterns['evening_hours']} hours</strong>
                        </li>
                    </ul>
                </div>
                
                <div class="pattern-card">
                    <h3>Top Marathon Days</h3>
                    <ul class="pattern-list">
"""
    
    for date, hours in sorted(patterns['marathon_days'], key=lambda x: x[1], reverse=True)[:10]:
        html += f"""
                        <li>
                            <span>{date}</span>
                            <strong>{hours} hours</strong>
                        </li>
"""
    
    html += """
                    </ul>
                </div>
                
                <div class="pattern-card">
                    <h3>Work Intensity</h3>
                    <ul class="pattern-list">
"""
    
    total_days = len(work_stats)
    html += f"""
                        <li>
                            <span>16+ hour days</span>
                            <strong>{len(patterns['marathon_days'])} ({len(patterns['marathon_days'])/total_days*100:.1f}%)</strong>
                        </li>
                        <li>
                            <span>12-16 hour days</span>
                            <strong>{len(patterns['long_days'])} ({len(patterns['long_days'])/total_days*100:.1f}%)</strong>
                        </li>
                        <li>
                            <span>8-12 hour days</span>
                            <strong>{len(patterns['full_days'])} ({len(patterns['full_days'])/total_days*100:.1f}%)</strong>
                        </li>
                        <li>
                            <span>Avg hours/day</span>
                            <strong>{total_hours/total_days:.1f} hours</strong>
                        </li>
"""
    
    html += """
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="timeline-section">
            <div class="timeline-title">Daily Work Schedule</div>
"""
    
    for date, stats in sorted_stats:
        hours = stats['hours']
        
        if hours >= 16:
            class_name = "marathon"
        elif hours >= 12:
            class_name = "long"
        elif hours >= 8:
            class_name = "full"
        elif hours >= 4:
            class_name = "half"
        else:
            class_name = "short"
        
        html += f"""
            <div class="day-block">
                <div class="day-header {class_name}">
                    <div class="day-date">{date}</div>
                    <div class="day-type">{stats['type']}</div>
                    <div class="day-hours">{hours} hours</div>
                    <div class="day-range">{stats['hour_range']}</div>
                </div>
                <div class="hour-blocks">
"""
        
        # Show 24-hour timeline
        for hour in range(24):
            if hour in stats['active_hours']:
                if 23 <= hour or hour < 5:
                    block_class = "active late-night"
                elif 5 <= hour < 9:
                    block_class = "active early"
                else:
                    block_class = "active"
                html += f'                    <div class="hour-block {block_class}">{hour:02d}</div>\n'
            else:
                html += f'                    <div class="hour-block">{hour:02d}</div>\n'
        
        html += """                </div>
            </div>
"""
    
    html += f"""
        </div>
    </div>
    
    <script>
        const dates = {json.dumps(dates)};
        const hours = {json.dumps(hours)};
        const cumulativeHours = {json.dumps(cumulative_hours)};
        
        // Daily hours chart
        new Chart(document.getElementById('hoursChart'), {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Hours Worked',
                    data: hours,
                    backgroundColor: function(context) {{
                        const value = context.parsed.y;
                        if (value >= 16) return 'rgba(245, 87, 108, 0.8)';
                        if (value >= 12) return 'rgba(240, 147, 251, 0.8)';
                        if (value >= 8) return 'rgba(79, 172, 254, 0.8)';
                        if (value >= 4) return 'rgba(0, 242, 254, 0.8)';
                        return 'rgba(168, 237, 234, 0.8)';
                    }},
                    borderColor: 'rgba(30, 60, 114, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 24,
                        ticks: {{
                            stepSize: 2,
                            callback: function(value) {{
                                return value + 'h';
                            }}
                        }},
                        title: {{
                            display: true,
                            text: 'Hours Worked',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Date',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Worked: ' + context.parsed.y + ' hours';
                            }}
                        }}
                    }},
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Cumulative hours chart
        new Chart(document.getElementById('cumulativeChart'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Cumulative Hours',
                    data: cumulativeHours,
                    backgroundColor: 'rgba(79, 172, 254, 0.2)',
                    borderColor: 'rgba(30, 60, 114, 1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString() + 'h';
                            }}
                        }},
                        title: {{
                            display: true,
                            text: 'Total Hours',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Date',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Total: ' + context.parsed.y.toLocaleString() + ' hours';
                            }}
                        }}
                    }}
                }}
            }}
        }});
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
            'output_html': 'ai_agents_work_hours.html',
            'output_json': 'ai_agents_work_hours.json'
        },
        {
            'name': 'In_House_SQL (G_Folder)',
            'path': r'c:\Users\gpoli\GIT\In_House_SQL',
            'output_html': 'g_folder_work_hours.html',
            'output_json': 'g_folder_work_hours.json'
        }
    ]
    
    for project in projects:
        print(f"\n{'='*70}")
        print(f"CALCULATING WORK HOURS: {project['name']}")
        print(f"{'='*70}\n")
        
        # Scan files
        files_metadata = scan_directory_metadata(project['path'])
        
        # Analyze hourly activity
        print("Analyzing hourly activity patterns...")
        hourly_activity, daily_hours = analyze_hourly_activity(files_metadata, 'created')
        
        # Calculate work hours
        print("Calculating actual work hours...")
        work_stats, total_hours = calculate_work_hours(daily_hours)
        
        # Analyze patterns
        print("Analyzing work patterns...")
        patterns = analyze_work_patterns(work_stats)
        
        # Generate report
        output_path = os.path.join(project['path'], project['output_html'])
        print(f"Generating report...")
        generate_detailed_report(
            project['name'],
            files_metadata,
            work_stats,
            patterns,
            total_hours,
            output_path
        )
        
        # Save JSON summary
        json_path = os.path.join(project['path'], project['output_json'])
        summary = {
            'project': project['name'],
            'total_hours': total_hours,
            'total_days': len(work_stats),
            'avg_hours_per_day': total_hours / len(work_stats) if work_stats else 0,
            'marathon_days': len(patterns['marathon_days']),
            'long_days': len(patterns['long_days']),
            'full_days': len(patterns['full_days']),
            'consecutive_days_streak': patterns['consecutive_days'],
            'weekend_work_days': patterns['weekend_work'],
            'daily_breakdown': {date: stats['hours'] for date, stats in work_stats.items()}
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"WORK HOURS SUMMARY: {project['name']}")
        print(f"{'='*70}")
        print(f"Total Work Hours: {total_hours:,} hours")
        print(f"Total Work Days: {len(work_stats)}")
        print(f"Average Hours/Day: {total_hours/len(work_stats):.1f} hours")
        print(f"\nWork Intensity:")
        print(f"  Marathon Days (16+ hrs): {len(patterns['marathon_days'])} days")
        print(f"  Long Days (12-16 hrs): {len(patterns['long_days'])} days")
        print(f"  Full Days (8-12 hrs): {len(patterns['full_days'])} days")
        print(f"  Consecutive Days Streak: {patterns['consecutive_days']} days")
        print(f"  Weekend Work: {patterns['weekend_work']} days")
        print(f"\nTime Distribution:")
        print(f"  Late Night (11pm-5am): {patterns['late_night_hours']} hours")
        print(f"  Early Morning (5am-9am): {patterns['early_morning_hours']} hours")
        print(f"  Business Hours (9am-5pm): {patterns['business_hours']} hours")
        print(f"  Evening (5pm-11pm): {patterns['evening_hours']} hours")
        print(f"\nReport saved: {output_path}")
        print(f"JSON saved: {json_path}")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
