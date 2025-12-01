# Analyze All Modules for ES6/V4 Compliance
# Usage: .\scripts\analyze_all_modules_es6.ps1
# Output: CSV file with compliance report for all modules

$modulesPath = "UI\modules_external"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputCsv = "module_es6_compliance_report_$timestamp.csv"

Write-Host "🔍 ES6/V4 Compliance Analyzer - Batch Mode" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Get all module folders
$modules = Get-ChildItem -Path $modulesPath -Directory | Sort-Object Name

Write-Host "📊 Found $($modules.Count) modules to analyze" -ForegroundColor Green
Write-Host ""

$results = @()
$moduleCount = 0

foreach ($module in $modules) {
    $moduleCount++
    $moduleName = $module.Name
    
    Write-Host "[$moduleCount/$($modules.Count)] Analyzing $moduleName..." -ForegroundColor Yellow
    
    # Run analyzer
    $analysisOutput = python scripts\testing\module_analyzer.py $module.FullName 2>&1
    
    # Find the JSON output file
    $jsonFile = Get-ChildItem -Path $module.FullName -Filter "*_analysis_*.json" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1
    
    if ($jsonFile) {
        $json = Get-Content $jsonFile.FullName | ConvertFrom-Json
        $es6 = $json.checks.es6_v4_compliance
        
        $results += [PSCustomObject]@{
            Module             = $moduleName
            ES6_Status         = $es6.status
            Pattern            = $es6.pattern
            ES6_Compliant      = $es6.es6_compliant
            V4_Ready           = $es6.v4_ready
            Export_Default     = $es6.has_export_default
            Composition        = $es6.has_composition
            Lifecycle_Hooks    = ($es6.has_lifecycle_hooks -join ', ')
            Extends_BaseModule = $es6.extends_base_module
            Is_Class_Based     = $es6.is_class_based
            Manifest_Framework = $es6.manifest_framework
            Migration_Items    = $es6.migration_needed.Count
            Compliance_Score   = $json.compliance_score
            Architecture       = $json.checks.architecture_pattern.architecture
        }
        
        # Show quick status
        $statusColor = switch ($es6.status) {
            "READY" { "Green" }
            "PARTIAL" { "Yellow" }
            "NEEDS_MIGRATION" { "Red" }
            "NEEDS_REFACTOR" { "Yellow" }
            default { "Gray" }
        }
        
        Write-Host "   Status: $($es6.status)" -ForegroundColor $statusColor
        if ($es6.v4_ready) {
            Write-Host "   ✅ V4 Ready! ($($es6.has_lifecycle_hooks.Count) lifecycle hooks)" -ForegroundColor Green
        }
        else {
            Write-Host "   ⏳ Migration needed: $($es6.migration_needed.Count) items" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "   ❌ Analysis failed - no JSON output" -ForegroundColor Red
        
        $results += [PSCustomObject]@{
            Module             = $moduleName
            ES6_Status         = "ERROR"
            Pattern            = "Unknown"
            ES6_Compliant      = $false
            V4_Ready           = $false
            Export_Default     = $false
            Composition        = $false
            Lifecycle_Hooks    = ""
            Extends_BaseModule = $false
            Is_Class_Based     = $false
            Manifest_Framework = ""
            Migration_Items    = 0
            Compliance_Score   = 0
            Architecture       = "Unknown"
        }
    }
    
    Write-Host ""
}

# Export to CSV
$results | Export-Csv -Path $outputCsv -NoTypeInformation
Write-Host "📄 Report saved to: $outputCsv" -ForegroundColor Cyan
Write-Host ""

# Summary Statistics
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 SUMMARY STATISTICS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$readyCount = ($results | Where-Object { $_.ES6_Status -eq "READY" }).Count
$partialCount = ($results | Where-Object { $_.ES6_Status -eq "PARTIAL" }).Count
$migrationCount = ($results | Where-Object { $_.ES6_Status -eq "NEEDS_MIGRATION" }).Count
$refactorCount = ($results | Where-Object { $_.ES6_Status -eq "NEEDS_REFACTOR" }).Count
$unknownCount = ($results | Where-Object { $_.ES6_Status -eq "UNKNOWN" }).Count
$errorCount = ($results | Where-Object { $_.ES6_Status -eq "ERROR" }).Count

$totalModules = $results.Count
$v4ReadyPercent = [math]::Round(($readyCount / $totalModules) * 100, 1)

Write-Host "Total Modules: $totalModules" -ForegroundColor White
Write-Host ""
Write-Host "✅ READY:           $readyCount modules ($v4ReadyPercent%)" -ForegroundColor Green
Write-Host "⚠️  PARTIAL:         $partialCount modules" -ForegroundColor Yellow
Write-Host "🔄 NEEDS_MIGRATION: $migrationCount modules" -ForegroundColor Red
Write-Host "🛠️  NEEDS_REFACTOR:  $refactorCount modules" -ForegroundColor Yellow
Write-Host "❓ UNKNOWN:         $unknownCount modules" -ForegroundColor Gray
Write-Host "❌ ERROR:           $errorCount modules" -ForegroundColor Red
Write-Host ""

if ($v4ReadyPercent -eq 100) {
    Write-Host "🎉 ALL MODULES V4 READY! 🎉" -ForegroundColor Green
    Write-Host "You can now swap to the V4 module loader!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Update business-ai-platform-v2.html to use shared/js/module-loader-v4.js" -ForegroundColor White
    Write-Host "2. Test all modules load correctly" -ForegroundColor White
    Write-Host "3. Measure performance improvement (expect 50% faster load)" -ForegroundColor White
    Write-Host "4. Delete legacy loaders (modules/module_loader.js, modules_internal/module_loader.js)" -ForegroundColor White
}
else {
    $remainingModules = $totalModules - $readyCount
    Write-Host "📋 Migration Progress: $readyCount/$totalModules ready ($v4ReadyPercent%)" -ForegroundColor Yellow
    Write-Host "🎯 Remaining work: $remainingModules modules" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Priority Order:" -ForegroundColor Cyan
    Write-Host "1. Fix PARTIAL modules (easiest - add missing patterns)" -ForegroundColor White
    Write-Host "2. Refactor NEEDS_REFACTOR modules (moderate - convert class to composition)" -ForegroundColor White
    Write-Host "3. Migrate NEEDS_MIGRATION modules (hardest - remove BaseModule)" -ForegroundColor White
    Write-Host "4. Investigate UNKNOWN/ERROR modules" -ForegroundColor White
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Show detailed breakdown by status
Write-Host "📋 DETAILED BREAKDOWN" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

if ($readyCount -gt 0) {
    Write-Host "✅ READY Modules ($readyCount):" -ForegroundColor Green
    $results | Where-Object { $_.ES6_Status -eq "READY" } | 
    ForEach-Object { Write-Host "   - $($_.Module) (Score: $($_.Compliance_Score)/100)" -ForegroundColor Green }
    Write-Host ""
}

if ($partialCount -gt 0) {
    Write-Host "⚠️  PARTIAL Modules ($partialCount):" -ForegroundColor Yellow
    $results | Where-Object { $_.ES6_Status -eq "PARTIAL" } | 
    ForEach-Object { Write-Host "   - $($_.Module) (Migration items: $($_.Migration_Items))" -ForegroundColor Yellow }
    Write-Host ""
}

if ($migrationCount -gt 0) {
    Write-Host "🔄 NEEDS_MIGRATION Modules ($migrationCount):" -ForegroundColor Red
    $results | Where-Object { $_.ES6_Status -eq "NEEDS_MIGRATION" } | 
    ForEach-Object { Write-Host "   - $($_.Module) (Uses BaseModule)" -ForegroundColor Red }
    Write-Host ""
}

if ($refactorCount -gt 0) {
    Write-Host "🛠️  NEEDS_REFACTOR Modules ($refactorCount):" -ForegroundColor Yellow
    $results | Where-Object { $_.ES6_Status -eq "NEEDS_REFACTOR" } | 
    ForEach-Object { Write-Host "   - $($_.Module) (Class-based)" -ForegroundColor Yellow }
    Write-Host ""
}

if ($unknownCount -gt 0) {
    Write-Host "❓ UNKNOWN Modules ($unknownCount):" -ForegroundColor Gray
    $results | Where-Object { $_.ES6_Status -eq "UNKNOWN" } | 
    ForEach-Object { Write-Host "   - $($_.Module)" -ForegroundColor Gray }
    Write-Host ""
}

if ($errorCount -gt 0) {
    Write-Host "❌ ERROR Modules ($errorCount):" -ForegroundColor Red
    $results | Where-Object { $_.ES6_Status -eq "ERROR" } | 
    ForEach-Object { Write-Host "   - $($_.Module)" -ForegroundColor Red }
    Write-Host ""
}

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ Analysis complete! Check '$outputCsv' for full details." -ForegroundColor Green
Write-Host ""
