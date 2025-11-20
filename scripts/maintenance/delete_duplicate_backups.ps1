# Delete Duplicate Backup Files Script
# Removes .backup files and " copy.py" duplicates from AI_agents project

Write-Host "`n🗑️ Deleting Duplicate Backup Files" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$basePath = "c:\Users\gpoli\GIT\AI_agents"

# Find duplicate files
Write-Host "`n🔍 Scanning for duplicates..." -ForegroundColor Yellow

$copyFiles = Get-ChildItem -Path $basePath -Recurse -Filter "* copy.py" -File | 
    Where-Object { $_.FullName -like "*AI_agents*" }

$backupFiles = Get-ChildItem -Path $basePath -Recurse -Filter "*.backup" -File |
    Where-Object { $_.FullName -like "*AI_agents*" }

$allDuplicates = @($copyFiles) + @($backupFiles)

if ($allDuplicates.Count -eq 0) {
    Write-Host "`n✅ No duplicate files found!" -ForegroundColor Green
    exit
}

Write-Host "`n📋 Found $($allDuplicates.Count) duplicate files:" -ForegroundColor Cyan

foreach ($file in $allDuplicates) {
    $relativePath = $file.FullName.Replace("$basePath\", "")
    $size = [math]::Round($file.Length / 1KB, 2)
    Write-Host "  - $relativePath ($size KB)" -ForegroundColor White
}

# Calculate total size
$totalSize = ($allDuplicates | Measure-Object -Property Length -Sum).Sum
$totalSizeMB = [math]::Round($totalSize / 1MB, 2)

Write-Host "`n💾 Total size to free: $totalSizeMB MB" -ForegroundColor Yellow
Write-Host "`n⚠️  This will PERMANENTLY DELETE $($allDuplicates.Count) files" -ForegroundColor Red
$confirm = Read-Host "Continue? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "`n❌ Cancelled by user" -ForegroundColor Red
    exit
}

# Delete files
Write-Host "`n🗑️ Deleting files..." -ForegroundColor Yellow
$deleted = 0
$errors = 0

foreach ($file in $allDuplicates) {
    $relativePath = $file.FullName.Replace("$basePath\", "")
    try {
        Remove-Item -Path $file.FullName -Force
        Write-Host "  ✅ Deleted: $relativePath" -ForegroundColor Green
        $deleted++
    } catch {
        Write-Host "  ❌ Failed: $relativePath" -ForegroundColor Red
        Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
        $errors++
    }
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  Deleted: $deleted files" -ForegroundColor Green
Write-Host "  Errors: $errors files" -ForegroundColor $(if ($errors -gt 0) { "Red" } else { "Green" })
Write-Host "  Space freed: $totalSizeMB MB" -ForegroundColor Green

if ($deleted -gt 0) {
    Write-Host "`n✅ Cleanup complete!" -ForegroundColor Green
}

Write-Host "=" * 60 -ForegroundColor Cyan
