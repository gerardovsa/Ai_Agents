"""
Upload local database to Render persistent disk via shell access

USAGE:
1. Run this script to get the upload command
2. Copy the command and run it in Render Shell
"""

import os
from pathlib import Path

# Get local database path
root_dir = Path(__file__).parent.parent.parent
local_db = root_dir / 'data' / 'ai_infrastructure.db'

if not local_db.exists():
    print(f"[ERROR] Database not found at: {local_db}")
    exit(1)

db_size_mb = local_db.stat().st_size / (1024 * 1024)

print("=" * 70)
print("RENDER DATABASE UPLOAD INSTRUCTIONS")
print("=" * 70)
print()
print(f"Local database: {local_db}")
print(f"Size: {db_size_mb:.2f} MB")
print()
print("STEP 1: Go to Render Dashboard")
print("  https://dashboard.render.com")
print()
print("STEP 2: Open Shell for ai-agents-backend service")
print("  Click 'Shell' tab in dashboard")
print()
print("STEP 3: Stop the service temporarily")
print("  Settings → 'Suspend' (prevents database lock)")
print()
print("STEP 4: Upload database via one of these methods:")
print()
print("METHOD A - Direct Upload (Recommended):")
print("  1. In Render Shell, run:")
print("     cd /data")
print("     curl -O https://your-temp-host.com/ai_infrastructure.db")
print()
print("METHOD B - Base64 Upload (For small DBs):")
print("  1. On your PC, create base64 file:")
print(f"     cd {root_dir}")
print("     certutil -encode data\\ai_infrastructure.db data\\ai_infrastructure.db.b64")
print()
print("  2. Copy contents of data\\ai_infrastructure.db.b64")
print()
print("  3. In Render Shell, run:")
print("     cd /data")
print("     cat > ai_infrastructure.db.b64 << 'EOF'")
print("     [paste base64 content]")
print("     EOF")
print("     base64 -d ai_infrastructure.db.b64 > ai_infrastructure.db")
print("     rm ai_infrastructure.db.b64")
print()
print("METHOD C - SCP Upload (Fastest for large files):")
print("  1. Get Render shell SSH details from dashboard")
print("  2. Use SCP:")
print(f"     scp {local_db} srv-XXXXX:/data/ai_infrastructure.db")
print()
print("STEP 5: Verify upload")
print("  In Render Shell:")
print("     ls -lh /data/ai_infrastructure.db")
print("     sqlite3 /data/ai_infrastructure.db 'SELECT COUNT(*) FROM users'")
print()
print("STEP 6: Resume service")
print("  Settings → 'Resume'")
print()
print("=" * 70)
print()
print("QUICK METHOD - Use Render Disk Backup/Restore:")
print("=" * 70)
print("1. Create a temporary public URL for your database:")
print("   - Upload data/ai_infrastructure.db to Google Drive/Dropbox")
print("   - Get shareable link")
print()
print("2. Download in Render Shell:")
print("   cd /data")
print("   wget -O ai_infrastructure.db 'YOUR_SHARE_LINK'")
print()
print("=" * 70)
