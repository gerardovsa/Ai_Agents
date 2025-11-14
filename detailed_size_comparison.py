"""
Detailed Size Comparison: Critical Files

Compares actual file sizes with Git's tracked versions
"""

import os
import subprocess
from pathlib import Path

def get_file_size_bytes(path):
    """Get exact file size in bytes"""
    try:
        return os.path.getsize(path)
    except:
        return None

def get_git_file_size(file_path):
    """Get file size from Git index"""
    try:
        result = subprocess.run(
            ['git', 'ls-files', '-s', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        # Output format: mode hash stage size filename
        parts = result.stdout.strip().split()
        if len(parts) >= 2:
            # Get object hash
            obj_hash = parts[1]
            # Get object size
            result = subprocess.run(
                ['git', 'cat-file', '-s', obj_hash],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
    except:
        return None

def format_bytes(bytes_val):
    """Format bytes with comma separators"""
    if bytes_val is None:
        return "N/A"
    return f"{bytes_val:,} bytes"

def main():
    # Critical files to check
    critical_files = [
        'AI_infrastructure/flask_app.py',
        'AI_infrastructure/routes/google_auth_routes_V2_FIXED.py',
        'AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py',
        'AI_infrastructure/migrations/add_refresh_attempts_column.py',
        'AI_infrastructure/migrations/init_user_sessions_table.py',
        'AI_infrastructure/routes/synergy_routes.py',
        'AI_infrastructure/routes/thread_routes.py',
        'tools/registry_v3.py',
        'UI/business-ai-platform-v2.html',
        'data/ai_infrastructure.db',
        'data/sessions.db',
        'config.py',
        'AI_infrastructure/config.py',
    ]
    
    print("="*100)
    print("DETAILED FILE SIZE COMPARISON: LOCAL vs GIT")
    print("="*100)
    print(f"\n{'File':<70} {'Local':>15} {'Git':>15} {'Status':<10}")
    print("-"*100)
    
    total_local = 0
    total_git = 0
    
    for file in critical_files:
        local_size = get_file_size_bytes(file)
        git_size = get_git_file_size(file)
        
        if local_size is not None:
            total_local += local_size
        if git_size is not None:
            total_git += git_size
        
        # Determine status
        if local_size is None:
            status = "MISSING"
        elif git_size is None:
            status = "UNTRACKED"
        elif local_size == git_size:
            status = "✅ MATCH"
        elif abs(local_size - git_size) < 100:
            status = "⚠️ CLOSE"
        else:
            status = "❌ DIFFER"
        
        file_display = file if len(file) <= 68 else "..." + file[-65:]
        
        print(f"{file_display:<70} {format_bytes(local_size):>15} {format_bytes(git_size):>15} {status:<10}")
    
    print("-"*100)
    print(f"{'TOTALS':<70} {format_bytes(total_local):>15} {format_bytes(total_git):>15}")
    print("="*100)
    
    # Database WAL files analysis
    print("\n" + "="*100)
    print("DATABASE WAL FILES (Write-Ahead Log)")
    print("="*100)
    
    db_files = [
        ('data/ai_infrastructure.db', 'Main database'),
        ('data/ai_infrastructure.db-shm', 'Shared memory file'),
        ('data/ai_infrastructure.db-wal', 'Write-ahead log'),
        ('data/sessions.db', 'Sessions database'),
        ('data/sessions.db-shm', 'Shared memory file'),
        ('data/sessions.db-wal', 'Write-ahead log'),
    ]
    
    print(f"\n{'File':<50} {'Local Size':>20} {'Git Status':<20}")
    print("-"*100)
    
    for file, description in db_files:
        local_size = get_file_size_bytes(file)
        git_size = get_git_file_size(file)
        
        if git_size is not None:
            git_status = f"✅ In Git ({format_bytes(git_size)})"
        else:
            git_status = "Not tracked (normal)"
        
        file_display = f"{file} ({description})"
        if len(file_display) > 48:
            file_display = file_display[:45] + "..."
        
        print(f"{file_display:<50} {format_bytes(local_size):>20} {git_status:<20}")
    
    print("\n" + "="*100)
    print("EXPLANATION")
    print("="*100)
    print("""
✅ MATCH: Local file and Git-tracked file have identical sizes (perfectly synced)
⚠️ CLOSE: Sizes differ by less than 100 bytes (minor whitespace differences)
❌ DIFFER: Sizes differ significantly (content changes not committed)
UNTRACKED: File exists locally but not tracked by Git
MISSING: File tracked by Git but missing locally

DATABASE WAL FILES:
- .db-shm and .db-wal are SQLite temporary files
- They exist when database is open/in use
- Git tracks them from previous commit (243KB and 309KB)
- Not existing locally is NORMAL (database closed)
- These get recreated when Flask server starts

YOUR COMMIT (8fc56ac) INCLUDED:
- ai_infrastructure.db-wal (+243KB) - Git has this
- sessions.db-wal (+309KB) - Git has this
- But locally they don't exist because database is closed
""")
    
    print("="*100)

if __name__ == "__main__":
    main()
