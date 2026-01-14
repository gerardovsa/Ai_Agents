#!/bin/bash
# ===============================================================================
# RENDER DATABASE UPLOAD - COPY AND PASTE INTO RENDER SHELL
# ===============================================================================
# 
# STATUS: SUCCESSFULLY UPLOADED - November 14, 2025
# All 5 databases downloaded from Google Drive to Render /data folder
# 
# Open Render Shell: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/shell
# Then paste ALL commands below and press Enter
#
# ===============================================================================

cd /data
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'No existing databases to backup'

echo ''
echo '===== DOWNLOADING DATABASES FROM GOOGLE DRIVE ====='
echo ''

# synergy_sessions.db (220K)
echo 'Downloading synergy_sessions.db...'
curl -L 'https://drive.google.com/uc?export=download&id=1-oeXwkjnmmv1YhPkorfF1l8NKyAqzTpT' -o synergy_sessions.db

# ai_infrastructure.db (624K) - CRITICAL FOR OAUTH
echo 'Downloading ai_infrastructure.db...'
curl -L 'https://drive.google.com/uc?export=download&id=1-rPnKW17I0X4d0rm9QlLm_4713fgcmb9' -o ai_infrastructure.db

# sessions.db (716K)
echo 'Downloading sessions.db...'
curl -L 'https://drive.google.com/uc?export=download&id=1rIdxHdtNA3EbX4qxMtmYCH54ABksXVOl' -o sessions.db

# kanban_analytics.db (640K)
echo 'Downloading kanban_analytics.db...'
curl -L 'https://drive.google.com/uc?export=download&id=1ER9szXpTqliIjRTsqdFTWoiFc3AfNI2R' -o kanban_analytics.db

# stock_data.db (8.6M)
echo 'Downloading stock_data.db...'
curl -L 'https://drive.google.com/uc?export=download&id=1fd9Z0zJ_7ajg-Bu8sB3WM2bRSa1UmDVu' -o stock_data.db

echo ''
echo '===== VERIFICATION ====='
echo ''
ls -lh *.db

echo ''
echo '===== UPLOAD COMPLETE! ====='
echo ''
echo 'NEXT STEPS:'
echo '1. Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0'
echo '2. Click: Manual Deploy → Clear build cache & deploy'
echo '3. Wait 2-3 minutes for rebuild'
echo '4. Test OAuth login at: https://ai-agents-backend-singapore.onrender.com'
echo ''
echo 'NOTE: OAuth columns (has_google_oauth, has_microsoft_oauth) are in the new database'
echo 'The "no such column" error should be FIXED after restart!'
echo ''
