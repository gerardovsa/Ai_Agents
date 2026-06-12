# Fix Remaining UI Paths - November 30, 2025 (Round 2)
# Fixes the 13 remaining missing file paths

$htmlFile = "c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"

Write-Host "`n=====================================================`n" -ForegroundColor Cyan
Write-Host "  UI PATH FIX - ROUND 2" -ForegroundColor Cyan  
Write-Host "`n=====================================================`n" -ForegroundColor Cyan

Write-Host "[1/3] Reading HTML file..." -ForegroundColor Yellow
$content = Get-Content $htmlFile -Raw -Encoding UTF8

Write-Host "[2/3] Fixing remaining paths..." -ForegroundColor Yellow

$changes = @()

# Fix: shared/prompt-library/ -> modules_internal/prompt-library/
$count = ([regex]::Matches($content, 'shared/prompt-library/')).Count
if ($count -gt 0) {
    $content = $content -replace 'shared/prompt-library/', 'modules_internal/prompt-library/'
    $changes += "  - Fixed $count references: shared/prompt-library/ -> modules_internal/prompt-library/"
}

# Fix: modules_external/settings-sidebar/ -> modules_internal/settings-sidebar/
$count = ([regex]::Matches($content, 'modules_external/settings-sidebar/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules_external/settings-sidebar/', 'modules_internal/settings-sidebar/'
    $changes += "  - Fixed $count references: modules_external/settings-sidebar/ -> modules_internal/settings-sidebar/"
}

# Fix: shared/shared/message_renderer.js -> shared/utilities/message_renderer.js
$count = ([regex]::Matches($content, 'shared/shared/message_renderer\.js')).Count
if ($count -gt 0) {
    $content = $content -replace 'shared/shared/message_renderer\.js', 'shared/utilities/message_renderer.js'
    $changes += "  - Fixed $count references: shared/shared/message_renderer.js -> shared/utilities/message_renderer.js"
}

# Fix: shared/js/agent-status-indicator.js -> modules_internal/agent-status-indicator.js
$count = ([regex]::Matches($content, 'shared/js/agent-status-indicator\.js')).Count
if ($count -gt 0) {
    $content = $content -replace 'shared/js/agent-status-indicator\.js', 'modules_internal/agent-status-indicator.js'
    $changes += "  - Fixed $count references: shared/js/agent-status-indicator.js -> modules_internal/agent-status-indicator.js"
}

# Fix: modules/transcription/* -> modules_internal/transcription/* (JavaScript files that weren't caught)
$count = ([regex]::Matches($content, 'src="modules/transcription/')).Count
if ($count -gt 0) {
    $content = $content -replace 'src="modules/transcription/', 'src="modules_internal/transcription/'
    $changes += "  - Fixed $count references: src=modules/transcription/ -> src=modules_internal/transcription/"
}

# Fix: fetch('modules/transcription/...html') -> fetch('modules_internal/transcription/...html')
$count = ([regex]::Matches($content, "fetch\('modules/transcription/")).Count
if ($count -gt 0) {
    $content = $content -replace "fetch\('modules/transcription/", "fetch('modules_internal/transcription/"
    $changes += "  - Fixed $count references: fetch('modules/transcription/ -> fetch('modules_internal/transcription/"
}

# Note: automation-thread-integration.js and woocommerce.js might not exist yet (feature modules)
# We'll leave those as-is and they can be created later if needed

Write-Host "[3/3] Writing updated HTML..." -ForegroundColor Yellow
$content | Set-Content $htmlFile -Encoding UTF8 -NoNewline

Write-Host ""
Write-Host "CHANGES APPLIED:" -ForegroundColor Green
foreach ($change in $changes) {
    Write-Host $change -ForegroundColor White
}

Write-Host "`n=====================================================`n" -ForegroundColor Cyan
Write-Host "  FIX ROUND 2 COMPLETE" -ForegroundColor Green
Write-Host "`n=====================================================`n" -ForegroundColor Cyan

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Run verify_ui_paths.ps1 to check remaining issues" -ForegroundColor White
Write-Host "2. Restart BISTART" -ForegroundColor White  
Write-Host "3. Check browser console`n" -ForegroundColor White
