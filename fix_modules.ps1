# Quick fix for module loading issues

Write-Host "Module Loading Diagnostic and Fix Script" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Gray

# Step 1: Check database config files
Write-Host "`n[1] Checking database config files..." -ForegroundColor Yellow

$supabaseTxt = "C:\Users\gpoli\GIT\AI_agents\data\SUPABASE_DATABASE.txt"
$superbaseTxt = "C:\Users\gpoli\GIT\AI_agents\data\SUPERBASE DATABASE.txt"

if (Test-Path $supabaseTxt) {
    Write-Host "   [OK] Found: SUPABASE_DATABASE.txt" -ForegroundColor Green
    Write-Host "   Contents:" -ForegroundColor Gray
    Get-Content $supabaseTxt | Select-Object -First 10 | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
}
else {
    Write-Host "   [ERROR] NOT FOUND: SUPABASE_DATABASE.txt" -ForegroundColor Red
}

if (Test-Path $superbaseTxt) {
    Write-Host "   [WARNING] Found: SUPERBASE DATABASE.txt (TYPO IN FILENAME)" -ForegroundColor Yellow
}

# Step 2: Check .env.master
Write-Host "`n[2] Checking .env.master configuration..." -ForegroundColor Yellow

$envMaster = "C:\Users\gpoli\GIT\AI_agents\.env.master"

if (Test-Path $envMaster) {
    Write-Host "   [OK] .env.master exists" -ForegroundColor Green
    
    $hasSupabaseUrl = Select-String -Path $envMaster -Pattern "SUPABASE_URL" -Quiet
    $hasUseSupabase = Select-String -Path $envMaster -Pattern "USE_SUPABASE" -Quiet
    
    if ($hasSupabaseUrl) {
        Write-Host "   [OK] SUPABASE_URL configured" -ForegroundColor Green
    }
    else {
        Write-Host "   [ERROR] SUPABASE_URL NOT SET (modules will not load)" -ForegroundColor Red
        Write-Host "      Add: SUPABASE_URL=postgresql://..." -ForegroundColor Yellow
    }
    
    if ($hasUseSupabase) {
        $value = Select-String -Path $envMaster -Pattern "USE_SUPABASE" | Select-Object -First 1
        Write-Host "   [OK] USE_SUPABASE configured: $($value.Line)" -ForegroundColor Green
    }
    else {
        Write-Host "   [ERROR] USE_SUPABASE NOT SET (modules will not load)" -ForegroundColor Red
        Write-Host "      Add: USE_SUPABASE=true" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   [ERROR] .env.master NOT FOUND" -ForegroundColor Red
}

# Step 3: Check module structure
Write-Host "`n[3] Checking module structure..." -ForegroundColor Yellow

$modulesDir = "C:\Users\gpoli\GIT\AI_agents\UI\external\modules"
$modules = @('shopify', 'stock-management', 'inhouse-kanban', 'communication-hub', 'database-visualizer')

foreach ($module in $modules) {
    $modulePath = Join-Path $modulesDir $module
    $routesPath = Join-Path $modulePath "routes"
    
    if (Test-Path $modulePath) {
        if (Test-Path $routesPath) {
            $routeFiles = Get-ChildItem -Path $routesPath -Filter "*.py" -File
            Write-Host "   [OK] $module - Has routes/ folder ($($routeFiles.Count) files)" -ForegroundColor Green
        }
        else {
            Write-Host "   [WARNING] $module - Missing routes/ folder (backend will not load)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "   [ERROR] $module - Module folder NOT FOUND" -ForegroundColor Red
    }
}

# Step 4: Test database connection
Write-Host "`n[4] Testing database detection..." -ForegroundColor Yellow

try {
    Push-Location C:\Users\gpoli\GIT\AI_agents
    $result = python -c "from AI_infrastructure.shared.database_utils import is_using_supabase; print(is_using_supabase())" 2>&1
    Pop-Location
    
    if ($result -match "True") {
        Write-Host "   [OK] Supabase connection detected" -ForegroundColor Green
    }
    else {
        Write-Host "   [ERROR] Supabase NOT detected (using SQLite fallback)" -ForegroundColor Red
        Write-Host "      Fix .env.master with SUPABASE_URL and USE_SUPABASE=true" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   [ERROR] Failed to test database: $_" -ForegroundColor Red
}

# Step 5: Check Flask process
Write-Host "`n[5] Checking Flask server status..." -ForegroundColor Yellow

$flaskProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*flask*" -or 
    (netstat -ano | Select-String "5001" | Select-String $_.Id)
}

if ($flaskProcess) {
    Write-Host "   [OK] Flask server is running (PID: $($flaskProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "   [WARNING] Flask server not detected" -ForegroundColor Yellow
    Write-Host "      Run: BISTART" -ForegroundColor Gray
}

# Step 6: Check module manifest
Write-Host "`n[6] Checking module manifest files..." -ForegroundColor Yellow

foreach ($module in $modules) {
    $manifestPath = Join-Path $modulesDir "$module\manifest.json"
    
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath | ConvertFrom-Json
        Write-Host "   [OK] $module - manifest.json (enabled: $($manifest.enabled))" -ForegroundColor Green
    }
    else {
        Write-Host "   [WARNING] $module - Missing manifest.json" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Gray
Write-Host "SUMMARY AND NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""

$issues = @()

if (-not (Test-Path $envMaster)) {
    $issues += "[ERROR] .env.master file missing"
}

if ($hasSupabaseUrl -eq $false) {
    $issues += "[ERROR] SUPABASE_URL not configured in .env.master"
}

if ($hasUseSupabase -eq $false) {
    $issues += "[ERROR] USE_SUPABASE not configured in .env.master"
}

if ($issues.Count -gt 0) {
    Write-Host "ISSUES FOUND:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "   $issue" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "TO FIX:" -ForegroundColor Cyan
    Write-Host "   1. Extract connection string from data/SUPABASE_DATABASE.txt" -ForegroundColor White
    Write-Host "   2. Edit .env.master and add:" -ForegroundColor White
    Write-Host "      USE_SUPABASE=true" -ForegroundColor Gray
    Write-Host "      SUPABASE_URL=postgresql://postgres.PROJECT:PASSWORD@HOST:PORT/postgres" -ForegroundColor Gray
    Write-Host "      SUPABASE_KEY=your-service-role-key" -ForegroundColor Gray
    Write-Host "   3. Restart Flask: BISTART" -ForegroundColor White
    Write-Host "   4. Refresh browser (Ctrl+Shift+R)" -ForegroundColor White
}
else {
    Write-Host "[OK] Configuration looks good!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If modules still not loading:" -ForegroundColor Yellow
    Write-Host "   1. Check browser console (F12) for errors" -ForegroundColor White
    Write-Host "   2. Check Flask logs for module loading messages" -ForegroundColor White
    Write-Host "   3. Restart Flask: BISTOP then BISTART" -ForegroundColor White
}

Write-Host ""
