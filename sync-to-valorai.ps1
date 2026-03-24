#!/usr/bin/env pwsh
# Sync visualization and UI changes from AI_Agents to ValorAI
# Usage: .\sync-to-valorai.ps1 "commit message"

param(
    [Parameter(Mandatory=$false)]
    [string]$CommitMessage = "feat(ui): sync visualization improvements from AI_Agents"
)

$src = "C:\Users\gpoli\GIT\AI_Agents_V11\AI_agents"
$dst = "C:\Users\gpoli\GIT\ValorAI"

Write-Host "`n🔄 Syncing AI_Agents → ValorAI..." -ForegroundColor Cyan

# Define file groups to sync
$vizEngine = @(
    "UI\visualisation_engine\visualisation_v3.js",
    "UI\visualisation_engine\visualisation_copy.js",
    "UI\visualisation_engine\html_renderer.js",
    "UI\visualisation_engine\react_renderer.js",
    "UI\visualisation_engine\viz_popup_manager.js",
    "UI\visualisation_engine\streamingTwoRule.js",
    "UI\visualisation_engine\lottie_renderer.js",
    "UI\visualisation_engine\schematic_renderer.js",
    "UI\visualisation_engine\cad_renderer.js",
    "UI\visualisation_engine\cad_renderer_engineering.js",
    "UI\visualisation_engine\svg_renderer.js",
    "UI\visualisation_engine\latex_renderer.js",
    "UI\visualisation_engine\threejs_renderer.js",
    "UI\visualisation_engine\gsap_renderer.js"
)

$uiModules = @(
    "UI\modules_internal\agents\agent-column.js",
    "UI\modules_internal\agents\agent-js.js",
    "UI\modules_internal\agents\prime_ai_chat.js",
    "UI\modules_internal\components\user_auth.js",
    "UI\modules_internal\thread-manager\thread-manager-assignment.js",
    "UI\modules_internal\thread-manager\thread-manager-core.js",
    "UI\modules_internal\thread-manager\thread-manager-interactions.js",
    "UI\shared\utilities\message_renderer.js",
    "UI\business-ai-platform-v2.html"
)

$backend = @(
    "AI_infrastructure\flask_app.py",
    "AI_infrastructure\shared\database_utils.py",
    "AI_infrastructure\tools\connection_monitor.py",
    "tools\implementations\visualization_guide.py"
)

# Copy files
$copied = 0
foreach ($group in @($vizEngine, $uiModules, $backend)) {
    foreach ($file in $group) {
        if (Test-Path "$src\$file") {
            Copy-Item "$src\$file" "$dst\$file" -Force -ErrorAction SilentlyContinue
            if ($?) {
                Write-Host "  ✓ $file" -ForegroundColor Green
                $copied++
            }
        }
    }
}

Write-Host "`n📊 Copied $copied files" -ForegroundColor Yellow

# Git operations in ValorAI
Push-Location $dst
try {
    Write-Host "`n📦 Committing in ValorAI..." -ForegroundColor Cyan
    git add -A
    
    $status = git status --short
    if ($status) {
        Write-Host "`nChanged files:"
        Write-Host $status
        
        git commit -m $CommitMessage
        Write-Host "`n✅ Committed: $CommitMessage" -ForegroundColor Green
        
        Write-Host "`n🚀 Pushing to GitHub..." -ForegroundColor Cyan
        git push origin main
        Write-Host "✅ Pushed to gerardovsa/valorai-platform" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  No changes detected" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}

Write-Host "`n✨ Sync complete!`n" -ForegroundColor Cyan
