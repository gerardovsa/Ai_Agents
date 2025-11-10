# Manual Update Script for BISTART
# Run this to manually update your PowerShell profile

Write-Host "📝 Manual BISTART Update" -ForegroundColor Cyan
Write-Host ""
Write-Host "I'll open your PowerShell profile in notepad." -ForegroundColor Yellow
Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Find the section that starts with: function BISTART {" -ForegroundColor White
Write-Host "2. Delete the ENTIRE function (from 'function BISTART {' to the matching '}' )" -ForegroundColor White
Write-Host "3. Copy the NEW function from BISTART_NEW_VERSION.txt (opening now)" -ForegroundColor White
Write-Host "4. Paste it where the old function was" -ForegroundColor White
Write-Host "5. Save and close both files" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open the files..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open profile
notepad $PROFILE

# Open new version
notepad "C:\Users\gpoli\GIT\AI_agents\BISTART_NEW_VERSION.txt"

Write-Host ""
Write-Host "After editing, run: . `$PROFILE" -ForegroundColor Cyan
Write-Host ""
