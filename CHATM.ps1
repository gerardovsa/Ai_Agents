param(
    [Parameter(ValueFromRemainingArguments=$true, Position=0)]
    [string[]]$MessageParts
)

$Message = if ($MessageParts) { $MessageParts -join ' ' } else { $null }

if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Host ""
    Write-Host "Usage: CHATM <your message>" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  CHATM List my Excel workbooks" -ForegroundColor White
    Write-Host "  CHATM Show my OneNote notebooks" -ForegroundColor White
    Write-Host "  CHATM List my Outlook emails" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: CHATM automatically uses your Microsoft 365 account" -ForegroundColor Gray
    Write-Host "      (Gerardo@minivetguide.onmicrosoft.com)" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

$separator = "=" * 60

Write-Host ""
Write-Host "Microsoft 365 Account: " -ForegroundColor Cyan -NoNewline
Write-Host "Gerardo@minivetguide.onmicrosoft.com" -ForegroundColor White
Write-Host $separator -ForegroundColor DarkGray
Write-Host "You: " -ForegroundColor Cyan -NoNewline
Write-Host $Message -ForegroundColor White
Write-Host $separator -ForegroundColor DarkGray
Write-Host ""

try {
    $microsoftUser = "Gerardo@minivetguide.onmicrosoft.com"
    $tokenOutput = python "$PSScriptRoot\get_auth_token.py" "$microsoftUser" 2>&1
    
    $token = ($tokenOutput | Where-Object { $_ -match '^eyJ' } | Select-Object -Last 1)
    
    if ([string]::IsNullOrWhiteSpace($token)) {
        Write-Host "Warning: Authentication token generation failed, continuing without auth..." -ForegroundColor Yellow
        $headers = @{ "Content-Type" = "application/json" }
    } else {
        $token = $token.Trim()
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        }
    }
    
    $body = @{
        message = $Message
        source = "cli"
        context = @{ tools_enabled = $true }
    } | ConvertTo-Json -Depth 10

    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/agent/chat" -Method POST -Headers $headers -Body $body -TimeoutSec 120

    Write-Host "AI Agent: " -ForegroundColor Cyan -NoNewline
    Write-Host $response.response -ForegroundColor White

    if ($response.tool_calls -and $response.tool_calls.Count -gt 0) {
        Write-Host ""
        Write-Host "Tools Used:" -ForegroundColor Yellow
        foreach ($tool in $response.tool_calls) {
            if ($tool.success) {
                Write-Host "  [OK] " -ForegroundColor Green -NoNewline
            } else {
                Write-Host "  [FAIL] " -ForegroundColor Red -NoNewline
            }
            Write-Host $tool.name -ForegroundColor White
            if (-not $tool.success -and $tool.error) {
                Write-Host "     Error: $($tool.error)" -ForegroundColor Red
            }
        }
    }
    Write-Host ""
    Write-Host $separator -ForegroundColor DarkGray
    Write-Host ""
} catch {
    Write-Host "Error: " -ForegroundColor Red -NoNewline
    if ($_.Exception.Message -match "Unable to connect|connection") {
        Write-Host "Cannot connect to server on localhost:5001" -ForegroundColor Red
        Write-Host "Start server with: BISTART" -ForegroundColor Yellow
    } else {
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}
