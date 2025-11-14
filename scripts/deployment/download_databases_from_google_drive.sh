#!/bin/bash
# Download ALL databases from Google Drive to Render /data folder
# Folder: https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O

echo "=========================================="
echo "DOWNLOADING DATABASES FROM GOOGLE DRIVE"
echo "=========================================="

cd /data

# Backup existing databases
echo ""
echo "1. Backing up existing databases..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp -v *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "No existing databases to backup"

# Download ai_infrastructure.db (638 KB - CRITICAL)
echo ""
echo "2. Downloading ai_infrastructure.db..."
FILE_ID="REPLACE_WITH_FILE_ID_FROM_DRIVE"
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=${FILE_ID}" -O ai_infrastructure.db

# Download sessions.db (733 KB)
echo ""
echo "3. Downloading sessions.db..."
FILE_ID="REPLACE_WITH_FILE_ID_FROM_DRIVE"
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=${FILE_ID}" -O sessions.db

# Download synergy_sessions.db (225 KB)
echo ""
echo "4. Downloading synergy_sessions.db..."
FILE_ID="REPLACE_WITH_FILE_ID_FROM_DRIVE"
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=${FILE_ID}" -O synergy_sessions.db

# Download kanban_analytics.db (655 KB)
echo ""
echo "5. Downloading kanban_analytics.db..."
FILE_ID="REPLACE_WITH_FILE_ID_FROM_DRIVE"
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=${FILE_ID}" -O kanban_analytics.db

# Download stock_data.db (8.8 MB - LARGE!)
echo ""
echo "6. Downloading stock_data.db (LARGE - 8.8MB)..."
FILE_ID="REPLACE_WITH_FILE_ID_FROM_DRIVE"
wget --no-check-certificate "https://drive.google.com/uc?export=download&id=${FILE_ID}" -O stock_data.db

# Verify downloads
echo ""
echo "=========================================="
echo "VERIFICATION"
echo "=========================================="
echo ""
ls -lh *.db
echo ""

# Check schemas
echo "Checking ai_infrastructure.db schema..."
sqlite3 ai_infrastructure.db "SELECT COUNT(*) as column_count FROM pragma_table_info('users');"
echo ""
sqlite3 ai_infrastructure.db "SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';"

echo ""
echo "=========================================="
echo "DOWNLOAD COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart the Render service"
echo "2. Test Microsoft/Google OAuth login"
echo "3. Check logs for any errors"
echo ""
