# Simple BISTART Updater
# Replaces the BISTART function in your PowerShell profile

Write-Host "🔧 Updating BISTART function..." -ForegroundColor Cyan

try {
    # Read profile and new function
    $profileLines = Get-Content $PROFILE
    $newFunction = Get-Content "C:\Users\gpoli\GIT\AI_agents\BISTART_NEW_VERSION.txt"
    
    # Find function boundaries
    $startIdx = -1
    $endIdx = -1
    $braceDepth = 0
    
    for ($i = 0; $i -lt $profileLines.Count; $i++) {
        if ($profileLines[$i] -match 'function BISTART') {
            $startIdx = $i
            $braceDepth = 0
        }
        
        if ($startIdx -ge 0) {
            $braceDepth += [regex]::Matches($profileLines[$i], '\{').Count
            $braceDepth -= [regex]::Matches($profileLines[$i], '\}').Count
            
            if ($braceDepth -eq 0) {
                $endIdx = $i
                break
            }
        }
    }
    
    if ($startIdx -ge 0 -and $endIdx -ge 0) {
        Write-Host "Found BISTART at lines $($startIdx+1)-$($endIdx+1)" -ForegroundColor Green
        
        # Build new content
        $newContent = @()
        if ($startIdx -gt 0) {
            $newContent += $profileLines[0..($startIdx-1)]
        }
        $newContent += $newFunction
        if ($endIdx -lt $profileLines.Count-1) {
            $newContent += $profileLines[($endIdx+1)..($profileLines.Count-1)]
        }
        
        # Save
        $newContent | Out-File $PROFILE -Encoding UTF8 -Force
        
        Write-Host "Updated successfully!" -ForegroundColor Green
        Write-Host "Reloading profile..." -ForegroundColor Cyan
        . $PROFILE
        Write-Host "Done!" -ForegroundColor Green
    } else {
        Write-Host "Could not find BISTART function" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}
