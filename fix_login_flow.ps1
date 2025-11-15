# Fix login flow - suppress logs until after auth, add smooth transitions

$file = 'C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html'

Write-Host "`nReading file..." -ForegroundColor Cyan
$content = Get-Content $file -Raw -Encoding UTF8

Write-Host "Applying fixes..." -ForegroundColor Yellow

# 1. Add defer to visualization scripts
$content = $content -replace '(<script src="visualisation_engine/streamingTwoRule\.js">)', '$1 defer data-post-auth>'
$content = $content -replace '(<script src="visualisation_engine/visualisation_copy\.js">)', '$1 defer data-post-auth>'

# 2. Fix login overlay transition (remove display:none, use opacity)
$content = $content -replace '\.login-overlay\.hidden \{[\s\S]*?display: none;[\s\S]*?\}', @'
.login-overlay.hidden {
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s ease-out;
        }
        
        .login-overlay {
            transition: opacity 0.4s ease-in;
        }
'@

# 3. Wrap DOMContentLoaded in auth check
$content = $content -replace "document\.addEventListener\('DOMContentLoaded', async \(\) => \{[\s\S]*?console\.log\('🚀 Business AI Platform initializing\.\.\.'\);", @'
// ==================== MAIN APP INITIALIZATION (Post-Auth) ====================
        window.initializeMainApp = async function() {
            console.log('[MAIN APP] Initializing Business AI Platform...');
'@

# 4. Close the initializeMainApp function and add new DOMContentLoaded
$content = $content -replace "console\.log\('🎨 ====================================================================\\n'\);[\s\S]*?\}\);[\s\S]*?// ==================== DRAG AND DROP SETUP", @'
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

        // ==================== DRAG AND DROP SETUP
'@

# 5. Update showMainApp to call initializeMainApp
$content = $content -replace "async showMainApp\(\) \{[\s\S]*?document\.getElementById\('loginOverlay'\)\.classList\.add\('hidden'\);[\s\S]*?document\.querySelector\('\.platform-container'\)\.style\.display = 'grid';", @'
async showMainApp() {
                console.log('[AUTH] Login successful - Initializing main application...');
                
                // Smooth transition: fade out login, fade in main app
                const loginOverlay = document.getElementById('loginOverlay');
                const platformContainer = document.querySelector('.platform-container');
                
                // Start fade out login
                loginOverlay.classList.add('hidden');
                
                // Wait for fade animation, then initialize main app
                setTimeout(async () => {
                    loginOverlay.style.display = 'none';
                    platformContainer.style.display = 'grid';
                    platformContainer.style.opacity = '0';
                    
                    // Trigger main app initialization
                    await window.initializeMainApp();
                    
                    // Fade in main app
                    requestAnimationFrame(() => {
                        platformContainer.style.transition = 'opacity 0.4s ease-in';
                        platformContainer.style.opacity = '1';
                    });
                }, 400); // Match transition duration
'@

Write-Host "Saving changes..." -ForegroundColor Green
$content | Set-Content $file -Encoding UTF8 -NoNewline

Write-Host "`n[SUCCESS] Login flow optimized!" -ForegroundColor Green
Write-Host "Changes applied:" -ForegroundColor Cyan
Write-Host "  1. Deferred visualization scripts" -ForegroundColor White
Write-Host "  2. Smooth fade transitions (no white bar)" -ForegroundColor White
Write-Host "  3. Main app only loads AFTER login" -ForegroundColor White
Write-Host "  4. No duplicate loading" -ForegroundColor White
Write-Host "`nRefresh your browser to see changes!`n" -ForegroundColor Yellow
