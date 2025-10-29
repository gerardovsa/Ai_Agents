# Quick Start Guide - UI Connection Test

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🚀 QUICK START - NEW Flask UI Connection" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n📋 Steps to test UI connection:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Start NEW Flask app:" -ForegroundColor Cyan
Write-Host "    Type: RESTARTNEW" -ForegroundColor White
Write-Host "    (This command works from any directory)" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣  Wait for Flask to start (~10 seconds)" -ForegroundColor Cyan
Write-Host "    Look for: '🌐 Access at: http://localhost:5001'" -ForegroundColor White
Write-Host ""

Write-Host "3️⃣  Run test script (in a NEW terminal):" -ForegroundColor Cyan
Write-Host "    cd c:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure" -ForegroundColor White
Write-Host "    .\test_ui_connection.ps1" -ForegroundColor White
Write-Host ""

Write-Host "4️⃣  Open UIs in browser:" -ForegroundColor Cyan
Write-Host "    Stock Management: http://localhost:5001/stock-management" -ForegroundColor White
Write-Host "    Single Agent:     http://localhost:5001/single-agent-viewer" -ForegroundColor White
Write-Host "    Triple Agent:     http://localhost:5001/triple-agent" -ForegroundColor White
Write-Host "    Home (default):   http://localhost:5001/" -ForegroundColor White
Write-Host ""

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✨ What to expect:" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ HTML UIs load successfully" -ForegroundColor Green
Write-Host "✅ Stock AI Chat interface visible" -ForegroundColor Green
Write-Host "✅ File upload buttons work" -ForegroundColor Green
Write-Host "⚠️  Some features may not work yet (missing API endpoints)" -ForegroundColor Yellow
Write-Host "   - Stock inventory tabs" -ForegroundColor Gray
Write-Host "   - Invoice processing" -ForegroundColor Gray
Write-Host "   - Thread management" -ForegroundColor Gray
Write-Host ""

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Complete summary:      UI_CONNECTION_COMPLETE_SUMMARY.md" -ForegroundColor White
Write-Host "Implementation plan:   UI_CONNECTION_PLAN.md" -ForegroundColor White
Write-Host "Test script:           test_ui_connection.ps1" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Next steps after testing:" -ForegroundColor Yellow
Write-Host "- Add missing API endpoints (see UI_CONNECTION_PLAN.md)" -ForegroundColor White
Write-Host "- Test full Stock Management features" -ForegroundColor White
Write-Host "- Compare OLD Flask (port 5000) vs NEW Flask (port 5001)" -ForegroundColor White
Write-Host ""
