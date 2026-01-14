# Add Email Thread Badge Script Tag to HTML
# This script adds the email-thread-integration.js script tag to business-ai-platform-v2.html

$htmlFile = "UI\business-ai-platform-v2.html"
$scriptTag = '    <script src="UI/modules_internal/thread-cards/email-thread-integration.js"></script>'

Write-Host "`n🔧 Adding Email Thread Badge Script Tag..." -ForegroundColor Cyan

# Check if file exists
if (-not (Test-Path $htmlFile)) {
    Write-Host "❌ File not found: $htmlFile" -ForegroundColor Red
    exit 1
}

# Read file content
$content = Get-Content $htmlFile -Raw

# Check if script tag already exists
if ($content -match "email-thread-integration\.js") {
    Write-Host "✅ Script tag already exists in $htmlFile" -ForegroundColor Green
    Write-Host "   No changes needed." -ForegroundColor White
    exit 0
}

# Find the closing </body> tag
if ($content -match "</body>") {
    # Add script tag before </body>
    $content = $content -replace "</body>", "$scriptTag`n</body>"
    
    # Write back to file
    $content | Set-Content $htmlFile -NoNewline
    
    Write-Host "✅ Script tag added successfully!" -ForegroundColor Green
    Write-Host "   File: $htmlFile" -ForegroundColor White
    Write-Host "   Added: email-thread-integration.js" -ForegroundColor Cyan
    Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Restart Flask server (BISTART)" -ForegroundColor White
    Write-Host "   2. Run SQL migration on Supabase" -ForegroundColor White
    Write-Host "   3. Test email-to-thread assignment" -ForegroundColor White
}
else {
    Write-Host "❌ Could not find </body> tag in $htmlFile" -ForegroundColor Red
    exit 1
}
