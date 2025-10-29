# Quick Deploy to Render.com
# Run this after creating GitHub repository

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "🚀 AI AGENTS RENDER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Step 1: Check current status
Write-Host "📋 Step 1: Checking current status..." -ForegroundColor Yellow
git status --short
$branch = git branch --show-current
Write-Host "   Current branch: $branch" -ForegroundColor Green

# Step 2: Create GitHub repository prompt
Write-Host "`n📋 Step 2: Create GitHub Repository" -ForegroundColor Yellow
Write-Host "   1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "   2. Repository name: AI_agents" -ForegroundColor White
Write-Host "   3. Visibility: Private" -ForegroundColor White
Write-Host "   4. DON'T initialize with README" -ForegroundColor Red
Write-Host "   5. Click 'Create repository'" -ForegroundColor White
Write-Host "`nPress Enter when done..." -ForegroundColor Cyan
Read-Host

# Step 3: Push to GitHub
Write-Host "`n📋 Step 3: Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "   Pushing V2 branch..." -ForegroundColor White
git push -u origin V2

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ V2 branch pushed successfully!" -ForegroundColor Green
    
    Write-Host "`n   Pushing main branch..." -ForegroundColor White
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Main branch pushed successfully!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Main branch push failed (may not exist yet)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Push failed!" -ForegroundColor Red
    Write-Host "   Common fixes:" -ForegroundColor Yellow
    Write-Host "   - Generate Personal Access Token at: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "   - Use token as password when prompted" -ForegroundColor White
    Write-Host "   - Ensure repository name is exactly: gerardovsa/AI_agents" -ForegroundColor White
    exit 1
}

# Step 4: Configure Render
Write-Host "`n📋 Step 4: Configure Render Service" -ForegroundColor Yellow
Write-Host "   Opening Render dashboard..." -ForegroundColor White
Start-Process "https://dashboard.render.com/select-repo?type=web"

Write-Host "`n   Use these settings:" -ForegroundColor Cyan
Write-Host "   ✅ Name: ai-agents-v2" -ForegroundColor White
Write-Host "   ✅ Region: Oregon (US West)" -ForegroundColor White
Write-Host "   ✅ Branch: V2" -ForegroundColor White
Write-Host "   ✅ Root Directory: AI_infrastructure" -ForegroundColor White
Write-Host "   ✅ Build Command: pip install -r requirements.txt" -ForegroundColor White
Write-Host "   ✅ Start Command: python flask_app.py" -ForegroundColor White
Write-Host "   ✅ Plan: Free" -ForegroundColor White

Write-Host "`n   REQUIRED Environment Variables:" -ForegroundColor Red
Write-Host "   FLASK_ENV=production" -ForegroundColor White
Write-Host "   PORT=10000" -ForegroundColor White
Write-Host "   SECRET_KEY=<generate with command below>" -ForegroundColor White
Write-Host "   ANTHROPIC_API_KEY=<from .env.master>" -ForegroundColor White
Write-Host "   OPENAI_API_KEY=<from .env.master>" -ForegroundColor White
Write-Host "   DEEPSEEK_API_KEY=<from .env.master>" -ForegroundColor White
Write-Host "   MICROSOFT_CLIENT_ID=<from .env.master>" -ForegroundColor White
Write-Host "   MICROSOFT_CLIENT_SECRET=<from .env.master>" -ForegroundColor White
Write-Host "   MICROSOFT_TENANT_ID=common" -ForegroundColor White
Write-Host "   GOOGLE_CLIENT_ID=<from .env.master>" -ForegroundColor White
Write-Host "   GOOGLE_CLIENT_SECRET=<from .env.master>" -ForegroundColor White

# Generate SECRET_KEY
Write-Host "`n📋 Generating SECRET_KEY..." -ForegroundColor Yellow
$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "   SECRET_KEY=$secretKey" -ForegroundColor Green
Write-Host "   (Copy this to Render environment variables)" -ForegroundColor Cyan

# Step 5: Show .env.master values
Write-Host "`n📋 Step 5: Your API Keys (.env.master)" -ForegroundColor Yellow
if (Test-Path ".env.master") {
    Write-Host "   Reading from .env.master..." -ForegroundColor White
    $envContent = Get-Content ".env.master"
    $envContent | Select-String -Pattern "ANTHROPIC_API_KEY|OPENAI_API_KEY|DEEPSEEK_API_KEY|MICROSOFT_CLIENT_ID|MICROSOFT_CLIENT_SECRET|GOOGLE_CLIENT_ID|GOOGLE_CLIENT_SECRET" | ForEach-Object {
        $line = $_.Line
        if ($line -notmatch "^#") {
            Write-Host "   $line" -ForegroundColor White
        }
    }
} else {
    Write-Host "   ⚠️  .env.master not found!" -ForegroundColor Red
}

# Step 6: Next steps
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "📋 NEXT STEPS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "1. ✅ Complete Render service creation" -ForegroundColor White
Write-Host "2. ✅ Add all environment variables" -ForegroundColor White
Write-Host "3. ✅ Click 'Create Web Service'" -ForegroundColor White
Write-Host "4. ⏳ Wait for build (5-10 minutes)" -ForegroundColor White
Write-Host "5. ✅ Update OAuth redirect URLs:" -ForegroundColor White
Write-Host "   - Microsoft: https://portal.azure.com" -ForegroundColor Gray
Write-Host "   - Google: https://console.cloud.google.com" -ForegroundColor Gray
Write-Host "6. ✅ Test at: https://ai-agents-v2.onrender.com" -ForegroundColor White

Write-Host "`n📖 Full guide: RENDER_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan
