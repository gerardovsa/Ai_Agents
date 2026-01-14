# PowerShell Script: Comment Out All font-weight Declarations (V2 - Robust)
# Target: All CSS and HTML files in AI_agents project  
# Excludes: FontAwesome files, ui-standards.css
# Date: December 3, 2025

Write-Host "======================================================================"
Write-Host " FONT-WEIGHT COMMENT SCRIPT V2" -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host ""

$projectRoot = "c:\Users\gpoli\GIT\AI_agents"
$stats = @{ FilesScanned = 0; FilesModified = 0; TotalReplacements = 0; Errors = 0 }

# Get all CSS and HTML files, excluding problem areas
$files = Get-ChildItem -Path $projectRoot -Include "*.css","*.html" -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $path = $_.FullName
    $path -notlike "*\docs\Fontawesome\*" -and
    $path -notlike "*\node_modules\*" -and
    $path -notlike "*\.git\*" -and
    $_.Name -ne "ui-standards.css"
}

Write-Host "Found $($files.Count) files to process" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $files) {
    $stats.FilesScanned++
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
        $originalContent = $content
        
        # Replace font-weight lines with commented versions
        $content = $content -replace '(?m)^(\s*)(font-weight:\s*[^;]+;)(\s*)$', '$1/* $2 */$3'
        
        if ($content -ne $originalContent) {
            $replacements = ([regex]::Matches($originalContent, '(?m)^(\s*)(font-weight:\s*[^;]+;)(\s*)$')).Count
            
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline -ErrorAction Stop
            
            $stats.FilesModified++
            $stats.TotalReplacements += $replacements
            
            $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart('\')
            Write-Host "[OK] $relativePath ($replacements replacements)" -ForegroundColor Green
        }
    }
    catch {
        $stats.Errors++
    }
}

Write-Host ""
Write-Host "======================================================================"
Write-Host " SUMMARY" -ForegroundColor Yellow  
Write-Host "======================================================================"
Write-Host "Files Scanned:    $($stats.FilesScanned)" -ForegroundColor Cyan
Write-Host "Files Modified:   $($stats.FilesModified)" -ForegroundColor Green
Write-Host "Total Commented:  $($stats.TotalReplacements)" -ForegroundColor Yellow
Write-Host "Errors:           $($stats.Errors)" -ForegroundColor $(if ($stats.Errors -gt 0) { "Red" } else { "Green" })
Write-Host "======================================================================"
Write-Host ""

if ($stats.FilesModified -gt 0) {
    Write-Host "[OK] COMPLETE - All font-weight declarations commented out" -ForegroundColor Green
    Write-Host ""
    Write-Host "TO UNDO: git checkout -- ." -ForegroundColor Gray
} else {
    Write-Host "[WARN] NO CHANGES MADE" -ForegroundColor Yellow
}

Write-Host ""
