$lines = Get-Content "UI\business-ai-platform-v2.html"
$lineNum = 0
$opens = 0
$closes = 0
$results = @()

foreach ($line in $lines) {
    $lineNum++
    $lineOpens = ([regex]::Matches($line, '<script(?:\s|>)')).Count
    $lineCloses = ([regex]::Matches($line, '</script>')).Count
    
    $opens += $lineOpens
    $closes += $lineCloses
    $balance = $opens - $closes
    
    if ($lineOpens -gt 0) {
        $color = if ($balance -eq 0) { 'Green' } elseif ($balance -gt 0) { 'Cyan' } else { 'Red' }
        $results += [PSCustomObject]@{
            Line    = $lineNum
            Type    = "+$lineOpens open"
            Balance = $balance
            Color   = $color
        }
    }
    
    if ($lineCloses -gt 0) {
        $color = if ($balance -eq 0) { 'Green' } elseif ($balance -gt 0) { 'Cyan' } else { 'Red' }
        $results += [PSCustomObject]@{
            Line    = $lineNum
            Type    = "-$lineCloses close"
            Balance = $balance
            Color   = $color
        }
    }
}

# Show last 40 entries
$results | Select-Object -Last 40 | ForEach-Object {
    Write-Host "Line $($_.Line): $($_.Type) (balance: $($_.Balance))" -ForegroundColor $_.Color
}

Write-Host "`nFinal balance: $($opens - $closes)" -ForegroundColor $(if ($opens -eq $closes) { 'Green' } else { 'Red' })
