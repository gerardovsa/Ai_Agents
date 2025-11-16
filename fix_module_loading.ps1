# ==============================================================================
# MODULE LOADING FIX SCRIPT
# ==============================================================================
# Purpose: Diagnose and fix module loading issues for:
# - shopify
# - stock-management
# - inhouse-kanban
# - communication-hub
# - database-visualizer
#
# Issues Found:
# 1. Shopify uses old init_shopify_routes() pattern (not Blueprint)
# 2. Stock Management has Blueprint routes (GOOD)
# 3. InHouse Kanban - NO routes folder
# 4. Communication Hub - NO routes folder
# 5. Database Visualizer - NO routes folder
# ==============================================================================

Write-Host "=================================================================================================" -ForegroundColor Cyan
Write-Host "MODULE LOADING DIAGNOSTIC & FIX SCRIPT" -ForegroundColor Cyan
Write-Host "=================================================================================================" -ForegroundColor Cyan

$modulesDir = "C:\Users\gpoli\GIT\AI_agents\UI\external\modules"
$targetModules = @('shopify', 'stock-management', 'inhouse-kanban', 'communication-hub', 'database-visualizer')

Write-Host "`n[STEP 1] Checking Module Structure..." -ForegroundColor Yellow
Write-Host "=================================================================================================" -ForegroundColor Gray

$results = @()

foreach ($module in $targetModules) {
    $modulePath = Join-Path $modulesDir $module
    $routesPath = Join-Path $modulePath "routes"
    $jsFile = Join-Path $modulePath "$module.js"
    $manifestFile = Join-Path $modulePath "manifest.json"
    
    $hasRoutes = Test-Path $routesPath
    $hasJS = Test-Path $jsFile
    $hasManifest = Test-Path $manifestFile
    
    $status = @{
        'Module' = $module
        'JS File' = $hasJS
        'Manifest' = $hasManifest
        'Routes Folder' = $hasRoutes
        'Status' = 'Unknown'
    }
    
    # Determine status
    if ($hasJS -and $hasManifest -and $hasRoutes) {
        $status.Status = 'OK'
        Write-Host "  $module" -ForegroundColor Green -NoNewline
        Write-Host " - COMPLETE (has routes/)" -ForegroundColor Green
    } elseif ($hasJS -and $hasManifest) {
        $status.Status = 'MISSING_ROUTES'
        Write-Host "  $module" -ForegroundColor Yellow -NoNewline
        Write-Host " - MISSING routes/ folder" -ForegroundColor Red
    } else {
        $status.Status = 'BROKEN'
        Write-Host "  $module" -ForegroundColor Red -NoNewline
        Write-Host " - BROKEN (missing core files)" -ForegroundColor Red
    }
    
    $results += $status
}

Write-Host "`n[STEP 2] Checking Module Blueprint Loader..." -ForegroundColor Yellow
Write-Host "=================================================================================================" -ForegroundColor Gray

