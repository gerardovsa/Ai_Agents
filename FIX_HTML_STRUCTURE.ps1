# Force-fix the HTML structure
$filePath = "UI\business-ai-platform-v2.html"

Write-Host "Reading file..." -ForegroundColor Yellow
$content = Get-Content $filePath -Raw -Encoding UTF8

Write-Host "Finding problem lines..." -ForegroundColor Yellow

# Find and replace - line 19737 needs 12 spaces instead of 8
$content = $content -replace '(?m)^        </div>\s*\n        <!-- End of \.main-content -->', '            </div>`n            <!-- End of .main-content -->'

# Find and replace - line 19741 needs 12 spaces instead of 8  
$content = $content -replace '(?m)^        <!-- ={20} AI CHAT PANEL ={20} -->\s*\n        <div class="ai-chat-panel"', '            <!-- ==================== AI CHAT PANEL ==================== -->`n            <div class="ai-chat-panel"'

Write-Host "Writing fixed content..." -ForegroundColor Yellow
$content | Out-File $filePath -Encoding UTF8 -NoNewline

Write-Host "DONE! HTML structure fixed." -ForegroundColor Green
Write-Host "Now restart Flask and hard refresh browser!" -ForegroundColor Cyan
