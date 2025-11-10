"""Quick check of date range in both projects"""
import os
from datetime import datetime

ai_path = r"c:\Users\gpoli\GIT\AI_agents"
g_path = r"c:\Users\gpoli\GIT\In_House_SQL"

all_dates = []

for project_name, project_path in [('G_Folder', g_path), ('AI_agents', ai_path)]:
    print(f"\nScanning {project_name}...")
    project_dates = []
    
    for root, dirs, files in os.walk(project_path):
        skip_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                project_dates.append(created)
                all_dates.append(created)
            except:
                continue
    
    if project_dates:
        project_dates.sort()
        print(f"  Earliest: {project_dates[0].strftime('%Y-%m-%d')}")
        print(f"  Latest: {project_dates[-1].strftime('%Y-%m-%d')}")
        print(f"  Files: {len(project_dates):,}")

if all_dates:
    all_dates.sort()
    print(f"\nCOMBINED:")
    print(f"  Earliest: {all_dates[0].strftime('%Y-%m-%d %H:%M')}")
    print(f"  Latest: {all_dates[-1].strftime('%Y-%m-%d %H:%M')}")
    print(f"  Total days: {(all_dates[-1].date() - all_dates[0].date()).days + 1}")
    print(f"  Total files: {len(all_dates):,}")
