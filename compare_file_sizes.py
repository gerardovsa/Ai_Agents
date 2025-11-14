"""
Compare File Sizes: Local vs Git Repository

This script compares the actual file sizes on disk with what's tracked in Git
to ensure everything is properly synchronized.
"""

import os
import subprocess
from pathlib import Path
from collections import defaultdict

def get_file_size(path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(path)
    except:
        return 0

def format_size(bytes_size):
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:6.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:6.1f} TB"

def get_git_tracked_files():
    """Get all files tracked by Git"""
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n')
    except:
        return []

def analyze_directory(root_path):
    """Analyze directory structure"""
    root = Path(root_path)
    
    # Get Git tracked files
    print("="*80)
    print("FETCHING GIT TRACKED FILES...")
    print("="*80)
    git_files = set(get_git_tracked_files())
    print(f"Found {len(git_files)} files tracked by Git\n")
    
    # Scan local files
    print("="*80)
    print("SCANNING LOCAL FILES...")
    print("="*80)
    
    local_files = {}
    folder_sizes = defaultdict(int)
    
    ignore_patterns = [
        '.git',
        '__pycache__',
        'node_modules',
        '.venv',
        'venv',
        '.pytest_cache',
        '.vscode',
        '.idea',
        '*.pyc',
        '*.pyo'
    ]
    
    for item in root.rglob('*'):
        if item.is_file():
            # Skip ignored patterns
            skip = False
            for pattern in ignore_patterns:
                if pattern in str(item):
                    skip = True
                    break
            
            if not skip:
                rel_path = item.relative_to(root)
                size = get_file_size(item)
                local_files[str(rel_path)] = size
                
                # Track folder sizes
                folder = str(rel_path.parent)
                folder_sizes[folder] += size
    
    print(f"Found {len(local_files)} local files\n")
    
    # Compare
    print("="*80)
    print("COMPARISON: LOCAL vs GIT")
    print("="*80)
    
    only_local = []
    only_git = []
    size_differences = []
    
    # Files only in local
    for local_file in local_files:
        normalized = local_file.replace('\\', '/')
        if normalized not in git_files:
            only_local.append((local_file, local_files[local_file]))
    
    # Files only in git
    for git_file in git_files:
        normalized = git_file.replace('/', '\\') if os.name == 'nt' else git_file
        if normalized not in local_files:
            only_git.append(git_file)
    
    print(f"\n📁 FILES ONLY IN LOCAL (not tracked by Git): {len(only_local)}")
    if only_local:
        print("\nTop 10 by size:")
        only_local.sort(key=lambda x: x[1], reverse=True)
        for path, size in only_local[:10]:
            print(f"  {format_size(size)}  {path}")
    
    print(f"\n📦 FILES ONLY IN GIT (missing locally): {len(only_git)}")
    if only_git:
        for path in only_git[:10]:
            print(f"  {path}")
    
    # Folder size summary
    print("\n" + "="*80)
    print("FOLDER SIZE ANALYSIS")
    print("="*80)
    
    major_folders = {}
    for folder, size in folder_sizes.items():
        parts = folder.split(os.sep)
        if parts[0] == '.':
            continue
        root_folder = parts[0] if parts[0] else 'root'
        major_folders[root_folder] = major_folders.get(root_folder, 0) + size
    
    # Sort by size
    sorted_folders = sorted(major_folders.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTop folders by size:")
    for folder, size in sorted_folders[:15]:
        print(f"  {format_size(size):>12}  {folder}/")
    
    # Total size
    total_size = sum(local_files.values())
    print(f"\n{'='*80}")
    print(f"TOTAL LOCAL SIZE: {format_size(total_size)}")
    print(f"TOTAL FILES: {len(local_files)}")
    print(f"{'='*80}")
    
    # Critical files check
    print("\n" + "="*80)
    print("CRITICAL FILES CHECK")
    print("="*80)
    
    critical_files = [
        'AI_infrastructure/flask_app.py',
        'AI_infrastructure/routes/google_auth_routes_V2_FIXED.py',
        'AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py',
        'AI_infrastructure/migrations/add_refresh_attempts_column.py',
        'AI_infrastructure/migrations/init_user_sessions_table.py',
        'tools/registry_v3.py',
        'UI/business-ai-platform-v2.html',
    ]
    
    for file in critical_files:
        normalized = file.replace('/', '\\') if os.name == 'nt' else file
        if normalized in local_files:
            size = local_files[normalized]
            in_git = file in git_files or normalized.replace('\\', '/') in git_files
            status = "✅ In Git" if in_git else "❌ NOT in Git"
            print(f"  {format_size(size):>12}  {status}  {file}")
        else:
            print(f"  {'MISSING':>12}  ❌ NOT FOUND  {file}")
    
    # Database files
    print("\n" + "="*80)
    print("DATABASE FILES")
    print("="*80)
    
    db_files = [
        'data/ai_infrastructure.db',
        'data/ai_infrastructure.db-shm',
        'data/ai_infrastructure.db-wal',
        'data/sessions.db',
        'data/sessions.db-shm',
        'data/sessions.db-wal',
    ]
    
    for file in db_files:
        normalized = file.replace('/', '\\') if os.name == 'nt' else file
        if normalized in local_files:
            size = local_files[normalized]
            in_git = file in git_files or normalized.replace('\\', '/') in git_files
            status = "✅ In Git" if in_git else "⚠️  Not tracked"
            print(f"  {format_size(size):>12}  {status}  {file}")
        else:
            print(f"  {'N/A':>12}  File not found  {file}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if len(only_local) == 0 and len(only_git) == 0:
        print("✅ PERFECT SYNC: All files match between local and Git")
    else:
        print(f"⚠️  {len(only_local)} files local-only (untracked)")
        print(f"⚠️  {len(only_git)} files git-only (missing locally)")
    
    print("="*80)

if __name__ == "__main__":
    root_path = Path(__file__).parent
    analyze_directory(root_path)
