"""
COMPLETE PROJECT ANALYSIS - ALL FOLDERS
Analyzes EVERY project folder in the GIT directory
From the very first file to the last file created
"""

import os
from datetime import datetime
from collections import defaultdict
import sys

# All main project folders (excluding Copy folders for now)
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

def scan_project(project_name, base_path):
    """Scan a project and return all file creation dates"""
    project_path = os.path.join(base_path, project_name)
    
    if not os.path.exists(project_path):
        return []
    
    print(f"  Scanning {project_name}...", end='', flush=True)
    
    files_data = []
    file_count = 0
    
    try:
        for root, dirs, files in os.walk(project_path):
            # Skip common excluded directories
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
                    
                    files_data.append({
                        'project': project_name,
                        'file': filename,
                        'created': created,
                        'size': stats.st_size
                    })
                    file_count += 1
                except:
                    continue
        
        print(f" {file_count:,} files")
        return files_data
    
    except Exception as e:
        print(f" ERROR: {e}")
        return []

def analyze_all_projects():
    """Analyze all projects"""
    
    print(f"\n{'='*100}")
    print("COMPLETE PROJECT ANALYSIS - ALL FOLDERS")
    print("Scanning C:\\Users\\gpoli\\GIT")
    print(f"{'='*100}\n")
    
    base_path = r"C:\Users\gpoli\GIT"
    all_files = []
    
    # Scan all main projects
    for project in MAIN_PROJECTS:
        project_files = scan_project(project, base_path)
        all_files.extend(project_files)
    
    if not all_files:
        print("\n❌ No files found!")
        return
    
    # Sort by creation date
    all_files.sort(key=lambda x: x['created'])
    
    print(f"\n{'='*100}")
    print("ANALYSIS RESULTS")
    print(f"{'='*100}\n")
    
    first_file = all_files[0]
    last_file = all_files[-1]
    
    print(f"Total files analyzed: {len(all_files):,}")
    print(f"\nFirst file ever created:")
    print(f"  Date: {first_file['created'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Project: {first_file['project']}")
    print(f"  File: {first_file['file']}")
    
    print(f"\nLast file created:")
    print(f"  Date: {last_file['created'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Project: {last_file['project']}")
    print(f"  File: {last_file['file']}")
    
    # Date range
    start_date = first_file['created'].date()
    end_date = last_file['created'].date()
    total_days = (end_date - start_date).days + 1
    
    print(f"\nDate range: {start_date} to {end_date}")
    print(f"Total span: {total_days} days")
    
    # Files by project
    print(f"\n{'='*100}")
    print("FILES BY PROJECT")
    print(f"{'='*100}\n")
    
    project_counts = defaultdict(int)
    project_first_date = {}
    project_last_date = {}
    
    for file in all_files:
        project = file['project']
        project_counts[project] += 1
        
        if project not in project_first_date:
            project_first_date[project] = file['created']
        project_last_date[project] = file['created']
    
    # Sort by file count
    sorted_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)
    
    for project, count in sorted_projects:
        first = project_first_date[project].strftime('%Y-%m-%d')
        last = project_last_date[project].strftime('%Y-%m-%d')
        days = (project_last_date[project].date() - project_first_date[project].date()).days + 1
        
        print(f"{project:40s}: {count:7,} files  ({first} to {last}, {days} days)")
    
    # Files by date
    print(f"\n{'='*100}")
    print("WORK ACTIVITY BY DATE")
    print(f"{'='*100}\n")
    
    files_by_date = defaultdict(lambda: {'count': 0, 'projects': set()})
    
    for file in all_files:
        date_str = file['created'].strftime('%Y-%m-%d')
        files_by_date[date_str]['count'] += 1
        files_by_date[date_str]['projects'].add(file['project'])
    
    # Get all dates with work
    work_dates = sorted(files_by_date.keys())
    
    print(f"Total work days: {len(work_dates)}")
    print(f"\nRecent activity (last 30 days):\n")
    
    for date_str in work_dates[-30:]:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        count = files_by_date[date_str]['count']
        projects = sorted(list(files_by_date[date_str]['projects']))
        
        # Show top 3 projects
        project_str = ', '.join(projects[:3])
        if len(projects) > 3:
            project_str += f" (+{len(projects)-3} more)"
        
        print(f"{date_str} ({day_name:9s}): {count:5,} files  [{project_str}]")
    
    # Check for gaps
    print(f"\n{'='*100}")
    print("GAPS IN WORK ACTIVITY (7+ consecutive days)")
    print(f"{'='*100}\n")
    
    prev_date = None
    for work_date in work_dates:
        current = datetime.strptime(work_date, '%Y-%m-%d')
        
        if prev_date:
            gap = (current - prev_date).days - 1
            if gap >= 7:
                print(f"GAP: {prev_date.strftime('%Y-%m-%d')} to {current.strftime('%Y-%m-%d')} = {gap} days")
        
        prev_date = current
    
    # Save summary
    summary_file = 'all_projects_summary.txt'
    with open(summary_file, 'w') as f:
        f.write(f"COMPLETE PROJECT ANALYSIS\\n")
        f.write(f"{'='*100}\\n\\n")
        f.write(f"Total files: {len(all_files):,}\\n")
        f.write(f"Date range: {start_date} to {end_date} ({total_days} days)\\n")
        f.write(f"Total work days: {len(work_dates)}\\n\\n")
        f.write(f"FILES BY PROJECT:\\n")
        for project, count in sorted_projects:
            f.write(f"  {project:40s}: {count:7,} files\\n")
    
    print(f"\n{'='*100}")
    print(f"✅ Analysis complete!")
    print(f"✅ Summary saved to: {summary_file}")
    print(f"{'='*100}\n")
    
    return all_files, files_by_date

if __name__ == "__main__":
    all_files, files_by_date = analyze_all_projects()
