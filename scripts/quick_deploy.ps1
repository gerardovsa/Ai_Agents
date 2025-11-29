#Requires -Version 5.1
<#
.SYNOPSIS
    Quick deploy current version branch
    
.DESCRIPTION
    One-command deployment for current version branch
    - Auto-detects version from branch name
    - Creates empty commit to trigger GitHub Actions
    - Pushes to remote to start build
    
.PARAMETER Message
    Custom commit message (optional)
    
.EXAMPLE
    .\quick_deploy.ps1
    
.EXAMPLE
    .\quick_deploy.ps1 -Message "feat: Update authentication flow"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Message = ""
)

$ErrorActionPreference = "Stop"

# Colors
$SuccessColor = "Green"
$InfoColor = "Cyan"
$ErrorColor = "Red"

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $SuccessColor
}

function Write-Fail {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ErrorColor
}

$ProjectRoot = "c:\Users\gpoli\GIT\AI_agents"

Write-Host "`n🚀 Quick Deploy" -ForegroundColor $InfoColor
Write-Host "=" * 60 -ForegroundColor $InfoColor

# Navigate to project
Set-Location $ProjectRoot

# Get current branch
$CurrentBranch = git rev-parse --abbrev-ref HEAD
Write-Step "Current branch: $CurrentBranch"

# Extract version
$Version = "unknown"
if ($CurrentBranch -match '^v(\d+)$') {
    $Version = $Matches[1]
    Write-Step "Detected version: v$Version"
} else {
    Write-Fail "Not on a version branch (v10, v11, etc.)"
    Write-Host "Current branch: $CurrentBranch"
    exit 1
}

# Check for uncommitted changes
$Status = git status --porcelain
if ($Status) {
    Write-Fail "You have uncommitted changes:"
    git status --short
    Write-Host "`nCommit or stash changes before deploying"
    exit 1
}

# Default commit message
if ([string]::IsNullOrEmpty($Message)) {
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Message = "deploy: Trigger v$Version build - $Timestamp"
}

# Create empty commit to trigger build
Write-Step "Creating deployment commit..."
git commit --allow-empty -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Failed to create commit"
    exit 1
}
Write-Success "Commit created"

# Push to remote
Write-Step "Pushing to remote (this triggers GitHub Actions)..."
git push origin $CurrentBranch
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Failed to push to remote"
    exit 1
}
Write-Success "Pushed to origin/$CurrentBranch"

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor $SuccessColor
Write-Host "🎉 Deployment triggered for v$Version!" -ForegroundColor $SuccessColor
Write-Host ("=" * 60) -ForegroundColor $SuccessColor

Write-Host "`n📋 What's Happening:" -ForegroundColor $InfoColor
Write-Host "1. GitHub Actions building Docker image..."
Write-Host "2. Image tagged as: ghcr.io/gerardovsa/ai-agents-backend:v$Version"
Write-Host "3. Render will auto-deploy when build completes"
Write-Host "4. Monitor progress:"
Write-Host "   - GitHub: https://github.com/gerardovsa/AI_agents/actions"
Write-Host "   - Render: https://dashboard.render.com"

Write-Host "`n⏱️  Estimated Time:" -ForegroundColor $InfoColor
Write-Host "   - Docker build: 5-8 minutes"
Write-Host "   - Render deploy: 2-3 minutes"
Write-Host "   - Total: ~10 minutes"

Write-Host "`n🔗 Test URLs (after deployment):" -ForegroundColor $InfoColor
Write-Host "   Health: https://ai-agents-v$Version.onrender.com/api/v1/system/check"
Write-Host "   Login: https://ai-agents-v$Version.onrender.com"

Write-Host ""
