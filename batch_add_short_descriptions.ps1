# Batch Add Short Descriptions to Tool Schemas
# This script systematically adds short_description fields to all tools

param(
    [string]$SchemaPath = "c:\Users\gpoli\GIT\AI_agents\tools\schemas",
    [int]$BatchSize = 20
)

Write-Host "`n=== BATCH SHORT DESCRIPTION PROCESSOR ===" -ForegroundColor Cyan
Write-Host "Schema Path: $SchemaPath" -ForegroundColor White
Write-Host "Batch Size: $BatchSize tools at a time`n" -ForegroundColor White

# Get all incomplete files
$allFiles = Get-ChildItem "$SchemaPath\*.json" | Sort-Object Name
$incomplete = @()

foreach ($file in $allFiles) {
    $content = Get-Content $file.FullName -Raw
    $toolMatches = [regex]::Matches($content, '"name":\s+"([^"]+)"') | Where-Object { 
        $_.Groups[1].Value -notmatch '^(properties|type|description|required|items|default|enum)$' 
    }
    $toolCount = ($toolMatches | Select-Object -ExpandProperty Groups | Select-Object -Skip 1 | Select-Object -ExpandProperty Value | Select-Object -Unique).Count
    
    if ($toolCount -gt 0) {
        $descCount = ([regex]::Matches($content, '"name":\s+"[^"]+",\s*"short_description":')).Count
        if ($descCount -lt $toolCount) {
            $incomplete += [PSCustomObject]@{
                File      = $file.FullName
                FileName  = $file.Name
                Complete  = $descCount
                Total     = $toolCount
                Remaining = $toolCount - $descCount
            }
        }
    }
}

Write-Host "Found $($incomplete.Count) incomplete files" -ForegroundColor Yellow
Write-Host "Total tools to process: $(($incomplete | Measure-Object -Property Remaining -Sum).Sum)`n" -ForegroundColor White

# Sort by smallest remaining count first (quick wins)
$sorted = $incomplete | Sort-Object Remaining

Write-Host "Processing order:" -ForegroundColor Cyan
$sorted | ForEach-Object {
    Write-Host "  $($_.FileName): $($_.Remaining) tools" -ForegroundColor White
}

Write-Host "`nReady to process. Run with -Execute to start.`n" -ForegroundColor Yellow
