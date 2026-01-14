# BISTART Updater
Write-Host "Updating BISTART function..." -ForegroundColor Cyan

$profileLines = Get-Content $PROFILE
$newFunction = Get-Content "C:\Users\gpoli\GIT\AI_agents\BISTART_NEW_VERSION.txt"

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
    
    $newContent = @()
    if ($startIdx -gt 0) {
        $newContent += $profileLines[0..($startIdx-1)]
    }
    $newContent += $newFunction
    if ($endIdx -lt $profileLines.Count-1) {
        $newContent += $profileLines[($endIdx+1)..($profileLines.Count-1)]
    }
    
    $newContent | Out-File $PROFILE -Encoding UTF8 -Force
    
    Write-Host "Updated successfully!" -ForegroundColor Green
    . $PROFILE
    Write-Host "Done!" -ForegroundColor Green
} else {
    Write-Host "Could not find BISTART function" -ForegroundColor Red
}
