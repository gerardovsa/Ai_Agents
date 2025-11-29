#Requires -Version 5.1
<#
.SYNOPSIS
    List all deployed versions with health status
    
.DESCRIPTION
    Dashboard showing all version branches with:
    - Branch name and version number
    - Expected URL
    - Health check status
    - Last commit info
    
.PARAMETER CheckHealth
    Perform HTTP health checks (default: true)
    
.EXAMPLE
    .\list_versions.ps1
    
.EXAMPLE
    .\list_versions.ps1 -CheckHealth:$false
#>

param(
    [Parameter(Mandatory=$false)]
    [bool]$CheckHealth = $true
)

$ErrorActionPreference = "Stop"

# Colors
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"
$ErrorColor = "Red"

function Test-UrlHealth {
    param([string]$Url)
    
    try {
        $Response = Invoke-WebRequest -Uri "$Url/api/v1/system/check" -TimeoutSec 10 -UseBasicParsing
        if ($Response.StatusCode -eq 200) {
            return @{ Status = "✅ Online"; Color = $SuccessColor }
        } else {
            return @{ Status = "⚠️  HTTP $($Response.StatusCode)"; Color = $WarningColor }
        }
    } catch {
        return @{ Status = "❌ Offline"; Color = $ErrorColor }
    }
}

$ProjectRoot = "c:\Users\gpoli\GIT\AI_agents"
Set-Location $ProjectRoot

Write-Host "`n📊 Version Deployment Dashboard" -ForegroundColor $InfoColor
Write-Host "=" * 90 -ForegroundColor $InfoColor

# Get all version branches (local and remote)
$Branches = git branch -a | Where-Object { $_ -match 'v\d+$' } | ForEach-Object {
    $_.Trim() -replace '^\*\s+', '' -replace 'remotes/origin/', ''
} | Select-Object -Unique | Sort-Object

if ($Branches.Count -eq 0) {
    Write-Host "No version branches found (looking for v10, v11, etc.)" -ForegroundColor $WarningColor
    exit 0
}

Write-Host "Found $($Branches.Count) version branch(es)`n" -ForegroundColor $InfoColor

# Table header
Write-Host ("Branch".PadRight(12)) -NoNewline
Write-Host ("Version".PadRight(10)) -NoNewline
Write-Host ("Expected URL".PadRight(45)) -NoNewline
Write-Host ("Last Commit".PadRight(15)) -NoNewline
if ($CheckHealth) {
    Write-Host "Health"
} else {
    Write-Host ""
}
Write-Host ("-" * 90) -ForegroundColor $InfoColor

foreach ($Branch in $Branches) {
    # Extract version number
    $Version = "unknown"
    if ($Branch -match 'v(\d+)$') {
        $Version = $Matches[1]
    }
    
    # Get last commit info
    $CommitInfo = "N/A"
    try {
        $CommitInfo = git log -1 --format="%ar" $Branch 2>$null
        if ([string]::IsNullOrEmpty($CommitInfo)) {
            $CommitInfo = "N/A"
        }
    } catch {
        $CommitInfo = "N/A"
    }
    
    # Expected URL
    $ExpectedUrl = "https://ai-agents-v$Version.onrender.com"
    
    # Display row
    Write-Host ($Branch.PadRight(12)) -NoNewline -ForegroundColor $InfoColor
    Write-Host ($Version.PadRight(10)) -NoNewline
    Write-Host ($ExpectedUrl.PadRight(45)) -NoNewline
    Write-Host ($CommitInfo.PadRight(15)) -NoNewline
    
    if ($CheckHealth) {
        $HealthResult = Test-UrlHealth -Url $ExpectedUrl
        Write-Host $HealthResult.Status -ForegroundColor $HealthResult.Color
    } else {
        Write-Host ""
    }
}

Write-Host "`n" + ("=" * 90) -ForegroundColor $InfoColor

# Current branch
$CurrentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "📍 Current branch: " -NoNewline -ForegroundColor $InfoColor
Write-Host $CurrentBranch -ForegroundColor $SuccessColor

Write-Host "`n💡 Quick Commands:" -ForegroundColor $InfoColor
Write-Host "   Deploy current: .\scripts\quick_deploy.ps1"
Write-Host "   Create v11: .\scripts\create_new_version.ps1 -Version 11"
Write-Host "   Switch to v10: git checkout v10"

Write-Host ""
