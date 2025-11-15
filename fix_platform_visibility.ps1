# Fix platform-container visibility and Synergy button placement

$file = 'C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html'

Write-Host "`nReading file..." -ForegroundColor Cyan
$content = Get-Content $file -Raw -Encoding UTF8

Write-Host "Applying fixes..." -ForegroundColor Yellow

# 1. Make platform-container hidden by default
$content = $content -replace '(\.platform-container \{[\s\S]*?)(display: grid;)', '$1display: none; /* Hidden by default - shown after login */'

# 2. Add .active class styling for platform-container
$content = $content -replace '(\.platform-container \{[\s\S]*?height: 100vh;[\s\S]*?width: 100vw;[\s\S]*?\})', @'
$1
        
        .platform-container.active {
            display: grid; /* Show when authenticated */
        }
'@

# 3. Update showMainApp to use .active class
$content = $content -replace "platformContainer\.style\.display = 'grid';", "platformContainer.classList.add('active');"

# 4. Update showLogin to use .active class
$content = $content -replace "document\.querySelector\('\.platform-container'\)\.style\.display = 'none';", "document.querySelector('.platform-container').classList.remove('active');"

# 5. Move Synergy button inside platform-container (add it after opening div)
$content = $content -replace '(<div class="platform-container">[\s\S]*?)(<!-- ==================== SIDEBAR ==================== -->)', @'
$1<!-- ==================== SYNERGY TOGGLE BUTTON ==================== -->
        <button class="synergy-sidebar-toggle" id="synergy-sidebar-toggle" onclick="SynergySidebar.toggleSidebar()"
            title="Toggle Synergy Sessions">
            <i class="fa-solid fa-hexagon-nodes-bolt"></i>
        </button>

        $2
'@

# 6. Remove duplicate Synergy button from outside platform-container
$content = $content -replace '    <!-- ==================== SYNERGY SIDEBAR \(Right Side\) ==================== -->[\s\S]*?<button class="synergy-sidebar-toggle"[\s\S]*?</button>[\s\S]*?(<div class="synergy-sidebar)', '    <!-- ==================== SYNERGY SIDEBAR (Right Side) ==================== -->' + "`n    " + '$1'

Write-Host "Saving changes..." -ForegroundColor Green
$content | Set-Content $file -Encoding UTF8 -NoNewline

Write-Host "`n[SUCCESS] Platform styling fixed!" -ForegroundColor Green
Write-Host "Changes applied:" -ForegroundColor Cyan
Write-Host "  1. Platform-container hidden by default (display: none)" -ForegroundColor White
Write-Host "  2. Platform-container shows with .active class after login" -ForegroundColor White
Write-Host "  3. Synergy button moved inside platform-container" -ForegroundColor White
Write-Host "  4. Synergy button now hidden on login screen" -ForegroundColor White
Write-Host "`nRefresh your browser - login screen should look clean now!`n" -ForegroundColor Yellow
