"""
Analyze file creation and modification timestamps to detect work sessions
"""

import os
from datetime import datetime, timedelta
from collections import defaultdict

FOCUSED_PROJECTS = [
    'AI_agents',
    'In_House_SQL',
    'In_House_Print',
    'In_House_V2', 
    'In_House_FRED',
    'G_Folder Oct 8th',
    'G_Folder Oct 10th',
    'G_Folder Oct 14th',
    'G_Folder Oct 15th',
    'G_Folder Oct 17th'
]

def collect_all_timestamps():
    """Collect both creation and modification timestamps"""
    base_path = r"C:\Users\gpoli\GIT"
    
    all_timestamps = []  # List of (datetime, event_type, filepath)
    
    print("Collecting timestamps from all files...")
    
    for project in FOCUSED_PROJECTS:
        project_path = os.path.join(base_path, project)
        
        if not os.path.exists(project_path):
            continue
        
        print(f"  Scanning {project}...")
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
                        
                        # Get both creation and modification times
                        created = datetime.fromtimestamp(stats.st_ctime)
                        modified = datetime.fromtimestamp(stats.st_mtime)
                        
                        all_timestamps.append((created, 'create', filepath, project))
                        all_timestamps.append((modified, 'modify', filepath, project))
                        
                        count += 1
                    except:
                        continue
            
            print(f"    Processed {count:,} files")
        except Exception as e:
            print(f"    ERROR: {e}")
    
    print(f"\nTotal timestamps collected: {len(all_timestamps):,}")
    return all_timestamps


def analyze_daily_activity(timestamps):
    """Group timestamps by day and analyze time gaps"""
    
    # Sort all timestamps chronologically
    timestamps.sort(key=lambda x: x[0])
    
    # Group by date
    by_date = defaultdict(list)
    for ts, event_type, filepath, project in timestamps:
        date_str = ts.strftime('%Y-%m-%d')
        by_date[date_str].append(ts)
    
    print(f"\n{'='*80}")
    print("DAILY ACTIVITY ANALYSIS - CORRECTED LOGIC")
    print(f"{'='*80}\n")
    
    # Analyze each day
    daily_summaries = []
    
    for date_str in sorted(by_date.keys()):
        day_timestamps = sorted(set(by_date[date_str]))  # Remove duplicates
        
        if len(day_timestamps) < 2:
            continue
        
        # Apply 15-min padding to each timestamp
        padded_timestamps = []
        for ts in day_timestamps:
            start_padded = ts - timedelta(minutes=15)
            end_padded = ts + timedelta(minutes=15)
            padded_timestamps.append((start_padded, end_padded, ts))
        
        # Sort by padded start time
        padded_timestamps.sort(key=lambda x: x[0])
        
        # Find sessions based on gaps between padded timestamps
        sessions = []
        current_session_start = padded_timestamps[0][0]  # First padded start
        current_session_end = padded_timestamps[0][1]    # First padded end
        
        for i in range(1, len(padded_timestamps)):
            prev_padded_end = padded_timestamps[i-1][1]
            curr_padded_start = padded_timestamps[i][0]
            curr_padded_end = padded_timestamps[i][1]
            
            # Calculate gap between previous padded end and current padded start
            gap_minutes = (curr_padded_start - prev_padded_end).total_seconds() / 60
            
            # If gap > 60 minutes, it's a break (new session)
            if gap_minutes > 60:
                sessions.append((current_session_start, prev_padded_end))
                current_session_start = curr_padded_start
                current_session_end = curr_padded_end
            else:
                # Continuous work - extend the session end
                current_session_end = curr_padded_end
        
        # Add final session
        sessions.append((current_session_start, current_session_end))
        
        # Calculate total work time
        total_minutes = 0
        for start, end in sessions:
            session_duration = (end - start).total_seconds() / 60
            total_minutes += session_duration
        
        total_hours = total_minutes / 60
        
        earliest = day_timestamps[0]
        latest = day_timestamps[-1]
        span_hours = (latest - earliest).total_seconds() / 3600
        
        daily_summaries.append({
            'date': date_str,
            'timestamps': len(day_timestamps),
            'sessions': len(sessions),
            'total_hours': total_hours,
            'earliest': earliest.strftime('%H:%M:%S'),
            'latest': latest.strftime('%H:%M:%S'),
            'span_hours': span_hours
        })
    
    # Print summary
    print(f"Date       | Events | Sessions | Est Hours | Earliest - Latest | Span")
    print("-" * 80)
    
    for day in daily_summaries[-20:]:  # Show last 20 days
        print(f"{day['date']} | {day['timestamps']:6,} | {day['sessions']:8} | {day['total_hours']:9.1f} | "
              f"{day['earliest']} - {day['latest']} | {day['span_hours']:.1f}h")
    
    print(f"\n{'='*80}")
    print(f"SUMMARY STATISTICS")
    print(f"{'='*80}\n")
    
    total_days = len(daily_summaries)
    total_work_hours = sum(d['total_hours'] for d in daily_summaries)
    avg_hours_per_day = total_work_hours / total_days if total_days > 0 else 0
    
    print(f"Total work days: {total_days}")
    print(f"Total work hours: {total_work_hours:.1f}")
    print(f"Average hours/day: {avg_hours_per_day:.2f}")
    print(f"Total events (creates + modifies): {sum(d['timestamps'] for d in daily_summaries):,}")
    
    # Show some example days with detailed session breakdown
    print(f"\n{'='*80}")
    print(f"DETAILED SESSION BREAKDOWN (Sample Days)")
    print(f"{'='*80}\n")
    
    for day in daily_summaries[-5:]:  # Last 5 days
        date_str = day['date']
        day_timestamps = sorted(by_date[date_str])
        
        print(f"\n{date_str} - {day['timestamps']:,} events")
        print("-" * 40)
        
        # Apply padding and find sessions
        padded_timestamps = []
        for ts in day_timestamps:
            start_padded = ts - timedelta(minutes=15)
            end_padded = ts + timedelta(minutes=15)
            padded_timestamps.append((start_padded, end_padded, ts))
        
        padded_timestamps.sort(key=lambda x: x[0])
        
        sessions = []
        current_session_start = padded_timestamps[0][0]
        current_session_end = padded_timestamps[0][1]
        
        for i in range(1, len(padded_timestamps)):
            prev_padded_end = padded_timestamps[i-1][1]
            curr_padded_start = padded_timestamps[i][0]
            curr_padded_end = padded_timestamps[i][1]
            
            gap_minutes = (curr_padded_start - prev_padded_end).total_seconds() / 60
            
            if gap_minutes > 60:
                sessions.append((current_session_start, prev_padded_end))
                current_session_start = curr_padded_start
                current_session_end = curr_padded_end
            else:
                current_session_end = curr_padded_end
        
        sessions.append((current_session_start, current_session_end))
        
        for i, (start, end) in enumerate(sessions, 1):
            duration = (end - start).total_seconds() / 60
            hours = duration / 60
            print(f"  Session {i}: {start.strftime('%H:%M')} - {end.strftime('%H:%M')} "
                  f"= {duration:.0f} min ({hours:.2f} hrs)")
    
    return daily_summaries


if __name__ == "__main__":
    timestamps = collect_all_timestamps()
    daily_summaries = analyze_daily_activity(timestamps)