$blueprintLoaderPath = "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\module_blueprint_loader.py"
if (Test-Path $blueprintLoaderPath) {
    Write-Host "  module_blueprint_loader.py EXISTS" -ForegroundColor Green
    
    # Test it
    Write-Host "  Testing blueprint loader..." -ForegroundColor Cyan
    $testResult = python -c @"
import sys
sys.path.insert(0, 'AI_infrastructure')
try:
    from core.module_blueprint_loader import ModuleBlueprintLoader
    from flask import Flask
    app = Flask(__name__)
    loader = ModuleBlueprintLoader(app)
    modules = loader.discover_modules_with_routes()
    print(f'DISCOVERED:{len(modules)}')
    for m in modules:
        print(f'  - {m}')
except Exception as e:
    print(f'ERROR:{e}')
"@
    
    if ($testResult -match "DISCOVERED:(\d+)") {
        $count = $Matches[1]
        Write-Host "  Blueprint loader discovered $count modules with routes" -ForegroundColor Green
        $testResult | ForEach-Object { 
            if ($_ -match "^\s+-\s+(.+)") {
                Write-Host "    $($Matches[1])" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "  ERROR testing blueprint loader:" -ForegroundColor Red
        Write-Host $testResult -ForegroundColor Red
    }
} else {
    Write-Host "  module_blueprint_loader.py MISSING" -ForegroundColor Red
}

Write-Host "`n[STEP 3] Checking Flask App Integration..." -ForegroundColor Yellow
Write-Host "=================================================================================================" -ForegroundColor Gray

$flaskAppPath = "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py"
if (Test-Path $flaskAppPath) {
    Write-Host "  flask_app.py EXISTS" -ForegroundColor Green
    
    # Check for module_blueprint_loader import
    $hasImport = Select-String -Path $flaskAppPath -Pattern "from core.module_blueprint_loader import" -Quiet
    if ($hasImport) {
        Write-Host "  Imports module_blueprint_loader" -ForegroundColor Green
    } else {
        Write-Host "  MISSING import for module_blueprint_loader" -ForegroundColor Red
    }
    
    # Check for load_module_blueprints call
    $hasCall = Select-String -Path $flaskAppPath -Pattern "load_module_blueprints\(app\)" -Quiet
    if ($hasCall) {
        Write-Host "  Calls load_module_blueprints(app)" -ForegroundColor Green
    } else {
        Write-Host "  MISSING call to load_module_blueprints()" -ForegroundColor Red
    }
}

Write-Host "`n[STEP 4] Checking Database Configuration..." -ForegroundColor Yellow
Write-Host "=================================================================================================" -ForegroundColor Gray

# Check Supabase config
$supabaseFile = "C:\Users\gpoli\GIT\AI_agents\data\SUPABASE_DATABASE.txt"
if (Test-Path $supabaseFile) {
    Write-Host "  SUPABASE_DATABASE.txt found" -ForegroundColor Green
    Write-Host "  This is a REPORT file, not config (NORMAL)" -ForegroundColor Gray
}

# Check .env file
$envFile = "C:\Users\gpoli\GIT\AI_agents\.env.master"
if (Test-Path $envFile) {
    Write-Host "  .env.master EXISTS" -ForegroundColor Green
    
    $hasSupabaseUrl = Select-String -Path $envFile -Pattern "SUPABASE_URL" -Quiet
    $hasUseSupabase = Select-String -Path $envFile -Pattern "USE_SUPABASE" -Quiet
    
    if ($hasSupabaseUrl) {
        Write-Host "  SUPABASE_URL configured" -ForegroundColor Green
    } else {
        Write-Host "  SUPABASE_URL NOT configured" -ForegroundColor Yellow
    }
    
    if ($hasUseSupabase) {
        Write-Host "  USE_SUPABASE configured" -ForegroundColor Green
    } else {
        Write-Host "  USE_SUPABASE NOT configured" -ForegroundColor Yellow
    }
}

# Check stock database
$stockDbPath = "C:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\stocks\stock_data.db"
if (Test-Path $stockDbPath) {
    Write-Host "  stock_data.db EXISTS at In_House_SQL project" -ForegroundColor Green
    $stockDbSize = (Get-Item $stockDbPath).Length / 1MB
    Write-Host "  Size: $([math]::Round($stockDbSize, 2)) MB" -ForegroundColor Gray
} else {
    Write-Host "  stock_data.db NOT FOUND" -ForegroundColor Red
}

Write-Host "`n[STEP 5] Module-Specific Issues..." -ForegroundColor Yellow
Write-Host "=================================================================================================" -ForegroundColor Gray

# Shopify - Check if using old init pattern
Write-Host "`nSHOPIFY:" -ForegroundColor Cyan
$shopifyRoutesFile = Join-Path $modulesDir "shopify\shopify_routes.py"
if (Test-Path $shopifyRoutesFile) {
    $hasInitPattern = Select-String -Path $shopifyRoutesFile -Pattern "def init_shopify_routes" -Quiet
    $hasBlueprintPattern = Select-String -Path $shopifyRoutesFile -Pattern "Blueprint\(" -Quiet
    
    if ($hasInitPattern -and -not $hasBlueprintPattern) {
        Write-Host "  ISSUE: Using OLD init_shopify_routes() pattern" -ForegroundColor Red
        Write-Host "  FIX: Convert to Flask Blueprint pattern" -ForegroundColor Yellow
    } elseif ($hasBlueprintPattern) {
        Write-Host "  Using Blueprint pattern" -ForegroundColor Green
    }
}

# InHouse Kanban - Check if needs routes
Write-Host "`nINHOUSE-KANBAN:" -ForegroundColor Cyan
$kanbanRoutesPath = Join-Path $modulesDir "inhouse-kanban\routes"
if (-not (Test-Path $kanbanRoutesPath)) {
    Write-Host "  ISSUE: NO routes/ folder" -ForegroundColor Red
    Write-Host "  FIX: Create routes/kanban_routes.py with Blueprint" -ForegroundColor Yellow
} else {
    Write-Host "  Has routes/ folder" -ForegroundColor Green
}

# Communication Hub
Write-Host "`nCOMMUNICATION-HUB:" -ForegroundColor Cyan
$commHubRoutesPath = Join-Path $modulesDir "communication-hub\routes"
if (-not (Test-Path $commHubRoutesPath)) {
    Write-Host "  ISSUE: NO routes/ folder" -ForegroundColor Red
    Write-Host "  FIX: Create routes/communication_routes.py with Blueprint" -ForegroundColor Yellow
} else {
    Write-Host "  Has routes/ folder" -ForegroundColor Green
}

# Database Visualizer
Write-Host "`nDATABASE-VISUALIZER:" -ForegroundColor Cyan
$dbVizRoutesPath = Join-Path $modulesDir "database-visualizer\routes"
if (-not (Test-Path $dbVizRoutesPath)) {
    Write-Host "  ISSUE: NO routes/ folder" -ForegroundColor Red
    Write-Host "  FIX: Create routes/database_routes.py with Blueprint" -ForegroundColor Yellow
} else {
    Write-Host "  Has routes/ folder" -ForegroundColor Green
}

Write-Host "`n=================================================================================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=================================================================================================" -ForegroundColor Cyan

$okCount = ($results | Where-Object { $_.Status -eq 'OK' }).Count
$missingRoutesCount = ($results | Where-Object { $_.Status -eq 'MISSING_ROUTES' }).Count
$brokenCount = ($results | Where-Object { $_.Status -eq 'BROKEN' }).Count

Write-Host "`nModules Status:" -ForegroundColor White
Write-Host "  OK (has routes/): $okCount" -ForegroundColor Green
Write-Host "  Missing routes/: $missingRoutesCount" -ForegroundColor Yellow
Write-Host "  Broken: $brokenCount" -ForegroundColor Red

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Review the issues above" -ForegroundColor White
Write-Host "  2. For modules missing routes/, decide:" -ForegroundColor White
Write-Host "     a) If module needs backend API, create routes/ folder with Blueprint" -ForegroundColor White
Write-Host "     b) If module is frontend-only, it's OK (no backend needed)" -ForegroundColor White
Write-Host "  3. For Shopify, convert init_shopify_routes() to Blueprint pattern" -ForegroundColor White
Write-Host "  4. Test with: BISTART" -ForegroundColor White
Write-Host "  5. Check browser console at: http://localhost:5001/business-ai-platform-v2.html" -ForegroundColor White

Write-Host "`n=================================================================================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC COMPLETE" -ForegroundColor Green
Write-Host "=================================================================================================" -ForegroundColor Cyan
