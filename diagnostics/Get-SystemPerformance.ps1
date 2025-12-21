<#
.SYNOPSIS
    Comprehensive System Performance Diagnostics
.DESCRIPTION
    Analyzes CPU, memory, disk, and process performance to identify resource bottlenecks
.AUTHOR
    Generated for Gerardo's System Diagnostics
.DATE
    December 21, 2025
#>

param(
    [int]$SampleDuration = 10,
    [switch]$ExportJSON,
    [string]$OutputPath = ".\diagnostics_output"
)

# Ensure output directory exists
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

Write-Host "🔍 Starting System Performance Diagnostics..." -ForegroundColor Cyan
Write-Host "⏱️  Sample Duration: $SampleDuration seconds" -ForegroundColor Gray

# ============================================================================
# 1. CPU ANALYSIS
# ============================================================================
Write-Host "`n📊 Analyzing CPU Usage..." -ForegroundColor Yellow

$cpuSamples = @()
for ($i = 0; $i -lt $SampleDuration; $i++) {
    $cpu = Get-Counter '\Processor(_Total)\% Processor Time' -ErrorAction SilentlyContinue
    if ($cpu) {
        $cpuSamples += $cpu.CounterSamples[0].CookedValue
    }
    Start-Sleep -Seconds 1
}

$cpuAvg = ($cpuSamples | Measure-Object -Average).Average
$cpuMax = ($cpuSamples | Measure-Object -Maximum).Maximum
$cpuMin = ($cpuSamples | Measure-Object -Minimum).Minimum

$cpuInfo = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, CurrentClockSpeed

Write-Host "  CPU: $($cpuInfo.Name)" -ForegroundColor White
Write-Host "  Cores: $($cpuInfo.NumberOfCores) | Logical: $($cpuInfo.NumberOfLogicalProcessors)" -ForegroundColor White
Write-Host "  Clock: $($cpuInfo.CurrentClockSpeed) MHz / $($cpuInfo.MaxClockSpeed) MHz" -ForegroundColor White
Write-Host "  Average CPU: $([math]::Round($cpuAvg, 2))%" -ForegroundColor $(if ($cpuAvg -gt 80) { "Red" } elseif ($cpuAvg -gt 50) { "Yellow" } else { "Green" })
Write-Host "  Max CPU: $([math]::Round($cpuMax, 2))%" -ForegroundColor $(if ($cpuMax -gt 90) { "Red" } else { "Yellow" })

# ============================================================================
# 2. TOP PROCESSES BY CPU
# ============================================================================
Write-Host "`n🔥 Top 15 Processes by CPU Usage..." -ForegroundColor Yellow

$topCPU = Get-Process | Where-Object { $_.CPU -gt 0 } | 
    Sort-Object CPU -Descending | 
    Select-Object -First 15 -Property @{
        Name='Process'; Expression={$_.Name}
    }, @{
        Name='PID'; Expression={$_.Id}
    }, @{
        Name='CPU(s)'; Expression={[math]::Round($_.CPU, 2)}
    }, @{
        Name='Memory(MB)'; Expression={[math]::Round($_.WorkingSet64/1MB, 2)}
    }, @{
        Name='Threads'; Expression={$_.Threads.Count}
    }, @{
        Name='Handles'; Expression={$_.HandleCount}
    }

$topCPU | Format-Table -AutoSize

# ============================================================================
# 3. MEMORY ANALYSIS
# ============================================================================
Write-Host "`n💾 Memory Analysis..." -ForegroundColor Yellow

$os = Get-CimInstance Win32_OperatingSystem
$totalRAM = [math]::Round($os.TotalVisibleMemorySize/1MB, 2)
$freeRAM = [math]::Round($os.FreePhysicalMemory/1MB, 2)
$usedRAM = $totalRAM - $freeRAM
$memoryUsagePercent = [math]::Round(($usedRAM / $totalRAM) * 100, 2)

Write-Host "  Total RAM: $totalRAM GB" -ForegroundColor White
Write-Host "  Used RAM: $usedRAM GB ($memoryUsagePercent%)" -ForegroundColor $(if ($memoryUsagePercent -gt 85) { "Red" } elseif ($memoryUsagePercent -gt 70) { "Yellow" } else { "Green" })
Write-Host "  Free RAM: $freeRAM GB" -ForegroundColor White

# Top processes by memory
Write-Host "`n🔥 Top 15 Processes by Memory Usage..." -ForegroundColor Yellow
$topMemory = Get-Process | 
    Sort-Object WorkingSet64 -Descending | 
    Select-Object -First 15 -Property @{
        Name='Process'; Expression={$_.Name}
    }, @{
        Name='PID'; Expression={$_.Id}
    }, @{
        Name='Memory(MB)'; Expression={[math]::Round($_.WorkingSet64/1MB, 2)}
    }, @{
        Name='PrivateMB'; Expression={[math]::Round($_.PrivateMemorySize64/1MB, 2)}
    }, @{
        Name='Threads'; Expression={$_.Threads.Count}
    }

