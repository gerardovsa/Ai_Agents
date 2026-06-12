# PowerShell Script: Comment Out All font-weight Declarations
# Target: All CSS and HTML files in AI_agents project
# Excludes: FontAwesome files, ui-standards.css (uses CSS variables)
# Date: December 3, 2025

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host " FONT-WEIGHT COMMENT SCRIPT" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Configuration
$projectRoot = "c:\Users\gpoli\GIT\AI_agents"
$backupFolder = Join-Path $projectRoot "_font_weight_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Exclusion patterns
$excludePaths = @(
    "*\docs\Fontawesome\*",
    "*\node_modules\*",
    "*\.git\*",
    "*\venv\*",
    "*\__pycache__\*"
)

$excludeFiles = @(
    "ui-standards.css"  # Keep this - uses CSS variables
)

# Statistics
$stats = @{
    FilesScanned      = 0
    FilesModified     = 0
    TotalReplacements = 0
    BackupCreated     = $false
    Errors            = @()
}

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  Project Root: $projectRoot"
Write-Host "  Backup Folder: $backupFolder"
Write-Host "  Excluded: FontAwesome, ui-standards.css, node_modules"
Write-Host ""

# Create backup folder
try {
    New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null
    $stats.BackupCreated = $true
    Write-Host "[OK] Backup folder created" -ForegroundColor Green
}
catch {
    Write-Host "[ERR] Failed to create backup folder: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Scanning files..." -ForegroundColor Yellow
Write-Host ""

# Find all CSS and HTML files
$files = Get-ChildItem -Path $projectRoot -Include "*.css", "*.html" -Recurse -File | Where-Object {
    $file = $_
    $filePath = $file.FullName
    
    # Check if file matches exclusion patterns
    $excluded = $false
    foreach ($pattern in $excludePaths) {
        if ($filePath -like $pattern) {
            $excluded = $true
            break
        }
    }
    
    # Check if filename is in exclusion list
    if ($excludeFiles -contains $file.Name) {
        $excluded = $true
    }
    
    -not $excluded
}

Write-Host "Found $($files.Count) files to process" -ForegroundColor Cyan
Write-Host ""

# Process each file
foreach ($file in $files) {
    $stats.FilesScanned++
    $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart('\')
    
    try {
        # Read file content
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        $originalContent = $content
        $replacements = 0
        
        # Pattern 1: Comment out standalone font-weight lines
        # Matches lines with font-weight declarations
        $pattern1 = '(?m)^(\s*)(font-weight:\s*[^;]+;)(\s*)$'
        $replacement1 = '$1/* $2 */$3'
        
        if ($content -match $pattern1) {
            $content = $content -replace $pattern1, $replacement1
            $replacements = ([regex]::Matches($originalContent, $pattern1)).Count
        }
        
        # Only modify file if replacements were made
        if ($replacements -gt 0) {
            # Backup original file
            $backupPath = Join-Path $backupFolder $relativePath
            $backupDir = Split-Path -Parent $backupPath
            
            if (-not (Test-Path $backupDir)) {
                New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            }
            
            Copy-Item -Path $file.FullName -Destination $backupPath -Force
            
            # Write modified content
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            
            $stats.FilesModified++
            $stats.TotalReplacements += $replacements
            
            Write-Host "[OK] " -NoNewline -ForegroundColor Green
            Write-Host "$relativePath" -NoNewline -ForegroundColor White
            Write-Host " ($replacements replacements)" -ForegroundColor Gray
        }
        
    }
    catch {
        $stats.Errors += "Error processing $($relativePath): $_"
        Write-Host "[ERR] " -NoNewline -ForegroundColor Red
        Write-Host "$relativePath" -NoNewline -ForegroundColor White
        Write-Host " (ERROR: $_)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host " SUMMARY" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

Write-Host "Files Scanned:    " -NoNewline -ForegroundColor White
Write-Host $stats.FilesScanned -ForegroundColor Cyan

Write-Host "Files Modified:   " -NoNewline -ForegroundColor White
Write-Host $stats.FilesModified -ForegroundColor Green

Write-Host "Total font-weight declarations commented: " -NoNewline -ForegroundColor White
Write-Host $stats.TotalReplacements -ForegroundColor Yellow

Write-Host ""

if ($stats.Errors.Count -gt 0) {
    Write-Host "ERRORS:" -ForegroundColor Red
    foreach ($error in $stats.Errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "Backup Location: " -NoNewline -ForegroundColor White
Write-Host $backupFolder -ForegroundColor Cyan

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Restore instructions
Write-Host "TO RESTORE:" -ForegroundColor Yellow
Write-Host "  Copy files from backup folder back to original locations" -ForegroundColor Gray
Write-Host ""
Write-Host "TO UNDO (Quick):" -ForegroundColor Yellow
Write-Host "  Run: " -NoNewline -ForegroundColor Gray
Write-Host "git checkout -- ." -ForegroundColor White -NoNewline
Write-Host " (if files are tracked by Git)" -ForegroundColor Gray
Write-Host ""

if ($stats.FilesModified -gt 0) {
    Write-Host "[OK] COMPLETE - All font-weight declarations have been commented out" -ForegroundColor Green
}
else {
    Write-Host "[WARN] NO CHANGES - No font-weight declarations found" -ForegroundColor Yellow
}

Write-Host ""
