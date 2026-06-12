# Verify UI Path Fix - Check for remaining broken paths
# Run this after applying the fix to find any remaining issues

$htmlFile = "c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
$uiDir = "c:\Users\gpoli\GIT\AI_agents\UI"

Write-Host "`n=====================================================`n" -ForegroundColor Cyan
Write-Host "  UI PATH VERIFICATION SCRIPT" -ForegroundColor Cyan  
Write-Host "`n=====================================================`n" -ForegroundColor Cyan

Write-Host "[1/3] Extracting paths from HTML..." -ForegroundColor Yellow
$content = Get-Content $htmlFile -Raw -Encoding UTF8

# Extract all CSS/JS paths
$cssPaths = [regex]::Matches($content, 'href="([^"]+\.css[^"]*)"') | ForEach-Object { $_.Groups[1].Value }
$jsPaths = [regex]::Matches($content, 'src="([^"]+\.js[^"]*)"') | ForEach-Object { $_.Groups[1].Value }

# Filter to local paths only (exclude CDN URLs)
$localCssPaths = $cssPaths | Where-Object { $_ -notmatch '^https?://' }
$localJsPaths = $jsPaths | Where-Object { $_ -notmatch '^https?://' }

$totalPaths = $localCssPaths.Count + $localJsPaths.Count

Write-Host "[2/3] Checking if files exist..." -ForegroundColor Yellow
Write-Host "  Total local CSS files: $($localCssPaths.Count)" -ForegroundColor White
Write-Host "  Total local JS files: $($localJsPaths.Count)" -ForegroundColor White
Write-Host ""

$missing = @()
$found = 0

foreach ($path in $localCssPaths) {
    $cleanPath = ($path -split '\?')[0]  # Remove query params
    $fullPath = Join-Path $uiDir $cleanPath
    if (-not (Test-Path $fullPath)) {
        $missing += "❌ CSS: $cleanPath"
    } else {
        $found++
    }
}

foreach ($path in $localJsPaths) {
    $cleanPath = ($path -split '\?')[0]  # Remove query params
    $fullPath = Join-Path $uiDir $cleanPath
    if (-not (Test-Path $fullPath)) {
        $missing += "❌ JS: $cleanPath"
    } else {
        $found++
    }
}

Write-Host "[3/3] Results..." -ForegroundColor Yellow
Write-Host ""

if ($missing.Count -eq 0) {
    Write-Host "=====================================================`n" -ForegroundColor Green
    Write-Host "  ✅ SUCCESS - ALL FILES FOUND!" -ForegroundColor Green
    Write-Host "`n=====================================================`n" -ForegroundColor Green
    Write-Host "  Found: $found / $totalPaths files" -ForegroundColor White
    Write-Host "  Missing: 0 files" -ForegroundColor White
    Write-Host "`n  No 404 errors expected!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "=====================================================`n" -ForegroundColor Red
    Write-Host "  ⚠️  MISSING FILES DETECTED" -ForegroundColor Red
    Write-Host "`n=====================================================`n" -ForegroundColor Red
    Write-Host "  Found: $found / $totalPaths files" -ForegroundColor White
    Write-Host "  Missing: $($missing.Count) files`n" -ForegroundColor Red
    
    Write-Host "MISSING FILES:" -ForegroundColor Yellow
    foreach ($file in $missing) {
        Write-Host "  $file" -ForegroundColor White
    }
    Write-Host ""
}

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
if ($missing.Count -eq 0) {
    Write-Host "1. Restart BISTART" -ForegroundColor White
    Write-Host "2. Open browser console (F12)" -ForegroundColor White
    Write-Host "3. Verify zero 404 errors" -ForegroundColor White
} else {
    Write-Host "1. Investigate missing files" -ForegroundColor White
    Write-Host "2. Either fix paths or create missing files" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
}
Write-Host ""
