param(
    [Parameter(ValueFromRemainingArguments=$true, Position=0)]
    [string[]]$MessageParts,
    
    [Parameter()]
    [string]$User = "gerardo@vetsuccessacademy.com"
)

$Message = if ($MessageParts) { $MessageParts -join ' ' } else { $null }

if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Host "`nUsage: CHAT <your message> [-User <email>]" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  CHAT Can you help me?" -ForegroundColor White
    Write-Host "  CHAT List my Cloud Run services" -ForegroundColor White
    Write-Host "  CHAT List my Outlook emails -User Gerardo@minivetguide.onmicrosoft.com" -ForegroundColor White
    Write-Host "`nAvailable Users:" -ForegroundColor Yellow
    Write-Host "  • gerardo@vetsuccessacademy.com (Google Workspace)" -ForegroundColor White
    Write-Host "  • Gerardo@minivetguide.onmicrosoft.com (Microsoft 365)`n" -ForegroundColor White
    exit 1
}

Write-Host "`n$('=' * 60)" -ForegroundColor DarkGray
Write-Host "You: " -ForegroundColor Cyan -NoNewline
Write-Host $Message -ForegroundColor White
Write-Host "$('=' * 60)`n" -ForegroundColor DarkGray

try {
    # Get authentication token for specified user
    $tokenOutput = python "$PSScriptRoot\get_auth_token.py" "$User" 2>&1
    
    # Extract only the JWT token (last line, starts with eyJ)
    $token = ($tokenOutput | Where-Object { $_ -match '^eyJ' } | Select-Object -Last 1)
    
    # Check if we got a valid token (ignore exit code due to Python warnings)
    if ([string]::IsNullOrWhiteSpace($token)) {
        Write-Host "⚠️ Authentication token generation failed, continuing without auth..." -ForegroundColor Yellow
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
