"""Check work days across BOTH projects combined"""
import os
from datetime import datetime, timedelta
from collections import defaultdict

all_work_days = set()

# Scan both projects
for project_path, name in [(r'c:\Users\gpoli\GIT\AI_agents', 'AI_agents'), 
                            (r'c:\Users\gpoli\GIT\In_House_SQL', 'G_Folder')]:
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', 'venv', 'archive']]
        
        for file in files:
            try:
                file_path = os.path.join(root, file)
                stats = os.stat(file_path)
                created = datetime.fromtimestamp(stats.st_ctime)
                date_str = created.strftime('%Y-%m-%d')
                all_work_days.add(date_str)
            except:
                continue

# Sort dates
work_days = sorted(list(all_work_days))

print(f"\n{'='*80}")
print("COMBINED WORK DAYS (Both Projects)")
print(f"{'='*80}\n")
print(f"First work day: {work_days[0]}")
print(f"Last work day: {work_days[-1]}")
print(f"Total work days: {len(work_days)}")

# Find gaps
start = datetime.strptime(work_days[0], '%Y-%m-%d')
end = datetime.strptime(work_days[-1], '%Y-%m-%d')
total_days = (end - start).days + 1

print(f"Total calendar days: {total_days}")
print(f"Days without work: {total_days - len(work_days)}")

print(f"\n{'='*80}")
print("CHECKING FOR GAPS (consecutive days without work)")
print(f"{'='*80}\n")

prev_date = None
for work_day in work_days:
    current = datetime.strptime(work_day, '%Y-%m-%d')
    
    if prev_date:
        gap = (current - prev_date).days - 1
        if gap > 0:
            print(f"GAP: {prev_date.strftime('%Y-%m-%d')} to {current.strftime('%Y-%m-%d')} = {gap} day(s) without work")
    
    prev_date = current

print(f"\n{'='*80}")
print("OCTOBER 26 - NOVEMBER 4 DETAILS")
print(f"{'='*80}\n")

oct26_to_nov4 = []
current = datetime(2025, 10, 26)
end_check = datetime(2025, 11, 4)

while current <= end_check:
    date_str = current.strftime('%Y-%m-%d')
    day_name = current.strftime('%A')
    
    if date_str in work_days:
        status = "✓ WORK DAY"
    else:
        status = "✗ No work"
    
    print(f"{date_str} ({day_name:9s}): {status}")
    current += timedelta(days=1)
