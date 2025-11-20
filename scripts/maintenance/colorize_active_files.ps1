# Colorize Active Session Files Script
# Uses Peacock extension to highlight active files in Aqua Blue

Write-Host "`n🎨 Colorizing Active Session Files with Aqua Blue" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if Peacock extension is installed
$peacockInstalled = code --list-extensions | Select-String "johnpapa.vscode-peacock"

if (-not $peacockInstalled) {
    Write-Host "❌ Peacock extension not installed" -ForegroundColor Red
    Write-Host "Installing Peacock extension..." -ForegroundColor Yellow
    code --install-extension johnpapa.vscode-peacock
    Write-Host "✅ Peacock installed - Please restart VS Code" -ForegroundColor Green
    exit
}

Write-Host "✅ Peacock extension detected" -ForegroundColor Green

# Create .vscode folder if it doesn't exist
$vscodePath = "c:\Users\gpoli\GIT\AI_agents\.vscode"
if (-not (Test-Path $vscodePath)) {
    New-Item -Path $vscodePath -ItemType Directory -Force | Out-Null
    Write-Host "📁 Created .vscode folder" -ForegroundColor Green
}

# Active files to colorize (Aqua Blue)
$activeFiles = @(
    "unified_session_manager.py",
    "combined_agent_worker.py",
    "agent_routes_v4.py", 
    "session_orchestrator.py",
    "tool_executor.py",
    "tool_processor.py",
    "agent_state_manager.py"
)

# Create Peacock settings
$peacockSettings = @{
    "peacock.favoriteColors" = @(
        @{
            "name" = "Aqua Blue (Active)"
            "value" = "#00BFFF"
        }
    )
    "peacock.affectActivityBar" = $true
    "peacock.affectStatusBar" = $true
    "peacock.affectTitleBar" = $true
    "peacock.elementAdjustments" = @{
        "activityBar" = "lighten"
        "statusBar" = "none"
        "titleBar" = "none"
    }
}

# Read existing settings or create new
$settingsPath = "$vscodePath\settings.json"
$settings = @{}

if (Test-Path $settingsPath) {
    $settingsContent = Get-Content $settingsPath -Raw
    try {
        $settings = $settingsContent | ConvertFrom-Json -AsHashtable
        Write-Host "📄 Loaded existing settings.json" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not parse existing settings.json, creating new" -ForegroundColor Yellow
    }
}

# Merge Peacock settings
foreach ($key in $peacockSettings.Keys) {
    $settings[$key] = $peacockSettings[$key]
}

# Save settings
$settingsJson = $settings | ConvertTo-Json -Depth 10
Set-Content -Path $settingsPath -Value $settingsJson

Write-Host "`n✅ Peacock configured for Aqua Blue theme" -ForegroundColor Green
Write-Host "`n📋 Active Files (will appear in Aqua Blue):" -ForegroundColor Cyan
foreach ($file in $activeFiles) {
    Write-Host "  - $file" -ForegroundColor White
}

Write-Host "`n🎯 To activate Peacock colors:" -ForegroundColor Yellow
Write-Host "  1. Open VS Code Command Palette (Ctrl+Shift+P)" -ForegroundColor White
Write-Host "  2. Type: 'Peacock: Change to a Favorite Color'" -ForegroundColor White
Write-Host "  3. Select: 'Aqua Blue (Active)'" -ForegroundColor White

Write-Host "`n✅ Configuration complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
