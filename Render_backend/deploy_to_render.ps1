# AI AGENTS - RENDER DEPLOYMENT SCRIPT
# Automated deployment to Render.com Singapore region

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AI AGENTS - RENDER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check repository status
Write-Host "STEP 1: Checking repository status..." -ForegroundColor Yellow
cd C:\Users\gpoli\GIT\AI_agents

$branch = git branch --show-current
Write-Host "  Current branch: $branch" -ForegroundColor Green

$status = git status --porcelain
if ($status) {
    Write-Host "`n  WARNING: You have uncommitted changes!" -ForegroundColor Red
    Write-Host "  Commit them before deploying.`n" -ForegroundColor Red
    git status
    exit
} else {
    Write-Host "  Repository is clean" -ForegroundColor Green
}

# Step 2: Validate render.yaml
Write-Host "`nSTEP 2: Validating render.yaml..." -ForegroundColor Yellow
python Render_backend\render_complete_cli.py blueprint validate render.yaml

# Step 3: Check current services
Write-Host "`nSTEP 3: Current Render services..." -ForegroundColor Yellow
python Render_backend\render_complete_cli.py status overview

# Step 4: Prepare environment variables
Write-Host "`nSTEP 4: Preparing environment variables..." -ForegroundColor Yellow

if (Test-Path ".env.master") {
    Write-Host "  Found .env.master" -ForegroundColor Green
    
    # Extract key variables
    $envContent = Get-Content .env.master | Where-Object { $_ -match "=" -and $_ -notmatch "^#" }
    
    Write-Host "`n  KEY VARIABLES TO ADD IN RENDER:" -ForegroundColor Cyan
    Write-Host "  ================================" -ForegroundColor Cyan
    
    # Show critical variables
    $criticalVars = @(
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_CLIENT_SECRET",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "MICROSOFT_CLIENT_ID",
        "MICROSOFT_CLIENT_SECRET",
        "WOOCOMMERCE_URL",
        "WOOCOMMERCE_CONSUMER_KEY",
        "WOOCOMMERCE_CONSUMER_SECRET"
    )
    
    foreach ($var in $criticalVars) {
        $line = $envContent | Where-Object { $_ -match "^$var=" } | Select-Object -First 1
        if ($line) {
            $value = $line -replace "^$var=", ""
            # Mask secrets
            if ($value.Length -gt 20) {
                $masked = $value.Substring(0, 8) + "..." + $value.Substring($value.Length - 8)
                Write-Host "  $var = $masked" -ForegroundColor White
            } else {
                Write-Host "  $var = $value" -ForegroundColor White
            }
        }
    }
} else {
    Write-Host "  WARNING: .env.master not found!" -ForegroundColor Red
}

# Step 5: Open Render dashboard
Write-Host "`nSTEP 5: Opening Render dashboard..." -ForegroundColor Yellow
Write-Host "  URL: https://dashboard.render.com/select-repo" -ForegroundColor Cyan

Start-Process "https://dashboard.render.com/select-repo"

# Step 6: Show deployment instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "IN THE RENDER DASHBOARD:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Click 'Connect a repository'" -ForegroundColor White
Write-Host "   - Select: gerardovsa/Ai_Agents" -ForegroundColor Gray
Write-Host "   - Branch: V2_clean" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Render will detect render.yaml" -ForegroundColor White
Write-Host "   - Service: ai-agents-backend" -ForegroundColor Gray
Write-Host "   - Region: Singapore ✓" -ForegroundColor Green
Write-Host "   - Environment: Docker ✓" -ForegroundColor Green
Write-Host "   - Plan: Starter" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Add Environment Variables (CRITICAL):" -ForegroundColor White
Write-Host "   Click 'Add Environment Variable' for each:" -ForegroundColor Gray
Write-Host ""
Write-Host "   PORT=10000" -ForegroundColor Cyan
Write-Host "   RENDER=true" -ForegroundColor Cyan
Write-Host "   DEBUG=False" -ForegroundColor Cyan
Write-Host "   PYTHONUNBUFFERED=1" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Then add ALL variables from .env.master above" -ForegroundColor Yellow
Write-Host ""

Write-Host "4. IMPORTANT: Update redirect URLs AFTER deploy:" -ForegroundColor Yellow
Write-Host "   After you get your Render URL (e.g., https://ai-agents-xyz.onrender.com)" -ForegroundColor Gray
Write-Host "   Update these variables:" -ForegroundColor Gray
Write-Host "   GOOGLE_REDIRECT_URI=https://your-service.onrender.com/api/auth/google/callback" -ForegroundColor Cyan
Write-Host "   GOOGLE_OAUTH_REDIRECT_URI=https://your-service.onrender.com/oauth2callback" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. Click 'Apply' to deploy!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AFTER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Monitor deployment:" -ForegroundColor Yellow
Write-Host "  python Render_backend\render_complete_cli.py services list" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check health:" -ForegroundColor Yellow
Write-Host "  python Render_backend\render_complete_cli.py health check srv-xxxxx" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  Go to Render dashboard > Your service > Logs tab" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================`n" -ForegroundColor Cyan

# Step 7: Wait for user to complete deployment
Write-Host "Press ENTER after you've clicked 'Apply' in Render dashboard..." -ForegroundColor Yellow
$null = Read-Host

# Step 8: Monitor deployment
Write-Host "`nMonitoring deployment..." -ForegroundColor Yellow
Write-Host "Refreshing service list every 10 seconds...`n" -ForegroundColor Gray

for ($i = 1; $i -le 30; $i++) {
    Write-Host "Check #$i - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
    python Render_backend\render_complete_cli.py services list | Select-String -Pattern "ai-agent"
    
    Start-Sleep -Seconds 10
    
    if ($i -eq 30) {
        Write-Host "`nDeployment monitoring complete." -ForegroundColor Green
        Write-Host "Check Render dashboard for final status." -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT SCRIPT COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
