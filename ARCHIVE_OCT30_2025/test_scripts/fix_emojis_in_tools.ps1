# Fix Emoji Encoding Errors in Tool Implementations
# Replaces emoji characters with text markers

Write-Host "`n=== FIXING EMOJI ENCODING ERRORS ===" -ForegroundColor Cyan
Write-Host "Replacing emoji characters in tool implementation files...`n" -ForegroundColor Yellow

$toolsPath = "C:\Users\gpoli\GIT\AI_agents\tools\implementations"
$count = 0

# Get all Python files in implementations
$files = Get-ChildItem -Path $toolsPath -Filter "*.py" -File

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $originalContent = $content
    
    # Replace common emojis with text markers
    $content = $content -replace '✅', '[OK]'
    $content = $content -replace '❌', '[ERROR]'
    $content = $content -replace '⚠️', '[WARN]'
    $content = $content -replace '🔧', '[CONFIG]'
    $content = $content -replace '📦', '[LOAD]'
    $content = $content -replace '🎉', '[SUCCESS]'
    $content = $content -replace '⏳', '[WAIT]'
    $content = $content -replace '📊', '[CHART]'
    $content = $content -replace '🔄', '[SYNC]'
    $content = $content -replace '💡', '[INFO]'
    
    # Check if any changes were made
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "[FIXED] $($file.Name)" -ForegroundColor Green
        $count++
    }
}

Write-Host "`n=== COMPLETE ===" -ForegroundColor Cyan
Write-Host "Fixed $count files" -ForegroundColor Green
Write-Host "`nNow restart Flask: cd AI_infrastructure ; python flask_app.py`n" -ForegroundColor Yellow
