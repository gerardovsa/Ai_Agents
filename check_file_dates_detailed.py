"""
Check file dates in detail to see if there are gaps or if timestamps were reset
"""
import os
from datetime import datetime
from collections import defaultdict

def check_dates(project_path, project_name):
    """Check file creation and modification dates"""
    
    print(f"\n{'='*80}")
    print(f"CHECKING {project_name} FILE DATES")
    print(f"{'='*80}\n")
    
    dates_by_day = defaultdict(lambda: {'count': 0, 'files': []})
    all_dates = []
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                modified = datetime.fromtimestamp(stats.st_mtime)
                
                date_str = created.strftime('%Y-%m-%d')
                dates_by_day[date_str]['count'] += 1
                dates_by_day[date_str]['files'].append(os.path.basename(file))
                all_dates.append(created)
            except:
                continue
    
    if not all_dates:
        print("No files found!")
        return
    
    all_dates.sort()
    
    print(f"Total files: {len(all_dates):,}")
    print(f"Date range: {all_dates[0].strftime('%Y-%m-%d')} to {all_dates[-1].strftime('%Y-%m-%d')}")
    print(f"\nFiles by date:\n")
    
    # Show all dates with file counts
    for date_str in sorted(dates_by_day.keys()):
        count = dates_by_day[date_str]['count']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        
        # Show sample files for days with activity
        sample_files = dates_by_day[date_str]['files'][:3]
        samples = ", ".join(sample_files)
        if len(dates_by_day[date_str]['files']) > 3:
            samples += "..."
        
        print(f"{date_str} ({day_name:9s}): {count:5,} files  [{samples}]")
    
    # Check for gaps
    print(f"\n{'='*80}")
    print("CHECKING FOR GAPS (7+ day periods with no files)")
    print(f"{'='*80}\n")
    
    sorted_dates = sorted(dates_by_day.keys())
    
    for i in range(len(sorted_dates) - 1):
        current = datetime.strptime(sorted_dates[i], '%Y-%m-%d')
        next_date = datetime.strptime(sorted_dates[i+1], '%Y-%m-%d')
        gap = (next_date - current).days
        
        if gap > 7:
            print(f"GAP: {sorted_dates[i]} to {sorted_dates[i+1]} = {gap} days")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("DETAILED FILE DATE ANALYSIS")
    print("Checking both st_ctime (creation) timestamps")
    print("="*80)
    
    g_path = r"c:\Users\gpoli\GIT\In_House_SQL"
    ai_path = r"c:\Users\gpoli\GIT\AI_agents"
    
    check_dates(g_path, "G_Folder (In_House_SQL)")
    check_dates(ai_path, "AI_agents")
