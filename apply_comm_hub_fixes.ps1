# Apply Communication Hub fixes
$ErrorActionPreference = "Stop"

$file = "c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\communication-hub\communication-hub-v4-modern.js"
Write-Host "Reading file..." -ForegroundColor Yellow
$content = Get-Content $file -Raw -Encoding UTF8

Write-Host "Applying FIX #2: Processing state..." -ForegroundColor Cyan

# Find the line with "this.state.emailThreads[emailId] = threadSlug;" at line ~2682
# Insert Processing indicator after console.logs

$processingFix = @'
            
            // FIX #2: Immediately update cell with "Processing" state
            if (cell && cell.getElement) {
                cell.getElement().innerHTML = '<div style="display: flex; align-items: center; justify-content: center; gap: 6px;"><i class="fas fa-spinner fa-spin" style="color: #3b82f6;"></i><span style="color: #3b82f6; font-size: 11px; font-weight: 600;">Processing...</span></div>';
            }
'@

# Pattern to match: after the 4th console.log, before the CRITICAL comment
$pattern1 = '(console\.log\(''   this\.state\.emailThreads:'', this\.state\.emailThreads\);\s*\r?\n)'
$replacement1 = '$1' + $processingFix + "`r`n"
$content = $content -replace $pattern1,$replacement1

Write-Host "Applying FIX #2 Part 2: Force cell update..." -ForegroundColor Cyan

$cellUpdateFix = @'

                
                // FIX #2: Force immediate cell update now that thread is loaded
                if (cell && cell.getElement) {
                    const emailRow = this.state.emails.find(e => e.id === emailId);
                    if (emailRow) {
                        emailRow.assigned_agent = agentName;
                        emailRow._threadSlug = threadSlug;
                    }
                    cell.getRow().update({ assigned_agent: agentName });
                }
'@

# Pattern: After this.log.success('... ThreadManager refreshed...')
$pattern2 = "(this\.log\.success\('.*?ThreadManager refreshed.*?'\);\s*\r?\n)"
$replacement2 = '$1' + $cellUpdateFix + "`r`n"
$content = $content -replace $pattern2,$replacement2

Write-Host "Applying FIX #3: Complete openAIThread navigation..." -ForegroundColor Cyan

# Replace the beginning of openAIThread function to add Command Center tab switch
$pattern3 = @'
(?s)(openAIThread\(threadSlug\) \{\s*this\.log\.debug.*?\r?\n\s*\r?\n\s*// .*? FIX.*?command center\s*\r?\n\s*if \(typeof ThreadManager.*?\r?\n.*?const thread = ThreadManager\.threads\.find.*?\r?\n\s*\r?\n\s*if \(thread\) \{\s*\r?\n\s*const location = thread\.location;\s*\r?\n\s*this\.log\.info\(.*?\r?\n\s*\r?\n\s*// Close panel)
'@

$replacement3 = @'
openAIThread(threadSlug) {
        this.log.info(`Opening AI thread: ${threadSlug}`);

        // FIX #3: Complete navigation to Command Center + agent column
        if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
            const thread = ThreadManager.threads.find(t => t.id === threadSlug || t.thread_slug === threadSlug);

            if (thread) {
                const location = thread.location;
                this.log.info(`Thread ${threadSlug} is in location: ${location}`);

                // Step 1: Switch to Command Center tab if not already there
                const commandCenterBtn = document.querySelector('[data-tab="multi-agent"]') || 
                                        document.querySelector('[onclick*="switchTab"][onclick*="multi-agent"]') ||
                                        document.getElementById('command-center-tab-btn');
                
                if (commandCenterBtn && !commandCenterBtn.classList.contains('active')) {
                    commandCenterBtn.click();
                    this.log.info('Switched to Command Center view');
                }

                // Close Communication Hub panel
'@

$content = $content -replace $pattern3,$replacement3

Write-Host "Saving file..." -ForegroundColor Yellow
[System.IO.File]::WriteAllText($file, $content, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Done! All fixes applied." -ForegroundColor Green
Write-Host ""
Write-Host "Summary of changes:" -ForegroundColor Cyan
Write-Host "  - FIX #1: Custom instructions textarea reading (already applied)" -ForegroundColor Green
Write-Host "  - FIX #2: Processing state + force cell update" -ForegroundColor Green
Write-Host "  - FIX #3: Complete Command Center navigation" -ForegroundColor Green
Write-Host "  - FIX #4: Open Agent button (already in formatter)" -ForegroundColor Green
