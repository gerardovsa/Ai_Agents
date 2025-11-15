"""
Generate Render Shell Commands for Database Upload
Automatically extracts FILE_IDs from Google Drive links and generates ready-to-paste commands
"""

import os
import re

# Your Google Drive folder
DRIVE_FOLDER = "https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O"

# Database files to upload
DATABASES = [
    {"name": "ai_infrastructure.db", "size": "638 KB", "critical": True},
    {"name": "sessions.db", "size": "733 KB", "critical": True},
    {"name": "synergy_sessions.db", "size": "225 KB", "critical": False},
    {"name": "kanban_analytics.db", "size": "655 KB", "critical": False},
    {"name": "stock_data.db", "size": "8.8 MB", "critical": False},
]

print("=" * 80)
print("RENDER DATABASE UPLOAD COMMAND GENERATOR")
print("=" * 80)
print()
print(f"Google Drive Folder: {DRIVE_FOLDER}")
print()

# Step 1: Prompt user for FILE_IDs
print("STEP 1: Get FILE_IDs from Google Drive")
print("-" * 80)
print()
print("For each database file:")
print("1. Go to your Google Drive folder")
print("2. Right-click the file → Get link")
print("3. Make sure it's set to: 'Anyone with the link can view'")
print("4. Copy the link (looks like: https://drive.google.com/file/d/FILE_ID_HERE/view)")
print("5. Paste the link or just the FILE_ID below")
print()

file_ids = {}
for db in DATABASES:
    critical_marker = " [CRITICAL]" if db["critical"] else ""
    while True:
        link = input(f"Enter link/FILE_ID for {db['name']}{critical_marker} ({db['size']}): ").strip()
        
        if not link:
            print(f"  Skipping {db['name']}")
            break
        
        # Extract FILE_ID from link if full URL was pasted
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
        if match:
            file_id = match.group(1)
        else:
            file_id = link
        
        # Validate FILE_ID format
        if re.match(r'^[a-zA-Z0-9_-]+$', file_id):
            file_ids[db['name']] = file_id
            print(f"  [OK] Got FILE_ID: {file_id}")
            break
        else:
            print(f"  ✗ Invalid FILE_ID format. Try again.")

if not file_ids:
    print()
    print("No FILE_IDs provided. Exiting.")
    exit(1)

print()
print("=" * 80)
print("STEP 2: Generated Render Shell Commands")
print("=" * 80)
print()

# Generate the shell commands
commands = []

# Header
commands.append("# =========================================")
commands.append("# RENDER DATABASE UPLOAD - AUTO-GENERATED")
commands.append("# =========================================")
commands.append("")
commands.append("# Go to data folder")
commands.append("cd /data")
commands.append("")
commands.append("# Backup existing databases")
commands.append("echo 'Creating backup...'")
commands.append("mkdir -p backup_$(date +%Y%m%d_%H%M%S)")
commands.append("cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'No existing databases'")
commands.append("")

# Download each database
for db in DATABASES:
    if db['name'] in file_ids:
        file_id = file_ids[db['name']]
        commands.append(f"# Download {db['name']} ({db['size']})")
        commands.append(f"echo 'Downloading {db['name']}...'")
        commands.append(f"wget --no-check-certificate 'https://drive.google.com/uc?export=download&id={file_id}' -O {db['name']}")
        commands.append("")

# Verification
commands.append("# Verify downloads")
commands.append("echo ''")
commands.append("echo '===== VERIFICATION ====='")
commands.append("ls -lh *.db")
commands.append("")

# Critical check for OAuth columns
if 'ai_infrastructure.db' in file_ids:
    commands.append("# CRITICAL CHECK: Verify OAuth columns exist")
    commands.append("echo ''")
    commands.append("echo '===== CHECKING OAuth COLUMNS ====='")
    commands.append("sqlite3 ai_infrastructure.db \"SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';\"")
    commands.append("echo ''")
    commands.append("echo 'Expected output: has_google_oauth, has_microsoft_oauth'")
    commands.append("")

commands.append("echo ''")
commands.append("echo '===== UPLOAD COMPLETE! ====='")
commands.append("echo 'Next steps:'")
commands.append("echo '1. Go to Render Dashboard'")
commands.append("echo '2. Click: Manual Deploy → Clear build cache & deploy'")
commands.append("echo '3. Wait 2-3 minutes for rebuild'")
commands.append("echo '4. Test OAuth login'")

# Print commands
full_script = "\n".join(commands)
print(full_script)

# Save to file
output_file = "render_upload_commands.sh"
with open(output_file, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write(full_script)

print()
print("=" * 80)
print("STEP 3: Next Actions")
print("=" * 80)
print()
print(f"[OK] Commands saved to: {output_file}")
print()
print("TO EXECUTE:")
print("1. Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/shell")
print("2. Copy the commands above")
print("3. Paste into Render Shell")
print("4. Press Enter")
print()
print("ALTERNATIVE:")
print(f"1. Copy the entire {output_file} file content")
print("2. Paste into Render Shell")
print()
print("=" * 80)
print()

# Generate one-liner version
if len(file_ids) == len(DATABASES):
    print("BONUS: ONE-LINE VERSION (All databases at once)")
    print("=" * 80)
    print()
    
    one_liner_parts = [
        "cd /data",
        "mkdir -p backup_$(date +%Y%m%d_%H%M%S)",
        "cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null"
    ]
    
    for db in DATABASES:
        if db['name'] in file_ids:
            one_liner_parts.append(
                f"wget --no-check-certificate 'https://drive.google.com/uc?export=download&id={file_ids[db['name']]}' -O {db['name']}"
            )
    
    one_liner_parts.append("ls -lh *.db")
    
    if 'ai_infrastructure.db' in file_ids:
        one_liner_parts.append(
            'sqlite3 ai_infrastructure.db "SELECT name FROM pragma_table_info(\'users\') WHERE name LIKE \'%oauth%\';"'
        )
    
    one_liner = " && \\\n".join(one_liner_parts)
    print(one_liner)
    print()

print("Done!")
