"""
Analyze all work hours across ALL projects
"""
import os
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def analyze_project(root_path, project_name):
    """Analyze a single project"""
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', 
                   'venv', 'env', '.pytest_cache', '.mypy_cache',
                   'dist', 'build', '.eggs'}
    
    files_by_date = defaultdict(list)
    hourly_activity = defaultdict(set)
    
    print(f"\nScanning: {project_name}")
    file_count = 0
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for filename in files:
            if filename.startswith('.'):
                continue
                
            filepath = os.path.join(root, filename)
            try:
                stat = os.stat(filepath)
                dt = datetime.fromtimestamp(stat.st_ctime)
                date_key = dt.strftime('%Y-%m-%d')
                hour_key = dt.hour
                
                files_by_date[date_key].append(filepath)
                hourly_activity[date_key].add(hour_key)
                file_count += 1
            except:
                pass
    
    # Calculate work hours
    work_stats = {}
    total_hours = 0
    
    for date, hours_set in sorted(hourly_activity.items()):
        hours_worked = len(hours_set)
        total_hours += hours_worked
        work_stats[date] = {
            'hours': hours_worked,
            'files': len(files_by_date[date])
        }
    
    print(f"  Total files: {file_count}")
    print(f"  Total work days: {len(work_stats)}")
    print(f"  Total work hours: {total_hours}")
    print(f"  Average hours/day: {total_hours/len(work_stats) if work_stats else 0:.1f}")
    
    return {
        'project': project_name,
        'total_files': file_count,
        'total_days': len(work_stats),
        'total_hours': total_hours,
        'avg_hours_per_day': total_hours/len(work_stats) if work_stats else 0,
        'daily_stats': work_stats
    }

# Analyze all projects
projects = {
    'AI_agents': r'c:\Users\gpoli\GIT\AI_agents',
    'In_House_SQL (G_Folder)': r'c:\Users\gpoli\GIT\In_House_SQL',
}

all_results = {}

for name, path in projects.items():
    if os.path.exists(path):
        all_results[name] = analyze_project(path, name)
    else:
        print(f"\nSkipping {name}: Path not found")

# Save combined results
output_file = 'all_projects_work_hours.json'
with open(output_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*70}")
print("COMBINED SUMMARY")
print('='*70)

total_files = sum(p['total_files'] for p in all_results.values())
total_hours = sum(p['total_hours'] for p in all_results.values())
total_days = len(set().union(*[set(p['daily_stats'].keys()) for p in all_results.values()]))

print(f"Total Files Across All Projects: {total_files:,}")
print(f"Total Work Hours: {total_hours}")
print(f"Total Unique Work Days: {total_days}")
print(f"Overall Average Hours/Day: {total_hours/total_days:.1f}")

print(f"\nResults saved to: {output_file}")

# Show daily breakdown for last 30 days
print(f"\n{'='*70}")
print("DAILY BREAKDOWN (Last 30 Days)")
print('='*70)

all_dates = set()
for project_data in all_results.values():
    all_dates.update(project_data['daily_stats'].keys())

for date in sorted(all_dates)[-30:]:
    day_total_hours = 0
    day_total_files = 0
    projects_worked = []
    
    for project_name, project_data in all_results.items():
        if date in project_data['daily_stats']:
            stats = project_data['daily_stats'][date]
            day_total_hours += stats['hours']
            day_total_files += stats['files']
            projects_worked.append(f"{project_name}: {stats['hours']}h/{stats['files']}f")
    
    print(f"\n{date}: {day_total_hours}h total, {day_total_files} files")
    for p in projects_worked:
        print(f"  - {p}")
