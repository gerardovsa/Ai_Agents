# Message Count Fix - Validation Script
# Date: November 19, 2025

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  MESSAGE COUNT FIX - VALIDATION REPORT  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if file exists
$filePath = "c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
if (Test-Path $filePath) {
    Write-Host "[OK] File exists: business-ai-platform-v2.html" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] File not found!" -ForegroundColor Red
    exit 1
}

# Get file info
$fileInfo = Get-Item $filePath
Write-Host "[INFO] File size: $($fileInfo.Length) bytes" -ForegroundColor Yellow
Write-Host "[INFO] Last modified: $($fileInfo.LastWriteTime)" -ForegroundColor Yellow
Write-Host ""

# Check for the fixed updateMessageCount function
Write-Host "Checking for updateMessageCount function..." -ForegroundColor Cyan
$content = Get-Content $filePath -Raw

if ($content -match "updateMessageCount\(threadId\)") {
    Write-Host "[OK] updateMessageCount function found" -ForegroundColor Green
    
    # Check for querySelectorAll usage
    if ($content -match "querySelectorAll.*thread-meta-item.*Message count") {
        Write-Host "[OK] querySelectorAll usage confirmed" -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] querySelectorAll not found - fix may not be applied" -ForegroundColor Yellow
    }
    
    # Check for forEach usage
    if ($content -match "forEach\(item => \{") {
        Write-Host "[OK] forEach loop found (updating all elements)" -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] forEach not found" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[ERROR] updateMessageCount function not found!" -ForegroundColor Red
}

Write-Host ""

# Check for duplicate functions
Write-Host "Checking for duplicate functions..." -ForegroundColor Cyan
$duplicateCount = ([regex]::Matches($content, "updateMessageCount\(threadId\)")).Count

if ($duplicateCount -eq 1) {
    Write-Host "[OK] No duplicate updateMessageCount functions (found 1)" -ForegroundColor Green
}
elseif ($duplicateCount -gt 1) {
    Write-Host "[WARNING] Found $duplicateCount copies of updateMessageCount" -ForegroundColor Yellow
}
else {
    Write-Host "[ERROR] updateMessageCount function not found!" -ForegroundColor Red
}

Write-Host ""

# Check for broken HTML code
Write-Host "Checking for code quality..." -ForegroundColor Cyan
$brokenPatterns = @(
    @{ Pattern = "<button class=`"thread-action-btn"; Name = "Broken button HTML in JS" },
    @{ Pattern = "<!-- ROW \d+:"; Name = "HTML comments in JS" },
    @{ Pattern = "<div class=`"thread-item-"; Name = "Broken div HTML in JS" }
)

$issuesFound = 0
foreach ($check in $brokenPatterns) {
    $matches = ([regex]::Matches($content, $check.Pattern)).Count
    if ($matches -gt 0) {
        Write-Host "[WARNING] Found $matches instances of: $($check.Name)" -ForegroundColor Yellow
        $issuesFound++
    }
}

if ($issuesFound -eq 0) {
    Write-Host "[OK] No broken HTML patterns detected" -ForegroundColor Green
}

Write-Host ""

# Run automated tests
Write-Host "Running automated tests..." -ForegroundColor Cyan
$testScript = "c:\Users\gpoli\GIT\AI_agents\UI\test_message_count.js"
if (Test-Path $testScript) {
    Write-Host "[INFO] Executing: node test_message_count.js" -ForegroundColor Yellow
    $testResult = & node $testScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] All automated tests passed!" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Some tests failed!" -ForegroundColor Red
    }
}
else {
    Write-Host "[WARNING] Test script not found: $testScript" -ForegroundColor Yellow
}

Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check line count at line 29021
Write-Host "Checking specific line numbers..." -ForegroundColor Cyan
$lines = Get-Content $filePath
$line29021 = $lines[29020] # 0-indexed

if ($line29021 -match "updateMessageCount\(threadId\)") {
    Write-Host "[OK] updateMessageCount at expected line 29021" -ForegroundColor Green
}
else {
    Write-Host "[INFO] Line 29021: $($line29021.Substring(0, [Math]::Min(60, $line29021.Length)))" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[STATUS] Message count fix validation complete!" -ForegroundColor Cyan
Write-Host ""

# Open test report
Write-Host "Test files created:" -ForegroundColor Cyan
Write-Host "  1. test_message_count.js (automated tests)" -ForegroundColor White
Write-Host "  2. test_message_count_fix.html (interactive tests)" -ForegroundColor White
Write-Host "  3. MESSAGE_COUNT_FIX_TEST_REPORT.md (full report)" -ForegroundColor White
Write-Host ""
Write-Host "To view interactive test, run:" -ForegroundColor Yellow
Write-Host "  Start-Process 'c:\Users\gpoli\GIT\AI_agents\UI\test_message_count_fix.html'" -ForegroundColor White
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
