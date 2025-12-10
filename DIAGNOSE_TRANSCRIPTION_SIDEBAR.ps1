#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Diagnostic script for transcription-sidebar positioning and rendering issues
    
.DESCRIPTION
    Analyzes the transcription-sidebar CSS, HTML, and JS to compare with the working
    synergy-sidebar implementation. Outputs detailed positioning, z-index, transform,
    and structure information to identify why the sidebar doesn't appear properly.
    
.NOTES
    Run from AI_agents directory:
    .\DIAGNOSE_TRANSCRIPTION_SIDEBAR.ps1
#>

param(
    [switch]$Verbose = $true
)

# Color output functions
function Write-Section {
    param([string]$Title)
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $($Title.PadRight(69))║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-SubSection {
    param([string]$Title)
    Write-Host "`n┌─── $Title $('─' * (70 - $Title.Length))" -ForegroundColor Yellow
}

function Write-Property {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Status = "INFO"
    )
    $color = switch ($Status) {
        "OK" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "  $($Name.PadRight(30)): " -NoNewline -ForegroundColor Gray
    Write-Host $Value -ForegroundColor $color
}

function Write-Comparison {
    param(
        [string]$Property,
        [string]$Synergy,
        [string]$Transcription,
        [bool]$Match
    )
    $statusColor = if ($Match) { "Green" } else { "Yellow" }
    $statusIcon = if ($Match) { "✓" } else { "⚠" }
    
    Write-Host "  $($Property.PadRight(25)): " -NoNewline -ForegroundColor Gray
    Write-Host "Synergy: $($Synergy.PadRight(20)) " -NoNewline -ForegroundColor Cyan
    Write-Host "| Transcription: $($Transcription.PadRight(20)) " -NoNewline -ForegroundColor Magenta
    Write-Host "[$statusIcon]" -ForegroundColor $statusColor
}

# File paths
$basePath = Get-Location
$transcriptionSidebarCSS = Join-Path $basePath "UI\modules_internal\transcription\transcription-sidebar.css"
$transcriptionSidebarHTML = Join-Path $basePath "UI\modules_internal\transcription\transcription-sidebar.html"
$transcriptionSidebarJS = Join-Path $basePath "UI\modules_internal\transcription\transcription-sidebar.js"
$businessPlatformHTML = Join-Path $basePath "UI\business-ai-platform-v2.html"

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TRANSCRIPTION SIDEBAR DIAGNOSTIC REPORT" -ForegroundColor White
Write-Host "  Comparing with working synergy-sidebar implementation" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "  Path: $basePath" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# ============================================================================
# SECTION 1: CSS POSITIONING ANALYSIS
# ============================================================================
Write-Section "1. CSS POSITIONING & LAYOUT"

if (Test-Path $transcriptionSidebarCSS) {
    $cssContent = Get-Content $transcriptionSidebarCSS -Raw
    
    Write-SubSection "Transcription Sidebar Container (.transcription-sidebar)"
    
    # Extract key CSS properties
    if ($cssContent -match '\.transcription-sidebar\s*\{([^}]+)\}') {
        $sidebarBlock = $matches[1]
        
        # Position
        if ($sidebarBlock -match 'position:\s*([^;]+)') {
            Write-Property "position" $matches[1].Trim() "OK"
        }
        
        # Top
        if ($sidebarBlock -match 'top:\s*([^;]+)') {
            Write-Property "top" $matches[1].Trim() "OK"
        }
        
        # Left/Right
        if ($sidebarBlock -match 'left:\s*([^;]+)') {
            Write-Property "left" $matches[1].Trim() "WARNING"
        }
        if ($sidebarBlock -match 'right:\s*([^;]+)') {
            Write-Property "right" $matches[1].Trim() "WARNING"
        }
        
        # Width
        if ($sidebarBlock -match 'width:\s*([^;]+)') {
            Write-Property "width" $matches[1].Trim() "OK"
        }
        
        # Height
        if ($sidebarBlock -match 'height:\s*([^;]+)') {
            Write-Property "height" $matches[1].Trim() "OK"
        }
        
        # Z-index
        if ($sidebarBlock -match 'z-index:\s*([^;]+)') {
            $zIndex = $matches[1].Trim()
            $status = if ([int]$zIndex -ge 1000) { "OK" } else { "WARNING" }
            Write-Property "z-index" $zIndex $status
        }
        
        # Transform
        if ($sidebarBlock -match 'transform:\s*([^;]+)') {
            Write-Property "transform" $matches[1].Trim() "OK"
        }
        
        # Transition
        if ($sidebarBlock -match 'transition:\s*([^;]+)') {
            Write-Property "transition" $matches[1].Trim() "OK"
        }
    }
    
    Write-SubSection "Collapsed State (.transcription-sidebar.collapsed)"
    
    if ($cssContent -match '\.transcription-sidebar\.collapsed\s*\{([^}]+)\}') {
        $collapsedBlock = $matches[1]
        
        if ($collapsedBlock -match 'transform:\s*([^;]+)') {
            Write-Property "transform" $matches[1].Trim() "OK"
        }
    }
    
}
else {
    Write-Host "  ❌ CSS file not found: $transcriptionSidebarCSS" -ForegroundColor Red
}

# ============================================================================
# SECTION 2: SYNERGY SIDEBAR COMPARISON
# ============================================================================
Write-Section "2. SYNERGY SIDEBAR COMPARISON"

if (Test-Path $businessPlatformHTML) {
    $platformContent = Get-Content $businessPlatformHTML -Raw
    
    Write-SubSection "Synergy Sidebar Properties (from business-ai-platform-v2.html)"
    
    if ($platformContent -match '\.synergy-sidebar\s*\{([^}]+)\}') {
        $synergySidebarBlock = $matches[1]
        
        # Extract synergy properties
        $synergyProps = @{}
        if ($synergySidebarBlock -match 'position:\s*([^;]+)') { $synergyProps['position'] = $matches[1].Trim() }
        if ($synergySidebarBlock -match 'top:\s*([^;]+)') { $synergyProps['top'] = $matches[1].Trim() }
        if ($synergySidebarBlock -match 'width:\s*([^;]+)') { $synergyProps['width'] = $matches[1].Trim() }
        if ($synergySidebarBlock -match 'height:\s*([^;]+)') { $synergyProps['height'] = $matches[1].Trim() }
        if ($synergySidebarBlock -match 'z-index:\s*([^;]+)') { $synergyProps['z-index'] = $matches[1].Trim() }
        if ($synergySidebarBlock -match 'transition:\s*([^;]+)') { $synergyProps['transition'] = $matches[1].Trim() }
        
        foreach ($key in $synergyProps.Keys) {
            Write-Property $key $synergyProps[$key] "OK"
        }
    }
    
    Write-SubSection "Synergy Left Side (.synergy-sidebar[data-side='left'])"
    
    if ($platformContent -match '\.synergy-sidebar\[data-side="left"\]\s*\{([^}]+)\}') {
        $synergyLeftBlock = $matches[1]
        
        if ($synergyLeftBlock -match 'left:\s*([^;]+)') {
            Write-Property "left" $matches[1].Trim() "OK"
        }
        if ($synergyLeftBlock -match 'border-right:\s*([^;]+)') {
            Write-Property "border-right" $matches[1].Trim() "OK"
        }
    }
    
    Write-SubSection "Synergy Collapsed State (.synergy-sidebar[data-side='left'].collapsed)"
    
    if ($platformContent -match '\.synergy-sidebar\[data-side="left"\]\.collapsed\s*\{([^}]+)\}') {
        $synergyCollapsedBlock = $matches[1]
        
        if ($synergyCollapsedBlock -match 'transform:\s*([^;]+)') {
            Write-Property "transform" $matches[1].Trim() "OK"
        }
        if ($synergyCollapsedBlock -match 'box-shadow:\s*([^;]+)') {
            Write-Property "box-shadow" $matches[1].Trim() "OK"
        }
    }
    
    Write-SubSection "Synergy Toggle Button (.synergy-sidebar-toggle)"
    
    if ($platformContent -match '\.synergy-sidebar-toggle\s*\{([^}]+)\}') {
        $synergyToggleBlock = $matches[1]
        
        Write-Host "  Toggle button properties:" -ForegroundColor Cyan
        if ($synergyToggleBlock -match 'position:\s*([^;]+)') {
            Write-Property "  position" $matches[1].Trim() "OK"
        }
        if ($synergyToggleBlock -match 'z-index:\s*([^;]+)') {
            Write-Property "  z-index" $matches[1].Trim() "OK"
        }
        if ($synergyToggleBlock -match 'width:\s*([^;]+)') {
            Write-Property "  width" $matches[1].Trim() "OK"
        }
        if ($synergyToggleBlock -match 'height:\s*([^;]+)') {
            Write-Property "  height" $matches[1].Trim() "OK"
        }
    }
}

# ============================================================================
# SECTION 3: SIDE-BY-SIDE COMPARISON
# ============================================================================
Write-Section "3. PROPERTY COMPARISON"

Write-SubSection "Core Layout Properties"

$cssContent = Get-Content $transcriptionSidebarCSS -Raw
$platformContent = Get-Content $businessPlatformHTML -Raw

# Helper to extract property
function Get-CSSProperty {
    param([string]$Content, [string]$Selector, [string]$Property)
    if ($Content -match "$Selector\s*\{([^}]+)\}" -and $matches[1] -match "$Property\s*:\s*([^;]+)") {
        return $matches[1].Trim()
    }
    return "NOT FOUND"
}

$synergyPos = Get-CSSProperty $platformContent '\.synergy-sidebar' 'position'
$transPos = Get-CSSProperty $cssContent '\.transcription-sidebar' 'position'
Write-Comparison "position" $synergyPos $transPos ($synergyPos -eq $transPos)

$synergyTop = Get-CSSProperty $platformContent '\.synergy-sidebar' 'top'
$transTop = Get-CSSProperty $cssContent '\.transcription-sidebar' 'top'
Write-Comparison "top" $synergyTop $transTop ($synergyTop -eq $transTop)

$synergyZ = Get-CSSProperty $platformContent '\.synergy-sidebar' 'z-index'
$transZ = Get-CSSProperty $cssContent '\.transcription-sidebar' 'z-index'
Write-Comparison "z-index" $synergyZ $transZ ($synergyZ -eq $transZ)

$synergyWidth = Get-CSSProperty $platformContent '\.synergy-sidebar' 'width'
$transWidth = Get-CSSProperty $cssContent '\.transcription-sidebar' 'width'
Write-Comparison "width" $synergyWidth $transWidth ($synergyWidth -eq $transWidth)

Write-SubSection "Left Side Positioning"

$synergyLeft = Get-CSSProperty $platformContent '\.synergy-sidebar\[data-side="left"\]' 'left'
$transLeft = Get-CSSProperty $cssContent '\.transcription-sidebar' 'left'
Write-Comparison "left" $synergyLeft $transLeft ($synergyLeft -eq $transLeft)

Write-SubSection "Collapsed Transform"

$synergyCollapsed = Get-CSSProperty $platformContent '\.synergy-sidebar\[data-side="left"\]\.collapsed' 'transform'
$transCollapsed = Get-CSSProperty $cssContent '\.transcription-sidebar\.collapsed' 'transform'
Write-Comparison "transform (collapsed)" $synergyCollapsed $transCollapsed ($synergyCollapsed -eq $transCollapsed)

# ============================================================================
# SECTION 4: HTML STRUCTURE ANALYSIS
# ============================================================================
Write-Section "4. HTML STRUCTURE"

if (Test-Path $transcriptionSidebarHTML) {
    $htmlContent = Get-Content $transcriptionSidebarHTML -Raw
    
    Write-SubSection "Transcription Sidebar Container"
    
    if ($htmlContent -match '<div[^>]*class="transcription-sidebar[^"]*"[^>]*>') {
        $containerTag = $matches[0]
        Write-Host "  $containerTag" -ForegroundColor Green
        
        # Check for data-side attribute
        if ($containerTag -match 'data-side="([^"]+)"') {
            Write-Property "data-side attribute" $matches[1] "OK"
        }
        else {
            Write-Property "data-side attribute" "MISSING" "WARNING"
        }
        
        # Check for ID
        if ($containerTag -match 'id="([^"]+)"') {
            Write-Property "id attribute" $matches[1] "OK"
        }
        else {
            Write-Property "id attribute" "MISSING" "ERROR"
        }
        
        # Check for collapsed class
        if ($containerTag -match 'collapsed') {
            Write-Property "Initial state" "collapsed" "OK"
        }
        else {
            Write-Property "Initial state" "expanded" "WARNING"
        }
    }
    
    Write-SubSection "Toggle Button Check"
    
    if ($htmlContent -match 'onclick="[^"]*toggleSidebar[^"]*"') {
        Write-Property "Toggle button" "FOUND in HTML" "OK"
    }
    else {
        Write-Property "Toggle button" "NOT FOUND in sidebar HTML" "WARNING"
        Write-Host "  Note: Toggle may be created dynamically by JS" -ForegroundColor Yellow
    }
}

# ============================================================================
# SECTION 5: JAVASCRIPT ANALYSIS
# ============================================================================
Write-Section "5. JAVASCRIPT FUNCTIONALITY"

if (Test-Path $transcriptionSidebarJS) {
    $jsContent = Get-Content $transcriptionSidebarJS -Raw
    
    Write-SubSection "Sidebar Controller"
    
    # Check for TranscriptionSidebar object
    if ($jsContent -match 'TranscriptionSidebar\s*=') {
        Write-Property "TranscriptionSidebar object" "DEFINED" "OK"
    }
    else {
        Write-Property "TranscriptionSidebar object" "NOT FOUND" "ERROR"
    }
    
    # Check for toggleSidebar method
    if ($jsContent -match 'toggleSidebar\s*\(') {
        Write-Property "toggleSidebar() method" "DEFINED" "OK"
        
        # Extract the toggleSidebar implementation
        if ($jsContent -match 'toggleSidebar\s*\(\)\s*\{([^}]+(?:\{[^}]+\}[^}]+)*)\}') {
            $toggleImpl = $matches[1]
            Write-Host "`n  Implementation:" -ForegroundColor Cyan
            
            if ($toggleImpl -match 'getElementById.*transcription-sidebar') {
                Write-Property "  Gets sidebar element" "YES" "OK"
            }
            
            if ($toggleImpl -match '\.classList\.toggle.*collapsed') {
                Write-Property "  Toggles .collapsed class" "YES" "OK"
            }
            
            if ($toggleImpl -match 'transform') {
                Write-Property "  Manipulates transform" "YES" "WARNING"
                Write-Host "  Note: Should use CSS class toggle, not direct style manipulation" -ForegroundColor Yellow
            }
        }
    }
    else {
        Write-Property "toggleSidebar() method" "NOT FOUND" "ERROR"
    }
    
    # Check for init method
    if ($jsContent -match 'init\s*\(') {
        Write-Property "init() method" "DEFINED" "OK"
    }
    
    Write-SubSection "Integration with Main Platform"
    
    # Check if sidebar is injected into DOM
    if ($platformContent -match "fetch.*transcription-sidebar\.html") {
        Write-Property "Sidebar HTML injection" "FOUND in platform" "OK"
        
        # Check where it's injected
        if ($platformContent -match "insertAdjacentHTML.*beforeend.*transcription-sidebar") {
            Write-Property "Injection target" "document.body (beforeend)" "OK"
        }
        elseif ($platformContent -match "innerHTML.*transcription-sidebar") {
            Write-Property "Injection target" "container.innerHTML" "WARNING"
        }
    }
    else {
        Write-Property "Sidebar HTML injection" "NOT FOUND" "ERROR"
    }
}

# ============================================================================
# SECTION 6: KEY DIFFERENCES & ISSUES
# ============================================================================
Write-Section "6. IDENTIFIED ISSUES"

Write-SubSection "Critical Differences from Synergy Sidebar"

$issues = @()

# Check if transcription sidebar has data-side attribute
$htmlContent = Get-Content $transcriptionSidebarHTML -Raw
if ($htmlContent -notmatch 'data-side="left"') {
    $issues += @{
        Level  = "HIGH"
        Issue  = "Missing data-side attribute"
        Impact = "Sidebar won't match synergy-sidebar's positioning logic"
        Fix    = "Add data-side='left' to <div class='transcription-sidebar'>"
    }
}

# Check z-index
$cssContent = Get-Content $transcriptionSidebarCSS -Raw
if ($cssContent -match '\.transcription-sidebar\s*\{[^}]*z-index:\s*(\d+)') {
    $zIndex = [int]$matches[1]
    if ($zIndex -lt 9999) {
        $issues += @{
            Level  = "MEDIUM"
            Issue  = "Lower z-index than synergy-sidebar (1000 vs 9999)"
            Impact = "May be hidden behind other elements"
            Fix    = "Change z-index to 9999 in .transcription-sidebar"
        }
    }
}

# Check for toggle button
if (-not (Test-Path $transcriptionSidebarHTML) -or 
    (Get-Content $transcriptionSidebarHTML -Raw) -notmatch 'class="[^"]*toggle[^"]*"') {
    $issues += @{
        Level  = "HIGH"
        Issue  = "No visible toggle button in HTML"
        Impact = "Users cannot open/close the sidebar"
        Fix    = "Add a floating toggle button like synergy-sidebar-toggle"
    }
}

# Check transform in collapsed state
if ($cssContent -match '\.transcription-sidebar\.collapsed\s*\{[^}]*transform:\s*([^;]+)') {
    $transform = $matches[1].Trim()
    if ($transform -notmatch 'calc\(-100% - 60px\)') {
        $issues += @{
            Level  = "HIGH"
            Issue  = "Collapsed transform doesn't account for left offset"
            Impact = "Sidebar may still be partially visible when collapsed"
            Fix    = "Change transform to: translateX(calc(-100% - 60px))"
        }
    }
}

# Display issues
$issueNum = 1
foreach ($issue in $issues) {
    $levelColor = switch ($issue.Level) {
        "HIGH" { "Red" }
        "MEDIUM" { "Yellow" }
        "LOW" { "Cyan" }
    }
    
    Write-Host "`n  Issue #$issueNum - [$($issue.Level)]" -ForegroundColor $levelColor
    Write-Host "    Problem : $($issue.Issue)" -ForegroundColor White
    Write-Host "    Impact  : $($issue.Impact)" -ForegroundColor Gray
    Write-Host "    Solution: $($issue.Fix)" -ForegroundColor Green
    $issueNum++
}

if ($issues.Count -eq 0) {
    Write-Host "`n  ✓ No critical issues detected" -ForegroundColor Green
}

# ============================================================================
# SECTION 7: RECOMMENDATIONS
# ============================================================================
Write-Section "7. RECOMMENDED FIXES"

Write-Host @"

  To make transcription-sidebar work like synergy-sidebar:

  1. HTML (transcription-sidebar.html):
     ✓ Ensure: <div class="transcription-sidebar collapsed" id="transcription-sidebar" data-side="left">
     ✓ Verify it's injected into document.body (not a container)

  2. CSS (transcription-sidebar.css):
     ✓ Match synergy-sidebar positioning:
       position: fixed;
       top: 60px;
       left: 60px;
       width: 480px;  (or keep 450px)
       height: calc(100vh - 60px);
       z-index: 9999;

     ✓ Collapsed state transform:
       .transcription-sidebar.collapsed {
           transform: translateX(calc(-100% - 60px));
       }

  3. Toggle Button:
     ✓ Create a floating toggle button outside the sidebar:
       <button class="transcription-sidebar-toggle" data-side="left">
           <i class="fas fa-microphone"></i>
       </button>

     ✓ Position it like synergy-sidebar-toggle:
       position: fixed;
       left: 60px;
       z-index: 10000;
       border-radius: 0 12px 12px 0;

  4. JavaScript:
     ✓ Ensure toggleSidebar() only toggles .collapsed class
     ✓ Don't manipulate transform directly - let CSS handle it
     ✓ Register toggle button click handler

  5. Integration:
     ✓ Verify sidebar is injected with: document.body.insertAdjacentHTML('beforeend', html)
     ✓ Not inserted into a tab container or hidden parent

"@ -ForegroundColor Cyan

# ============================================================================
# SECTION 8: FILE SUMMARY
# ============================================================================
Write-Section "8. FILE VERIFICATION"

$files = @(
    @{Path = $transcriptionSidebarHTML; Name = "transcription-sidebar.html" },
    @{Path = $transcriptionSidebarCSS; Name = "transcription-sidebar.css" },
    @{Path = $transcriptionSidebarJS; Name = "transcription-sidebar.js" },
    @{Path = $businessPlatformHTML; Name = "business-ai-platform-v2.html" }
)

foreach ($file in $files) {
    if (Test-Path $file.Path) {
        $size = (Get-Item $file.Path).Length
        $lines = (Get-Content $file.Path).Count
        Write-Host "  ✓ $($file.Name.PadRight(35))" -NoNewline -ForegroundColor Green
        Write-Host " [$($size.ToString('N0').PadLeft(8)) bytes, $($lines.ToString('N0').PadLeft(6)) lines]" -ForegroundColor Gray
    }
    else {
        Write-Host "  ✗ $($file.Name.PadRight(35))" -NoNewline -ForegroundColor Red
        Write-Host " [NOT FOUND]" -ForegroundColor Red
    }
}

# ============================================================================
# END
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DIAGNOSTIC COMPLETE" -ForegroundColor White
Write-Host "  Review issues above and apply recommended fixes" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
