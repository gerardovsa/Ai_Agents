#!/bin/bash
# RENDER SHELL COMMANDS - Download Updated Databases from Google Drive
# Updated: November 15, 2025 - After user replaced files in Drive
# FILE_IDs retrieved via get_drive_file_ids.py

# Navigate to data directory
cd /data

# Backup existing databases
echo "Creating backup..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null
echo "Backup complete"

# Download updated databases using curl (wget not available)
echo "Downloading sessions.db (0.71 MB)..."
curl -L 'https://drive.google.com/uc?export=download&id=1rIdxHdtNA3EbX4qxMtmYCH54ABksXVOl' -o sessions.db

echo "Downloading synergy_sessions.db (0.21 MB)..."
curl -L 'https://drive.google.com/uc?export=download&id=1-oeXwkjnmmv1YhPkorfF1l8NKyAqzTpT' -o synergy_sessions.db

echo "Downloading ai_infrastructure.db (0.61 MB)..."
curl -L 'https://drive.google.com/uc?export=download&id=1-rPnKW17I0X4d0rm9QlLm_4713fgcmb9' -o ai_infrastructure.db

echo "Downloading kanban_analytics.db (0.62 MB)..."
curl -L 'https://drive.google.com/uc?export=download&id=1ER9szXpTqliIjRTsqdFTWoiFc3AfNI2R' -o kanban_analytics.db

echo "Downloading stock_data.db (8.58 MB)..."
curl -L 'https://drive.google.com/uc?export=download&id=1fd9Z0zJ_7ajg-Bu8sB3WM2bRSa1UmDVu' -o stock_data.db

# Verify downloads
echo "Verifying downloads..."
ls -lh *.db

# Check OAuth columns in ai_infrastructure.db
echo "Checking OAuth columns..."
sqlite3 ai_infrastructure.db "SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';"

# Check threads table in sessions.db
echo "Checking threads table..."
sqlite3 sessions.db "SELECT COUNT(*) as thread_count FROM threads;"

echo "Download complete! Ready to restart service."
