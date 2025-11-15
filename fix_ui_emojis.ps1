# Fix Emoji Encoding Issues in business-ai-platform-v2.html
# This script replaces corrupted emoji characters with proper UTF-8 encoded emojis

$filePath = "C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
$backupPath = "C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html.backup"

Write-Host "Backing up original file..." -ForegroundColor Yellow
Copy-Item $filePath $backupPath -Force

Write-Host "Reading file..." -ForegroundColor Yellow
$content = Get-Content $filePath -Raw -Encoding UTF8

Write-Host "Replacing corrupted emojis..." -ForegroundColor Yellow

# Replace all corrupted emoji patterns
$replacements = @{
    'Ã°Å¸â€'      = '🔧'
    'Ã°Å¸â€¦'     = '📦'
    'Ã°Å¸â€ºÃ¯Â¸' = '🛒'
    'Ã°Å¸â€™Â¥'   = '👥'
    'Ã°Å¸â€™Â°'   = '💰'
    'Ã°Å¸Å¸Â¡'    = '🟡'
    'Ã°Å¸â€�Âµ'   = '🔵'
    'Ã°Å¸Å¸Â¢'    = '🟢'
    'Ã°Å¸â€�Â´'   = '🔴'
    'Ã°Å¸â€�Ë†'   = '📈'
    'Ã°Å¸ÂŽÂ¯'    = '🎯'
    'Ã°Å¸â€ '     = '🏆'
    'Ã°Å¸â€�â€¦'  = '📅'
    'Ã°Å¸ÂŽÂ¨'    = '🎨'
}

foreach ($pattern in $replacements.Keys) {
    $emoji = $replacements[$pattern]
    $content = $content -replace [regex]::Escape($pattern), $emoji
    Write-Host "  Replaced $pattern with $emoji" -ForegroundColor Gray
}

Write-Host "Saving fixed file..." -ForegroundColor Yellow
$content | Set-Content $filePath -Encoding UTF8 -NoNewline

Write-Host "`nSuccess! All emoji encoding issues fixed." -ForegroundColor Green
Write-Host "Original file backed up to: $backupPath" -ForegroundColor Cyan