$topMemory | Format-Table -AutoSize

# ============================================================================
# 4. DISK ANALYSIS
# ============================================================================
Write-Host "`n💿 Disk Performance..." -ForegroundColor Yellow

$disks = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID, 
    @{Name="Size(GB)"; Expression={[math]::Round($_.Size/1GB, 2)}},
    @{Name="Free(GB)"; Expression={[math]::Round($_.FreeSpace/1GB, 2)}},
    @{Name="Used%"; Expression={[math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 2)}}

$disks | Format-Table -AutoSize

# Disk queue length (indicator of disk bottleneck)
$diskQueue = Get-Counter '\PhysicalDisk(_Total)\Avg. Disk Queue Length' -ErrorAction SilentlyContinue
if ($diskQueue) {
    $queueLength = [math]::Round($diskQueue.CounterSamples[0].CookedValue, 2)
    Write-Host "  Disk Queue Length: $queueLength" -ForegroundColor $(if ($queueLength -gt 2) { "Red" } elseif ($queueLength -gt 1) { "Yellow" } else { "Green" })
    if ($queueLength -gt 2) {
        Write-Host "  ⚠️  HIGH DISK QUEUE - Potential disk bottleneck!" -ForegroundColor Red
    }
}

# ============================================================================
# 5. VS CODE PROCESSES
# ============================================================================
Write-Host "`n🆚 VS Code Processes..." -ForegroundColor Yellow

$vscodeProcesses = Get-Process | Where-Object { 
    $_.ProcessName -like "*code*" -or 
    $_.ProcessName -like "*electron*" -or
    $_.ProcessName -like "*node*" -and $_.Path -like "*VSCode*"
}

if ($vscodeProcesses) {
    $vscodeTotal = $vscodeProcesses | Measure-Object -Property CPU, WorkingSet64 -Sum
    $vscodeCPU = [math]::Round($vscodeTotal[0].Sum, 2)
    $vscodeMemory = [math]::Round($vscodeTotal[1].Sum/1MB, 2)
    
    Write-Host "  Total VS Code CPU: $vscodeCPU seconds" -ForegroundColor Cyan
    Write-Host "  Total VS Code Memory: $vscodeMemory MB" -ForegroundColor Cyan
    Write-Host "  Number of VS Code Processes: $($vscodeProcesses.Count)" -ForegroundColor Cyan
    
    Write-Host "`n  Individual VS Code Processes:" -ForegroundColor Gray
    $vscodeProcesses | Sort-Object CPU -Descending | Select-Object -First 10 -Property @{
        Name='Process'; Expression={$_.ProcessName}
    }, @{
        Name='PID'; Expression={$_.Id}
    }, @{
        Name='CPU(s)'; Expression={[math]::Round($_.CPU, 2)}
    }, @{
        Name='Memory(MB)'; Expression={[math]::Round($_.WorkingSet64/1MB, 2)}
    }, @{
        Name='Threads'; Expression={$_.Threads.Count}
    } | Format-Table -AutoSize
} else {
    Write-Host "  No VS Code processes detected" -ForegroundColor Gray
}

# ============================================================================
# 6. PYTHON PROCESSES
# ============================================================================
Write-Host "`n🐍 Python Processes..." -ForegroundColor Yellow

$pythonProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" }

if ($pythonProcesses) {
    Write-Host "  Number of Python Processes: $($pythonProcesses.Count)" -ForegroundColor Cyan
    
    $pythonProcesses | Sort-Object CPU -Descending | Select-Object -Property @{
        Name='Process'; Expression={$_.ProcessName}
    }, @{
        Name='PID'; Expression={$_.Id}
    }, @{
        Name='CPU(s)'; Expression={[math]::Round($_.CPU, 2)}
    }, @{
        Name='Memory(MB)'; Expression={[math]::Round($_.WorkingSet64/1MB, 2)}
    }, @{
        Name='Threads'; Expression={$_.Threads.Count}
    } | Format-Table -AutoSize
} else {
    Write-Host "  No Python processes detected" -ForegroundColor Gray
}

# ============================================================================
# 7. SYSTEM SERVICES
# ============================================================================
Write-Host "`n⚙️  High-Impact Services..." -ForegroundColor Yellow

$services = Get-Process | Where-Object { $_.SessionId -eq 0 } | 
    Sort-Object CPU -Descending | 
    Select-Object -First 10 -Property @{
        Name='Service'; Expression={$_.Name}
    }, @{
        Name='PID'; Expression={$_.Id}
    }, @{
        Name='CPU(s)'; Expression={[math]::Round($_.CPU, 2)}
    }, @{
        Name='Memory(MB)'; Expression={[math]::Round($_.WorkingSet64/1MB, 2)}
    }

