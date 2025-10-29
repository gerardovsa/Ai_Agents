# Direct Profile Update Script
# This will find and replace the BISTART function directly

Write-Host "🔧 Updating BISTART function directly..." -ForegroundColor Cyan

# Read the entire profile
$profilePath = $PROFILE
$content = Get-Content $profilePath -Raw

# Check if BISTART exists
if ($content -match 'function BISTART') {
    Write-Host " Found BISTART function" -ForegroundColor Green
    
    # Find the start of the function
    $lines = Get-Content $profilePath
    $startLine = -1
    $endLine = -1
    $braceCount = 0
    $inFunction = $false
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match 'function BISTART') {
            $startLine = $i
            $inFunction = $true
            $braceCount = 0
        }
        
        if ($inFunction) {
            # Count opening braces
            $braceCount += ($lines[$i] -split '\{').Count - 1
            # Count closing braces
            $braceCount -= ($lines[$i] -split '\}').Count - 1
            
            if ($braceCount -eq 0 -and $lines[$i] -match '\}') {
                $endLine = $i
                break
            }
        }
    }
    
    if ($startLine -ge 0 -and $endLine -ge 0) {
        Write-Host "📍 Found function from line $($startLine + 1) to $($endLine + 1)" -ForegroundColor Yellow
        
        # Read new function
        $newFunction = Get-Content "C:\Users\gpoli\GIT\AI_agents\BISTART_NEW_VERSION.txt" -Raw
        
        # Build new profile content
        $newLines = @()
        if ($startLine -gt 0) {
            $newLines += $lines[0..($startLine - 1)]
        }
        $newLines += $newFunction.Trim()
        if ($endLine + 1 -lt $lines.Count) {
            $newLines += $lines[($endLine + 1)..($lines.Count - 1)]
        }
        
        # Save
        $newLines -join "`r`n" | Set-Content $profilePath -Force
        
        Write-Host "✅ BISTART function updated!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Reloading profile..." -ForegroundColor Cyan
        . $PROFILE
        Write-Host ""
        Write-Host "✅ Done! Try running: BISTART" -ForegroundColor Green
    } else {
        Write-Host "❌ Could not find function boundaries" -ForegroundColor Red
    }
} else {
    Write-Host "❌ BISTART function not found in profile" -ForegroundColor Red
}
