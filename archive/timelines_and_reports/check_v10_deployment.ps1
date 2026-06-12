# Check v10 Deployment Status
# Run this to see if the Docker image was built and Render deployed it

Write-Host "`n=== V10 Deployment Status Check ===" -ForegroundColor Cyan

# 1. Check local v10 branch commit
Write-Host "`n1. Local v10 branch commit:" -ForegroundColor Yellow
git log -1 --oneline

# 2. Check remote v10 branch commit
Write-Host "`n2. Remote v10 branch commit:" -ForegroundColor Yellow
git ls-remote origin v10 | ForEach-Object { $_.Split()[0].Substring(0, 7) }

# 3. Check if FORCE_V10 is true in local code
Write-Host "`n3. Local code FORCE_V10 value:" -ForegroundColor Yellow
Select-String -Path "UI/business-ai-platform-v2.html" -Pattern "const FORCE_V10 = " | ForEach-Object { $_.Line.Trim() }

# 4. Check service worker cache version
Write-Host "`n4. Service Worker cache version:" -ForegroundColor Yellow
Select-String -Path "UI/service-worker.js" -Pattern "const CACHE_VERSION = " | ForEach-Object { $_.Line.Trim() }

# 5. Check GitHub Actions status
Write-Host "`n5. GitHub Actions status (check manually):" -ForegroundColor Yellow
Write-Host "   https://github.com/gerardovsa/AI_agents/actions" -ForegroundColor White
Write-Host "   Look for: 'Build and Push Docker Image' workflow" -ForegroundColor Gray
Write-Host "   Should show: Running or Completed (green check)" -ForegroundColor Gray

# 6. Check if Docker image exists
Write-Host "`n6. Docker image status (manual check):" -ForegroundColor Yellow
Write-Host "   https://github.com/gerardovsa/AI_agents/pkgs/container/ai_agents" -ForegroundColor White
Write-Host "   Look for: v10 tag in the list" -ForegroundColor Gray

# 7. Check Render deployment
Write-Host "`n7. Render v10 service status:" -ForegroundColor Yellow
Write-Host "   https://dashboard.render.com/web/srv-d4f7coe8fa8c73af4f0" -ForegroundColor White
Write-Host "   Check: Latest Deploy tab for recent activity" -ForegroundColor Gray

Write-Host "`n=== What to do next ===" -ForegroundColor Green
Write-Host "1. Check GitHub Actions (link above) - wait for build to complete (~3-5 min)" -ForegroundColor White
Write-Host "2. Once green check appears, wait 2-3 more minutes for Render to deploy" -ForegroundColor White
Write-Host "3. Visit: https://ai-agents-v10.onrender.com" -ForegroundColor White
Write-Host "4. Open console (F12) and look for:" -ForegroundColor White
Write-Host "   'API Base URL: https://ai-agents-v10.onrender.com' (should be v10, not v9)" -ForegroundColor Cyan
Write-Host ""