$services | Format-Table -AutoSize

# ============================================================================
# 8. THERMAL AND POWER INFO
# ============================================================================
Write-Host "`n🌡️  Power & Thermal..." -ForegroundColor Yellow

$battery = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
if ($battery) {
    Write-Host "  Battery Status: $($battery.BatteryStatus)" -ForegroundColor White
    Write-Host "  Estimated Charge: $($battery.EstimatedChargeRemaining)%" -ForegroundColor White
}

$powerPlan = Get-CimInstance Win32_PowerPlan -Namespace root\cimv2\power | Where-Object { $_.IsActive -eq $true }
if ($powerPlan) {
    Write-Host "  Active Power Plan: $($powerPlan.ElementName)" -ForegroundColor White
}

# ============================================================================
# 9. NETWORK ACTIVITY
# ============================================================================
Write-Host "`n🌐 Network Activity..." -ForegroundColor Yellow

$netstat = netstat -ano | Select-String "ESTABLISHED"
$establishedConnections = $netstat.Count

Write-Host "  Established Connections: $establishedConnections" -ForegroundColor White

# ============================================================================
# 10. RECOMMENDATIONS
# ============================================================================
Write-Host "`n💡 Recommendations..." -ForegroundColor Green

$recommendations = @()

if ($cpuAvg -gt 80) {
    $recommendations += "🔴 HIGH CPU USAGE: Average CPU at $([math]::Round($cpuAvg, 2))% - Consider closing unnecessary applications"
}

if ($memoryUsagePercent -gt 85) {
    $recommendations += "🔴 HIGH MEMORY USAGE: $memoryUsagePercent% used - Consider closing memory-intensive applications or upgrading RAM"
}

if ($diskQueue -and $diskQueue.CounterSamples[0].CookedValue -gt 2) {
    $recommendations += "🔴 DISK BOTTLENECK: High disk queue - Consider SSD upgrade or closing disk-intensive processes"
}

if ($vscodeProcesses -and $vscodeProcesses.Count -gt 20) {
    $recommendations += "🟡 MULTIPLE VS CODE PROCESSES: $($vscodeProcesses.Count) processes detected - Consider closing unused extensions or workspaces"
}

if ($pythonProcesses -and $pythonProcesses.Count -gt 5) {
    $recommendations += "🟡 MULTIPLE PYTHON PROCESSES: $($pythonProcesses.Count) processes - Check for background scripts or orphaned processes"
}

if ($recommendations.Count -eq 0) {
    Write-Host "  ✅ System performance looks healthy!" -ForegroundColor Green
} else {
    $recommendations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
}

# ============================================================================
# 11. EXPORT RESULTS
# ============================================================================
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

$diagnosticsData = @{
    Timestamp = $timestamp
    CPU = @{
        Info = $cpuInfo
        AverageUsage = $cpuAvg
        MaxUsage = $cpuMax
        MinUsage = $cpuMin
        Samples = $cpuSamples
        TopProcesses = $topCPU
    }
    Memory = @{
        TotalGB = $totalRAM
        UsedGB = $usedRAM
        FreeGB = $freeRAM
        UsagePercent = $memoryUsagePercent
        TopProcesses = $topMemory
    }
    Disk = @{
        Disks = $disks
        QueueLength = if ($diskQueue) { $diskQueue.CounterSamples[0].CookedValue } else { $null }
    }
    VSCode = @{
        ProcessCount = if ($vscodeProcesses) { $vscodeProcesses.Count } else { 0 }
        TotalCPU = if ($vscodeProcesses) { $vscodeCPU } else { 0 }
        TotalMemoryMB = if ($vscodeProcesses) { $vscodeMemory } else { 0 }
        Processes = $vscodeProcesses
    }
    Python = @{
        ProcessCount = if ($pythonProcesses) { $pythonProcesses.Count } else { 0 }
        Processes = $pythonProcesses
    }
    Network = @{
        EstablishedConnections = $establishedConnections
    }
    Recommendations = $recommendations
}

if ($ExportJSON) {
    $jsonPath = Join-Path $OutputPath "system_diagnostics_$timestamp.json"
    $diagnosticsData | ConvertTo-Json -Depth 10 | Out-File $jsonPath
    Write-Host "`n📄 Diagnostics exported to: $jsonPath" -ForegroundColor Cyan
}

Write-Host "`n✅ Diagnostics Complete!" -ForegroundColor Green
Write-Host "Run with -ExportJSON to save results to JSON file" -ForegroundColor Gray

return $diagnosticsData
