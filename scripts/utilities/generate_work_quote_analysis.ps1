# Work Quote Analysis Script
# Analyzes git history, file counts, and code metrics to generate quote data

param(
    [string]$OutputPath = ".\work_quote_analysis.json",
    [string]$HtmlOutputPath = ".\work_quote_report.html"
)

Write-Host "`n=== WORK QUOTE ANALYSIS ===" -ForegroundColor Cyan
Write-Host "Analyzing AI_agents and In_House_SQL projects..." -ForegroundColor White

$results = @{
    generated_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    projects     = @()
}

function Analyze-Repository {
    param([string]$Path, [string]$Name)
    
    Write-Host "`n--- Analyzing: $Name ---" -ForegroundColor Yellow
    
    if (-not (Test-Path "$Path\.git")) {
        Write-Host "Not a git repository: $Path" -ForegroundColor Red
        return $null
    }
    
    Push-Location $Path
    
    # Basic stats
    $totalCommits = (git log --all --pretty=format:"%H" | Measure-Object).Count
    $totalFiles = (git ls-files | Measure-Object).Count
    $totalBranches = (git branch -a | Measure-Object).Count
    
    # Timeline
    $firstCommit = git log --all --reverse --pretty=format:"%ai|%s" | Select-Object -First 1
    $lastCommit = git log --all --pretty=format:"%ai|%s" | Select-Object -First 1
    
    $firstDate = if ($firstCommit) { ($firstCommit -split '\|')[0] } else { "N/A" }
    $lastDate = if ($lastCommit) { ($lastCommit -split '\|')[0] } else { "N/A" }
    
    # Calculate days
    $days = 0
    if ($firstDate -ne "N/A" -and $lastDate -ne "N/A") {
        $start = [DateTime]::Parse($firstDate)
        $end = [DateTime]::Parse($lastDate)
        $days = ($end - $start).Days
    }
    
    # Lines of code (Python, JavaScript, etc.)
    $codeExtensions = @('*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.html', '*.css', '*.json')
    $totalLines = 0
    foreach ($ext in $codeExtensions) {
        $files = git ls-files "*$ext" 2>$null
        if ($files) {
            foreach ($file in $files) {
                if (Test-Path $file) {
                    $totalLines += (Get-Content $file -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
                }
            }
        }
    }
    
    # Commits by author
    $authorCommits = git log --all --pretty=format:"%an" | Group-Object | 
    Select-Object @{Name = 'Author'; Expression = { $_.Name } }, @{Name = 'Commits'; Expression = { $_.Count } } |
    Sort-Object Commits -Descending
    
    # File types breakdown
    $fileTypes = git ls-files | ForEach-Object {
        $ext = [System.IO.Path]::GetExtension($_)
        if ($ext) { $ext } else { "no_extension" }
    } | Group-Object | Select-Object @{Name = 'Extension'; Expression = { $_.Name } }, @{Name = 'Count'; Expression = { $_.Count } } |
    Sort-Object Count -Descending | Select-Object -First 15
    
    # Changed files statistics
    $changedFilesStats = git log --all --pretty=format: --numstat | 
    Select-String -Pattern '^\d+\s+\d+\s+' | 
    ForEach-Object {
        $parts = $_ -split '\s+'
        [PSCustomObject]@{
            Added   = [int]$parts[0]
            Deleted = [int]$parts[1]
        }
    }
    
    $totalAdded = ($changedFilesStats | Measure-Object -Property Added -Sum).Sum
    $totalDeleted = ($changedFilesStats | Measure-Object -Property Deleted -Sum).Sum
    
    # Recent activity (last 30 days)
    $thirtyDaysAgo = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
    $recentCommits = (git log --all --since="$thirtyDaysAgo" --pretty=format:"%H" | Measure-Object).Count
    
    Pop-Location
    
    $projectData = @{
        name     = $Name
        path     = $Path
        commits  = @{
            total          = $totalCommits
            recent_30_days = $recentCommits
            by_author      = $authorCommits
        }
        timeline = @{
            first_commit    = $firstDate
            last_commit     = $lastDate
            duration_days   = $days
            duration_months = [math]::Round($days / 30, 1)
        }
        files    = @{
            total   = $totalFiles
            by_type = $fileTypes
        }
        code     = @{
            total_lines   = $totalLines
            lines_added   = $totalAdded
            lines_deleted = $totalDeleted
            net_lines     = $totalAdded - $totalDeleted
        }
        branches = $totalBranches
    }
    
    Write-Host "  Commits: $totalCommits" -ForegroundColor Green
    Write-Host "  Files: $totalFiles" -ForegroundColor Green
    Write-Host "  Lines of Code: $totalLines" -ForegroundColor Green
    Write-Host "  Duration: $days days ($([math]::Round($days/30, 1)) months)" -ForegroundColor Green
    
    return $projectData
}

# Analyze both projects
$aiAgentsData = Analyze-Repository -Path "c:\Users\gpoli\GIT\AI_agents" -Name "AI_agents"
$gFolderData = Analyze-Repository -Path "c:\Users\gpoli\GIT\In_House_SQL" -Name "In_House_SQL (G_Folder)"

if ($aiAgentsData) { $results.projects += $aiAgentsData }
if ($gFolderData) { $results.projects += $gFolderData }

# Calculate totals
$totalCommits = 0
$totalFiles = 0
$totalLines = 0
$totalAdded = 0
$totalDays = 0

foreach ($proj in $results.projects) {
    $totalCommits += $proj.commits.total
    $totalFiles += $proj.files.total
    $totalLines += $proj.code.total_lines
    $totalAdded += $proj.code.lines_added
    $totalDays += $proj.timeline.duration_days
}

$results.totals = @{
    total_commits       = $totalCommits
    total_files         = $totalFiles
    total_lines         = $totalLines
    total_lines_added   = $totalAdded
    total_duration_days = $totalDays
}

# Estimated hours calculation (multiple methods)
$results.time_estimates = @{
    method_1_commits     = @{
        description = "Based on commits (avg 2 hours per commit)"
        hours       = $results.totals.total_commits * 2
    }
    method_2_lines       = @{
        description = "Based on lines of code (avg 50 lines per hour)"
        hours       = [math]::Round($results.totals.total_lines / 50, 0)
    }
    method_3_active_days = @{
        description = "Based on active development days (avg 6 hours per day)"
        hours       = $results.totals.total_duration_days * 0.4 * 6  # Assuming 40% of days were active
    }
    method_4_files       = @{
        description = "Based on files created/modified (avg 0.5 hours per file)"
        hours       = $results.totals.total_files * 0.5
    }
}

# Calculate average estimated hours
$avgHours = [math]::Round((
        $results.time_estimates.method_1_commits.hours +
        $results.time_estimates.method_2_lines.hours +
        $results.time_estimates.method_3_active_days.hours +
        $results.time_estimates.method_4_files.hours
    ) / 4, 0)

$results.time_estimates.average_estimate = @{
    description = "Average of all methods"
    hours       = $avgHours
}

# Save JSON
$results | ConvertTo-Json -Depth 10 | Out-File -Encoding UTF8 $OutputPath

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total Commits: $($results.totals.total_commits)" -ForegroundColor White
Write-Host "Total Files: $($results.totals.total_files)" -ForegroundColor White
Write-Host "Total Lines of Code: $($results.totals.total_lines)" -ForegroundColor White
Write-Host "`nEstimated Hours:" -ForegroundColor Cyan
Write-Host "  Method 1 (Commits): $($results.time_estimates.method_1_commits.hours) hours" -ForegroundColor White
Write-Host "  Method 2 (Lines): $($results.time_estimates.method_2_lines.hours) hours" -ForegroundColor White
Write-Host "  Method 3 (Active Days): $($results.time_estimates.method_3_active_days.hours) hours" -ForegroundColor White
Write-Host "  Method 4 (Files): $($results.time_estimates.method_4_files.hours) hours" -ForegroundColor White
Write-Host "  AVERAGE ESTIMATE: $avgHours hours" -ForegroundColor Green
Write-Host "`nJSON saved to: $OutputPath" -ForegroundColor Yellow

# Generate HTML Report
$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Work Quote Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .summary { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .metric { display: inline-block; margin: 15px 30px 15px 0; }
        .metric-label { color: #7f8c8d; font-size: 14px; }
        .metric-value { color: #2c3e50; font-size: 28px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #3498db; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f8f9fa; }
        .highlight { background: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0; }
        .project-section { margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Work Quote Analysis Report</h1>
        <p><strong>Generated:</strong> $($results.generated_at)</p>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="metric">
                <div class="metric-label">Total Commits</div>
                <div class="metric-value">$($results.totals.total_commits)</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Files</div>
                <div class="metric-value">$($results.totals.total_files)</div>
            </div>
            <div class="metric">
                <div class="metric-label">Lines of Code</div>
                <div class="metric-value">$($results.totals.total_lines)</div>
            </div>
            <div class="metric">
                <div class="metric-label">Lines Added</div>
                <div class="metric-value">$($results.totals.total_lines_added)</div>
            </div>
        </div>
        
        <div class="highlight">
            <h2>Estimated Work Hours</h2>
            <table>
                <tr>
                    <th>Method</th>
                    <th>Description</th>
                    <th>Hours</th>
                </tr>
                <tr>
                    <td><strong>Method 1</strong></td>
                    <td>$($results.time_estimates.method_1_commits.description)</td>
                    <td><strong>$($results.time_estimates.method_1_commits.hours)</strong></td>
                </tr>
                <tr>
                    <td><strong>Method 2</strong></td>
                    <td>$($results.time_estimates.method_2_lines.description)</td>
                    <td><strong>$($results.time_estimates.method_2_lines.hours)</strong></td>
                </tr>
                <tr>
                    <td><strong>Method 3</strong></td>
                    <td>$($results.time_estimates.method_3_active_days.description)</td>
                    <td><strong>$($results.time_estimates.method_3_active_days.hours)</strong></td>
                </tr>
                <tr>
                    <td><strong>Method 4</strong></td>
                    <td>$($results.time_estimates.method_4_files.description)</td>
                    <td><strong>$($results.time_estimates.method_4_files.hours)</strong></td>
                </tr>
                <tr style="background: #d4edda;">
                    <td><strong>AVERAGE</strong></td>
                    <td>$($results.time_estimates.average_estimate.description)</td>
                    <td><strong style="font-size: 24px; color: #155724;">$($results.time_estimates.average_estimate.hours) hours</strong></td>
                </tr>
            </table>
        </div>
"@

# Add project details
foreach ($project in $results.projects) {
    $html += @"
        <div class="project-section">
            <h2>$($project.name)</h2>
            <p><strong>Path:</strong> $($project.path)</p>
            <p><strong>Duration:</strong> $($project.timeline.first_commit) to $($project.timeline.last_commit) 
               ($($project.timeline.duration_days) days / $($project.timeline.duration_months) months)</p>
            
            <h3>Metrics</h3>
            <table>
                <tr><td>Total Commits</td><td>$($project.commits.total)</td></tr>
                <tr><td>Recent Commits (30 days)</td><td>$($project.commits.recent_30_days)</td></tr>
                <tr><td>Total Files</td><td>$($project.files.total)</td></tr>
                <tr><td>Total Lines of Code</td><td>$($project.code.total_lines)</td></tr>
                <tr><td>Lines Added</td><td>$($project.code.lines_added)</td></tr>
                <tr><td>Lines Deleted</td><td>$($project.code.lines_deleted)</td></tr>
                <tr><td>Net Lines</td><td>$($project.code.net_lines)</td></tr>
                <tr><td>Branches</td><td>$($project.branches)</td></tr>
            </table>
        </div>
"@
}

$html += @"
    </div>
</body>
</html>
"@

$html | Out-File -Encoding UTF8 $HtmlOutputPath
Write-Host "HTML report saved to: $HtmlOutputPath" -ForegroundColor Yellow
Write-Host "`nDone!" -ForegroundColor Green
