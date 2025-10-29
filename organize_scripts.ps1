# AI_agents Script Organization
# Moves root scripts to organized scripts/ folder structure

Write-Host "`nORGANIZING SCRIPTS`n" -ForegroundColor Cyan

$moveCount = 0

# 1. STARTUP SCRIPTS
Write-Host "Moving startup scripts..." -ForegroundColor Yellow
"BISTART.ps1","BISTOP.ps1","chat.ps1","SYNERGY_START.ps1","SYNERGY_START.bat" | ForEach-Object {
    if (Test-Path $_) { Move-Item $_ "scripts\startup\" -Force; Write-Host "  Moved: $_" -ForegroundColor Green; $script:moveCount++ }
}

# Copy shortcuts back to root
Copy-Item "scripts\startup\BISTART.ps1" "BISTART.ps1" -Force
Copy-Item "scripts\startup\chat.ps1" "chat.ps1" -Force
Write-Host "  Created root shortcuts" -ForegroundColor Green

# 2. ARCHIVE SUPERSEDED
Write-Host "`nArchiving superseded scripts..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "docs\archive\scripts" -Force | Out-Null
"BISTART_DIRECT_UPDATE.ps1","BISTART_MANUAL_UPDATE.ps1","BISTART_UPDATED_FUNCTION.ps1","SIMPLE_BISTART_UPDATE.ps1","UPDATE_BISTART.ps1","UPDATE_NOW.ps1" | ForEach-Object {
    if (Test-Path $_) { Move-Item $_ "docs\archive\scripts\" -Force; Write-Host "  Archived: $_" -ForegroundColor Gray; $script:moveCount++ }
}

# 3. SETUP SCRIPTS
Write-Host "`nMoving setup scripts..." -ForegroundColor Yellow
"setup_microsoft_login.ps1","setup_master_account.py","UPDATE_PROFILE_TO_5001.ps1" | ForEach-Object {
    if (Test-Path $_) { Move-Item $_ "scripts\setup\" -Force; Write-Host "  Moved: $_" -ForegroundColor Green; $script:moveCount++ }
}

# 4. TESTING SCRIPTS
Write-Host "`nMoving testing scripts..." -ForegroundColor Yellow
"test_kanban_integration.py","test_oauth_all.py","test_task_sync.py","test_unified_oauth.py","check_db_schema.py","check_gmail_tools.py","check_routes.py","table_structure_analysis.py" | ForEach-Object {
    if (Test-Path $_) { Move-Item $_ "scripts\testing\" -Force; Write-Host "  Moved: $_" -ForegroundColor Green; $script:moveCount++ }
}

# 5. MAINTENANCE SCRIPTS
Write-Host "`nMoving maintenance scripts..." -ForegroundColor Yellow
"cleanup_final.ps1","execute_phase2_cleanup.ps1","final_comprehensive_cleanup.ps1" | ForEach-Object {
    if (Test-Path $_) { Move-Item $_ "scripts\maintenance\" -Force; Write-Host "  Moved: $_" -ForegroundColor Green; $script:moveCount++ }
}

# 6. DEPLOYMENT SCRIPTS
Write-Host "`nMoving deployment scripts..." -ForegroundColor Yellow
if (Test-Path "ai_agent_render_deploy.py") { Move-Item "ai_agent_render_deploy.py" "scripts\deployment\" -Force; Write-Host "  Moved: ai_agent_render_deploy.py" -ForegroundColor Green; $moveCount++ }

# 7. UTILITY SCRIPTS
Write-Host "`nMoving utility scripts..." -ForegroundColor Yellow
"create_doc_with_chart_images.py","create_professional_charts.py","create_professional_charts_with_folder.py","task_sync_universal.py" | ForEach-Object {
    if (Test-Path $_) { Move-Item $_ "scripts\utilities\" -Force; Write-Host "  Moved: $_" -ForegroundColor Green; $script:moveCount++ }
}

# 8. MIGRATIONS
Write-Host "`nMoving database scripts..." -ForegroundColor Yellow
if (-not (Test-Path "migrations")) { New-Item -ItemType Directory -Path "migrations" -Force | Out-Null }
if (Test-Path "run_migration.py") { Move-Item "run_migration.py" "migrations\" -Force; Write-Host "  Moved: run_migration.py" -ForegroundColor Green; $moveCount++ }

# 9. ARCHIVE OLD
Write-Host "`nArchiving old scripts..." -ForegroundColor Yellow
if (Test-Path "google_sheets_auth_OLD.py") { Move-Item "google_sheets_auth_OLD.py" "docs\archive\scripts\" -Force; Write-Host "  Archived: google_sheets_auth_OLD.py" -ForegroundColor Gray; $moveCount++ }

Write-Host "`nMoved/Archived: $moveCount files" -ForegroundColor Green
Write-Host "`nRoot scripts remaining:" -ForegroundColor Yellow
Get-ChildItem -Path . -File | Where-Object { $_.Extension -in @('.py', '.ps1', '.bat') } | Select-Object Name | Format-Table -HideTableHeaders
