# PowerShell Script: Comment Out Remaining font-weight Declarations
# Catches files that were missed by the previous script
# Date: December 3, 2025

Write-Host "======================================================================"
Write-Host " COMMENT REMAINING FONT-WEIGHTS" -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host ""

$targetFiles = @(
    "c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\prompt-library\prompt-library.css",
    "c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\thread-manager\thread.css",
    "c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\thread-cards\thread-card-styles.css"
)

$stats = @{ FilesModified = 0; TotalReplacements = 0 }

foreach ($filePath in $targetFiles) {
    if (-not (Test-Path $filePath)) {
        Write-Host "[SKIP] File not found: $filePath" -ForegroundColor Yellow
        continue
    }
    
    try {
        $content = Get-Content -Path $filePath -Raw -Encoding UTF8
        $originalContent = $content
        
        # Replace all font-weight lines (not already commented, not using var())
        # Simpler pattern that catches all indentation styles
        $pattern = '(?m)^([ \t]*)(font-weight:\s*(?!var\()[^;]+;)([ \t]*)$'
        $replacement = '$1/* $2 */$3'
        
        $content = $content -replace $pattern, $replacement
        
        if ($content -ne $originalContent) {
            $replacements = ([regex]::Matches($originalContent, $pattern)).Count
            
            Set-Content -Path $filePath -Value $content -Encoding UTF8 -NoNewline
            
            $stats.FilesModified++
            $stats.TotalReplacements += $replacements
            
            $fileName = Split-Path $filePath -Leaf
            Write-Host "[OK] $fileName ($replacements replacements)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[ERR] Failed to process $filePath : $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "======================================================================"
Write-Host " SUMMARY" -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host "Files Modified:   $($stats.FilesModified)" -ForegroundColor Green
Write-Host "Total Commented:  $($stats.TotalReplacements)" -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host ""

if ($stats.FilesModified -gt 0) {
    Write-Host "[OK] COMPLETE - All remaining font-weight declarations commented" -ForegroundColor Green
}
else {
    Write-Host "[WARN] NO CHANGES MADE" -ForegroundColor Yellow
}

Write-Host ""
