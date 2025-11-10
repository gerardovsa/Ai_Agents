# Final Comprehensive Cleanup Script
# Removes backup folders and consolidates scattered documentation

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Final Comprehensive Cleanup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = "C:\Users\gpoli\GIT\AI_agents"
Set-Location $ProjectRoot

# ============================================
# Step 1: Remove old backup folder (40 files)
# ============================================
Write-Host "Step 1: Removing old backup folder..." -ForegroundColor Yellow

$backupFolder = "AI_infrastructure_BACKUP_20251023_224947"
if (Test-Path $backupFolder) {
    Remove-Item -Path $backupFolder -Recurse -Force
    Write-Host "  [REMOVED] $backupFolder" -ForegroundColor Red
} else {
    Write-Host "  [SKIP] Backup folder not found" -ForegroundColor Gray
}

# ============================================
# Step 2: Archive AI_infrastructure docs (40 files)
# ============================================
Write-Host "`nStep 2: Archiving AI_infrastructure documentation..." -ForegroundColor Yellow

$aiInfrastructureDocs = Get-ChildItem -Path "AI_infrastructure" -Filter "*.md" -File -ErrorAction SilentlyContinue

if ($aiInfrastructureDocs.Count -gt 0) {
    New-Item -ItemType Directory -Path "docs\archive\ai_infrastructure" -Force | Out-Null
    
    $count = 0
    foreach ($doc in $aiInfrastructureDocs) {
        Move-Item -Path $doc.FullName -Destination "docs\archive\ai_infrastructure\" -Force
        $count++
    }
    Write-Host "  [ARCHIVED] $count files from AI_infrastructure" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] No markdown files found in AI_infrastructure" -ForegroundColor Gray
}

# ============================================
# Step 3: Archive UI documentation (25 files)
# ============================================
Write-Host "`nStep 3: Archiving UI documentation..." -ForegroundColor Yellow

$uiDocs = Get-ChildItem -Path "UI" -Filter "*.md" -File -ErrorAction SilentlyContinue

if ($uiDocs.Count -gt 0) {
    # UI archive already exists, ensure it's there
    New-Item -ItemType Directory -Path "docs\archive\ui" -Force | Out-Null
    
    $count = 0
    foreach ($doc in $uiDocs) {
        Move-Item -Path $doc.FullName -Destination "docs\archive\ui\" -Force
        $count++
    }
    Write-Host "  [ARCHIVED] $count files from UI" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] No markdown files found in UI" -ForegroundColor Gray
}

# ============================================
# Step 4: Archive tools documentation (10 files)
# ============================================
Write-Host "`nStep 4: Archiving tools documentation..." -ForegroundColor Yellow

$toolsDocs = Get-ChildItem -Path "tools" -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue

if ($toolsDocs.Count -gt 0) {
    New-Item -ItemType Directory -Path "docs\archive\tools" -Force | Out-Null
    
    $count = 0
    foreach ($doc in $toolsDocs) {
        $targetPath = Join-Path "docs\archive\tools" $doc.Name
        Move-Item -Path $doc.FullName -Destination $targetPath -Force
        $count++
    }
    Write-Host "  [ARCHIVED] $count files from tools" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] No markdown files found in tools" -ForegroundColor Gray
}

# ============================================
# Step 5: Archive platform-specific docs
# ============================================
Write-Host "`nStep 5: Archiving platform-specific documentation..." -ForegroundColor Yellow

$platformFolders = @(
    "google_workspace",
    "Microsoft_365_Connection",
    "Cloudflare",
    "Supabase",
    "Render_backend",
    "Woocommerce"
)

$totalPlatformDocs = 0
foreach ($folder in $platformFolders) {
    if (Test-Path $folder) {
        $docs = Get-ChildItem -Path $folder -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue
        
        if ($docs.Count -gt 0) {
            $archivePath = "docs\archive\platforms\$folder"
            New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
            
            foreach ($doc in $docs) {
                $targetPath = Join-Path $archivePath $doc.Name
                Move-Item -Path $doc.FullName -Destination $targetPath -Force
                $totalPlatformDocs++
            }
            Write-Host "  [ARCHIVED] $($docs.Count) files from $folder" -ForegroundColor Green
        }
    }
}

if ($totalPlatformDocs -eq 0) {
    Write-Host "  [SKIP] No platform documentation found" -ForegroundColor Gray
}

# ============================================
# Step 6: Archive any remaining scattered docs
# ============================================
Write-Host "`nStep 6: Finding any remaining scattered documentation..." -ForegroundColor Yellow

$excludeFolders = @("docs", "archive", ".git", "node_modules", "__pycache__", "data", ".pytest_cache")
$scatteredDocs = Get-ChildItem -Path . -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { 
        $path = $_.FullName
        $exclude = $false
        foreach ($folder in $excludeFolders) {
            if ($path -like "*\$folder\*") {
                $exclude = $true
                break
            }
        }
        -not $exclude -and $_.Directory.FullName -ne $ProjectRoot
    }

if ($scatteredDocs.Count -gt 0) {
    New-Item -ItemType Directory -Path "docs\archive\miscellaneous" -Force | Out-Null
    
    foreach ($doc in $scatteredDocs) {
        $relativePath = $doc.FullName.Substring($ProjectRoot.Length + 1)
        $targetPath = Join-Path "docs\archive\miscellaneous" $doc.Name
        
        # Handle filename conflicts
        $counter = 1
        while (Test-Path $targetPath) {
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($doc.Name)
            $extension = [System.IO.Path]::GetExtension($doc.Name)
            $targetPath = Join-Path "docs\archive\miscellaneous" "$baseName`_$counter$extension"
            $counter++
        }
        
        Move-Item -Path $doc.FullName -Destination $targetPath -Force
        Write-Host "  [ARCHIVED] $relativePath" -ForegroundColor Green
    }
} else {
    Write-Host "  [SKIP] No scattered documentation found" -ForegroundColor Gray
}

# ============================================
# Step 7: Generate final report
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Count remaining docs in root
$rootDocs = (Get-ChildItem -Path . -Filter "*.md" -File | Measure-Object).Count
Write-Host "`nRoot folder: $rootDocs markdown files" -ForegroundColor White

# Count docs in archive
$archiveDocs = (Get-ChildItem -Path "docs\archive" -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "Archive: $archiveDocs markdown files" -ForegroundColor White

# Count docs in docs/features
$featureDocs = (Get-ChildItem -Path "docs\features" -Filter "*.md" -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "Features: $featureDocs markdown files" -ForegroundColor White

# Total project docs (excluding archive)
$activeDocs = (Get-ChildItem -Path . -Filter "*.md" -Recurse -File | Where-Object { $_.FullName -notlike "*\archive\*" -and $_.FullName -notlike "*\.git\*" -and $_.FullName -notlike "*node_modules*" } | Measure-Object).Count
Write-Host "`nActive documentation: $activeDocs files" -ForegroundColor Cyan
Write-Host "Archived documentation: $archiveDocs files" -ForegroundColor Yellow

Write-Host "`nWorkspace is now clean!" -ForegroundColor Green
Write-Host ""
