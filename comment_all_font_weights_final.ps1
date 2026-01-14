# Final Font-Weight Comment Script - Catches ALL patterns
# December 4, 2025

Write-Host "======================================================================"
Write-Host " FINAL FONT-WEIGHT CLEANUP" -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host ""

$projectRoot = "c:\Users\gpoli\GIT\AI_agents"
$stats = @{ Total = 0; Files = 0 }

# Target specific files that still have uncommented font-weight
$targetFiles = @(
    "UI\modules_internal\thread-manager\thread.css",
    "UI\modules_internal\prompt-library\prompt-library.css", 
    "UI\modules_internal\thread-cards\thread-card-styles.css"
)

foreach ($relPath in $targetFiles) {
    $fullPath = Join-Path $projectRoot $relPath
    
    Write-Host "Processing: $relPath" -ForegroundColor Cyan
    
    $content = Get-Content $fullPath -Raw -Encoding UTF8
    $originalContent = $content
    
    # Pattern: Match ANY whitespace before font-weight (spaces or tabs)
    # Captures: (whitespace)(font-weight: value;)(optional whitespace/newline)
    $pattern = '(\s*)(font-weight:\s*[^;]+;)(\s*)'
    
    $matches = [regex]::Matches($content, $pattern)
    $count = 0
    
    # Replace each match that is NOT already commented
    foreach ($match in $matches) {
        $fullMatch = $match.Value
        # Check if already commented
        if ($fullMatch -notmatch '/\*.*font-weight.*\*/') {
            $whitespace = $match.Groups[1].Value
            $declaration = $match.Groups[2].Value
            $trailing = $match.Groups[3].Value
            
            $commented = "$whitespace/* $declaration */$trailing"
            $content = $content.Replace($fullMatch, $commented)
            $count++
        }
    }
    
    if ($count -gt 0) {
        Set-Content $fullPath -Value $content -Encoding UTF8 -NoNewline
        Write-Host "  [OK] Commented $count font-weight declarations" -ForegroundColor Green
        $stats.Total += $count
        $stats.Files++
    }
    else {
        Write-Host "  [SKIP] No uncommented font-weight found" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "======================================================================"
Write-Host " COMPLETE" -ForegroundColor Green
Write-Host "======================================================================"
Write-Host "Files Modified: $($stats.Files)" -ForegroundColor Cyan
Write-Host "Total Commented: $($stats.Total)" -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host ""
