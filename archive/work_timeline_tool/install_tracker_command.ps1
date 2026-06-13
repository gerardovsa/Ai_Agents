# Install TRACKER as a global PowerShell command
# This script adds the TRACKER function to your PowerShell profile

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Installing TRACKER Global Command" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$profilePath = $PROFILE

# Check if profile exists
if (-not (Test-Path $profilePath)) {
    Write-Host "Creating PowerShell profile..." -ForegroundColor Yellow
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
}

# The TRACKER function to add
$trackerFunction = @'

# TRACKER - Work Timeline Tool Global Command
function TRACKER {
    $ErrorActionPreference = "Stop"
    
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host "   TRACKER - Work Timeline Generator" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Define tool path
    $toolPath = "C:\Users\gpoli\GIT\AI_agents\work_timeline_tool"
    $configPath = Join-Path $toolPath "config.py"
    $scriptPath = Join-Path $toolPath "create_focused_timeline.py"
    $outputPath = Join-Path $toolPath "focused_timeline_detailed.html"
    
    # Check if tool exists
    if (-not (Test-Path $toolPath)) {
        Write-Host "[ERROR] Work Timeline Tool not found at:" -ForegroundColor Red
        Write-Host "  $toolPath" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please ensure the tool is installed in the correct location." -ForegroundColor Yellow
        return
    }
    
    # Save current location
    $currentLocation = Get-Location
    
    # Change to tool directory
    Write-Host "[1/4] Navigating to tool directory..." -ForegroundColor Green
    Set-Location $toolPath
    
    # Check if config exists
    if (-not (Test-Path $configPath)) {
        Write-Host ""
        Write-Host "[WARNING] config.py not found!" -ForegroundColor Yellow
        Write-Host "Creating from template..." -ForegroundColor Yellow
        
        $templatePath = Join-Path $toolPath "config_template.py"
        if (Test-Path $templatePath) {
            Copy-Item $templatePath $configPath
            Write-Host "[SUCCESS] config.py created from template" -ForegroundColor Green
            Write-Host ""
            Write-Host "Please edit config.py with your project paths:" -ForegroundColor Cyan
            Write-Host "  $configPath" -ForegroundColor White
            Write-Host ""
            
            # Open config in VS Code or default editor
            try {
                code $configPath
                Write-Host "Opened in VS Code" -ForegroundColor Green
            } catch {
                Start-Process notepad $configPath
                Write-Host "Opened in Notepad" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "After editing config.py, run TRACKER again." -ForegroundColor Yellow
            Set-Location $currentLocation
            return
        } else {
            Write-Host "[ERROR] config_template.py not found!" -ForegroundColor Red
            Set-Location $currentLocation
            return
        }
    }
    
    # Check Python
    Write-Host "[2/4] Checking Python..." -ForegroundColor Green
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "  $pythonVersion" -ForegroundColor Gray
    } catch {
        Write-Host "[ERROR] Python not found! Please install Python 3.x" -ForegroundColor Red
        Set-Location $currentLocation
        return
    }
    
    # Generate timeline
    Write-Host "[3/4] Generating timeline..." -ForegroundColor Green
    Write-Host "  (This may take a few moments for large projects)" -ForegroundColor Gray
    Write-Host ""
    
    try {
        python $scriptPath
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Timeline generation failed!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Common issues:" -ForegroundColor Yellow
            Write-Host "  - Invalid project paths in config.py" -ForegroundColor White
            Write-Host "  - Missing project folders" -ForegroundColor White
            Write-Host "  - Permission issues" -ForegroundColor White
            Write-Host ""
            Set-Location $currentLocation
            return
        }
    } catch {
        Write-Host "[ERROR] Failed to run Python script: $_" -ForegroundColor Red
        Set-Location $currentLocation
        return
    }
    
    # Check if output was created
    if (-not (Test-Path $outputPath)) {
        Write-Host "[ERROR] Output file not generated!" -ForegroundColor Red
        Write-Host "Expected at: $outputPath" -ForegroundColor Yellow
        Set-Location $currentLocation
        return
    }
    
    # Open in new browser tab
    Write-Host "[4/4] Opening timeline in new browser tab..." -ForegroundColor Green
    
    try {
        # Use default browser to open in new tab
        Start-Process $outputPath
        
        Write-Host ""
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host "   SUCCESS! Timeline Generated & Opened" -ForegroundColor Green
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Dashboard opened in your browser:" -ForegroundColor White
        Write-Host "  $outputPath" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Features:" -ForegroundColor Cyan
        Write-Host "  - Timeline View (visual file changes)" -ForegroundColor White
        Write-Host "  - Labor Summary (project breakdown)" -ForegroundColor White
        Write-Host "  - Daily Hours (all dates, auto-populated!)" -ForegroundColor White
        Write-Host "  - Work Intensity (top days)" -ForegroundColor White
        Write-Host "  - Combined Analysis (schedule breakdown)" -ForegroundColor White
        Write-Host ""
        Write-Host "Tip: Run TRACKER anytime to regenerate with latest data" -ForegroundColor Yellow
        Write-Host ""
        
    } catch {
        Write-Host "[ERROR] Failed to open browser: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "You can manually open:" -ForegroundColor Yellow
        Write-Host "  $outputPath" -ForegroundColor White
    }
    
    # Return to original location
    Set-Location $currentLocation
}
'@

# Check if TRACKER already exists in profile
$profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue

if ($profileContent -like "*function TRACKER*") {
    Write-Host "[INFO] TRACKER function already exists in profile" -ForegroundColor Yellow
    Write-Host ""
    $overwrite = Read-Host "Do you want to update it? (y/n)"
    
    if ($overwrite -eq 'y') {
        # Remove old TRACKER function
        $lines = Get-Content $profilePath
        $inTrackerFunction = $false
        $newLines = @()
        
        foreach ($line in $lines) {
            if ($line -match "^# TRACKER - Work Timeline Tool Global Command") {
                $inTrackerFunction = $true
            }
            elseif ($inTrackerFunction -and $line -match "^function " -and $line -notmatch "^function TRACKER") {
                $inTrackerFunction = $false
            }
            
            if (-not $inTrackerFunction) {
                $newLines += $line
            }
        }
        
        # Write back without TRACKER
        $newLines -join "`n" | Out-File $profilePath -Encoding UTF8
        
        # Add new TRACKER
        Add-Content -Path $profilePath -Value $trackerFunction
        Write-Host "[SUCCESS] TRACKER function updated!" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIPPED] Keeping existing TRACKER function" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To test, run: TRACKER" -ForegroundColor Cyan
        exit 0
    }
}
else {
    # Add TRACKER function to profile
    Add-Content -Path $profilePath -Value $trackerFunction
    Write-Host "[SUCCESS] TRACKER function added to PowerShell profile!" -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "   Installation Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "The TRACKER command has been installed." -ForegroundColor White
Write-Host ""
Write-Host "To use it:" -ForegroundColor Cyan
Write-Host "  1. Restart PowerShell (or run: . `$PROFILE)" -ForegroundColor White
Write-Host "  2. Run: TRACKER" -ForegroundColor White
Write-Host "  3. Timeline generates and opens in browser!" -ForegroundColor White
Write-Host ""
Write-Host "You can run TRACKER from ANY folder" -ForegroundColor Yellow
Write-Host ""

# Offer to reload profile now
$reload = Read-Host "Reload PowerShell profile now to use TRACKER immediately? (y/n)"

if ($reload -eq 'y') {
    . $PROFILE
    Write-Host ""
    Write-Host "[SUCCESS] Profile reloaded! You can now run: TRACKER" -ForegroundColor Green
    Write-Host ""
}
