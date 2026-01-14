# Simple V10 Deployment Trigger
# Triggers GitHub Actions build for v10 branch

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== V10 Deployment Trigger ===" -ForegroundColor Cyan
Write-Host ""

# Navigate to project
Set-Location "c:\Users\gpoli\GIT\AI_agents"

# Get current branch
$CurrentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Current branch: $CurrentBranch" -ForegroundColor Yellow

if ($CurrentBranch -ne "v10") {
    Write-Host "ERROR: Not on v10 branch!" -ForegroundColor Red
    Write-Host "Current branch: $CurrentBranch" -ForegroundColor Red
    exit 1
}

# Check for uncommitted changes
$Status = git status --porcelain
if ($Status) {
    Write-Host "ERROR: You have uncommitted changes" -ForegroundColor Red
    git status --short
    Write-Host ""
    Write-Host "Commit or stash changes before deploying" -ForegroundColor Yellow
    exit 1
}

# Create empty commit to trigger build
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$CommitMessage = "deploy: Trigger v10 rebuild - $Timestamp"

Write-Host ""
Write-Host "Creating deployment commit..." -ForegroundColor Cyan
git commit --allow-empty -m $CommitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create commit" -ForegroundColor Red
    exit 1
}

Write-Host "SUCCESS: Commit created" -ForegroundColor Green

# Push to remote
Write-Host ""
Write-Host "Pushing to remote (this triggers GitHub Actions)..." -ForegroundColor Cyan
git push origin v10

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push to remote" -ForegroundColor Red
    exit 1
}

Write-Host "SUCCESS: Pushed to origin/v10" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Deployment triggered for v10!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host ""
Write-Host "What's Happening:" -ForegroundColor Cyan
Write-Host "1. GitHub Actions building Docker image..."
Write-Host "2. Image will be tagged as: ghcr.io/gerardovsa/ai-agents-backend:v10"
Write-Host "3. Render will auto-deploy when build completes"
Write-Host "4. Monitor progress:"
Write-Host "   - GitHub: https://github.com/gerardovsa/AI_agents/actions"
Write-Host "   - Render: https://dashboard.render.com"

Write-Host ""
Write-Host "Estimated Time:" -ForegroundColor Cyan
Write-Host "   - Docker build: 5-8 minutes"
Write-Host "   - Render deploy: 2-3 minutes"
Write-Host "   - Total: approximately 10 minutes"

Write-Host ""
Write-Host "Test URLs (after deployment):" -ForegroundColor Cyan
Write-Host "   Health: https://ai-agents-v10.onrender.com/api/v1/system/check"
Write-Host "   Login: https://ai-agents-v10.onrender.com"

Write-Host ""
