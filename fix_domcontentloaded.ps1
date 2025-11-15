# Fix DOMContentLoaded to only check auth, not initialize everything

$file = 'C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html'

Write-Host "`nReading file..." -ForegroundColor Cyan
$content = Get-Content $file -Raw -Encoding UTF8

Write-Host "Finding and replacing DOMContentLoaded..." -ForegroundColor Yellow

# Find the closing of initializeMainApp and the old DOMContentLoaded
# Replace the "}); at the end of the old DOMContentLoaded with our new code
$oldPattern = "console\.log\('\s*====================================================================\\n'\);\s*\}\);"
$newCode = @'
console.log('[MAIN APP] Platform ready with full tool integration!\n');
        };
        
        // ==================== ON PAGE LOAD - AUTH CHECK ONLY ====================
        document.addEventListener('DOMContentLoaded', async () => {
            console.log('[AUTH] Checking authentication status...');
            
            // Check if user is already logged in
            const isAuthenticated = await UserAuth.checkExistingSession();
            
            if (isAuthenticated) {
                console.log('[AUTH] Session found - Loading main app...');
                await UserAuth.showMainApp();
            } else {
                console.log('[AUTH] No active session - Showing login screen');
                // Login screen is already visible by default
            }
        });
'@

if ($content -match $oldPattern) {
    $content = $content -replace $oldPattern, $newCode
    Write-Host "  [OK] Replaced DOMContentLoaded with auth check" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] Pattern not found - may already be fixed" -ForegroundColor Yellow
}

Write-Host "Saving changes..." -ForegroundColor Green
$content | Set-Content $file -Encoding UTF8 -NoNewline

Write-Host "`n[SUCCESS] DOMContentLoaded optimized!" -ForegroundColor Green
Write-Host "Now the app will:" -ForegroundColor Cyan
Write-Host "  1. Check authentication on page load" -ForegroundColor White
Write-Host "  2. Show login if not authenticated" -ForegroundColor White
Write-Host "  3. Only initialize main app AFTER successful login" -ForegroundColor White
Write-Host "`nRefresh your browser to test!`n" -ForegroundColor Yellow
