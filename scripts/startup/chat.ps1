param(
    [Parameter(ValueFromRemainingArguments=$true, Position=0)]
    [string[]]$MessageParts
)

$Message = if ($MessageParts) { $MessageParts -join ' ' } else { $null }

if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Host "`nUsage: CHAT <your message>" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  CHAT Can you help me?" -ForegroundColor White
    Write-Host "  CHAT List my Cloud Run services`n" -ForegroundColor White
    exit 1
}

Write-Host "`n$('=' * 60)" -ForegroundColor DarkGray
Write-Host "You: " -ForegroundColor Cyan -NoNewline
Write-Host $Message -ForegroundColor White
Write-Host "$('=' * 60)`n" -ForegroundColor DarkGray

try {
    $body = @{
        message = $Message
        source = "cli"
        context = @{ tools_enabled = $true }
    } | ConvertTo-Json -Depth 10

    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/agent/chat" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 120

    Write-Host "AI Agent: " -ForegroundColor Cyan -NoNewline
    Write-Host $response.response -ForegroundColor White

    if ($response.tool_calls -and $response.tool_calls.Count -gt 0) {
        Write-Host "`nTools Used:" -ForegroundColor Yellow
        foreach ($tool in $response.tool_calls) {
            $icon = if ($tool.success) { "[OK]" } else { "[FAIL]" }
            $color = if ($tool.success) { "Green" } else { "Red" }
            Write-Host "  $icon " -ForegroundColor $color -NoNewline
            Write-Host $tool.name -ForegroundColor White
            if (-not $tool.success -and $tool.error) {
                Write-Host "     Error: $($tool.error)" -ForegroundColor Red
            }
        }
    }
    Write-Host "`n$('=' * 60)`n" -ForegroundColor DarkGray
} catch {
    Write-Host "Error: " -ForegroundColor Red -NoNewline
    if ($_.Exception.Message -match "Unable to connect|connection") {
        Write-Host "Cannot connect to server on localhost:5001" -ForegroundColor Red
        Write-Host "Start server with: " -ForegroundColor Yellow -NoNewline
        Write-Host "BISTART`n" -ForegroundColor Green
    } else {
        Write-Host "$($_.Exception.Message)`n" -ForegroundColor Red
    }
    exit 1
}
