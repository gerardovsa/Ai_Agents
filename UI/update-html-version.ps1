# HTML Version Updater
# Run this after making changes to business-ai-platform-v2.html

$htmlFile = "c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"

Write-Host "`n🔄 Updating HTML Version..." -ForegroundColor Cyan

# Read file
$content = Get-Content $htmlFile -Raw

# Update version
$oldPattern = "const HTML_VERSION = '[^']+'"
$newVersion = "const HTML_VERSION = '$timestamp'"

if ($content -match $oldPattern) {
    $content = $content -replace $oldPattern, $newVersion
    Set-Content $htmlFile -Value $content -NoNewline
    Write-Host "✅ Updated to version: $timestamp" -ForegroundColor Green
    Write-Host "`nNext time you refresh browser, it will auto-reload with new HTML!" -ForegroundColor Yellow
}
else {
    Write-Host "❌ Version pattern not found in file" -ForegroundColor Red
}
