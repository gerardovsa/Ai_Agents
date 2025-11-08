# Git Contribution Analysis Script
# Analyzes individual contributor statistics for work quote purposes

param(
    [string]$RepoPath = ".",
    [string]$OutputFile = "git_contribution_analysis.txt"
)

Write-Host "`n=== GIT CONTRIBUTION ANALYSIS ===" -ForegroundColor Cyan
Write-Host "Analyzing repository: $RepoPath`n" -ForegroundColor White

Push-Location $RepoPath

# Get repository name
$repoName = Split-Path -Leaf (Get-Location)
Write-Host "Repository: $repoName" -ForegroundColor Yellow

# Author statistics
Write-Host "`n--- AUTHOR STATISTICS ---" -ForegroundColor Cyan
$authors = git log --all --format='%aN' | Sort-Object | Get-Unique
Write-Host "Total Authors: $($authors.Count)" -ForegroundColor Green

$authorStats = @()
foreach ($author in $authors) {
    $commits = (git log --all --author="$author" --oneline | Measure-Object).Count
    $added = git log --all --author="$author" --pretty=tformat: --numstat | 
    Select-String '^\d+' | 
    ForEach-Object { ($_ -split '\s+')[0] } |
    Measure-Object -Sum |
    Select-Object -ExpandProperty Sum
    $deleted = git log --all --author="$author" --pretty=tformat: --numstat | 
    Select-String '^\d+' | 
    ForEach-Object { ($_ -split '\s+')[1] } |
    Measure-Object -Sum |
    Select-Object -ExpandProperty Sum
    
    $authorStats += [PSCustomObject]@{
        Author       = $author
        Commits      = $commits
        LinesAdded   = if ($added) { $added } else { 0 }
        LinesDeleted = if ($deleted) { $deleted } else { 0 }
        NetLines     = if ($added -and $deleted) { $added - $deleted } else { if ($added) { $added } else { 0 } }
    }
}

$authorStats | Sort-Object Commits -Descending | Format-Table -AutoSize

# Commit frequency by date
Write-Host "`n--- COMMIT FREQUENCY ---" -ForegroundColor Cyan
$commitsByDate = git log --all --pretty=format:"%ai" | 
ForEach-Object { $_.Substring(0, 10) } | 
Group-Object | 
Select-Object @{Name = 'Date'; Expression = { $_.Name } }, @{Name = 'Commits'; Expression = { $_.Count } } |
Sort-Object Date

Write-Host "Total Active Days: $($commitsByDate.Count)" -ForegroundColor Green
Write-Host "Peak Activity Day: $(($commitsByDate | Sort-Object Commits -Descending | Select-Object -First 1).Date) with $(($commitsByDate | Sort-Object Commits -Descending | Select-Object -First 1).Commits) commits" -ForegroundColor Green

# Commit frequency by day of week
Write-Host "`n--- COMMITS BY DAY OF WEEK ---" -ForegroundColor Cyan
$commitsByDayOfWeek = git log --all --pretty=format:"%ai" |
ForEach-Object { [DateTime]::Parse($_).DayOfWeek } |
Group-Object |
Select-Object @{Name = 'DayOfWeek'; Expression = { $_.Name } }, @{Name = 'Commits'; Expression = { $_.Count } } |
Sort-Object Commits -Descending

$commitsByDayOfWeek | Format-Table -AutoSize

# Commit frequency by hour
Write-Host "`n--- COMMITS BY HOUR OF DAY ---" -ForegroundColor Cyan
$commitsByHour = git log --all --pretty=format:"%ai" |
ForEach-Object { ([DateTime]::Parse($_)).Hour } |
Group-Object |
Select-Object @{Name = 'Hour'; Expression = { $_.Name } }, @{Name = 'Commits'; Expression = { $_.Count } } |
Sort-Object Hour

$commitsByHour | Format-Table -AutoSize

# File type statistics
Write-Host "`n--- FILE TYPE STATISTICS ---" -ForegroundColor Cyan
$fileTypes = git ls-files | 
ForEach-Object { [System.IO.Path]::GetExtension($_) } |
Where-Object { $_ } |
Group-Object |
Select-Object @{Name = 'FileType'; Expression = { $_.Name } }, @{Name = 'Count'; Expression = { $_.Count } } |
Sort-Object Count -Descending |
Select-Object -First 20

$fileTypes | Format-Table -AutoSize

# Largest files
Write-Host "`n--- LARGEST FILES (Top 20) ---" -ForegroundColor Cyan
$largestFiles = git ls-files | 
Where-Object { Test-Path $_ } |
ForEach-Object {
    $file = $_
    $size = (Get-Item $file -ErrorAction SilentlyContinue).Length
    if ($size) {
        [PSCustomObject]@{
            File   = $file
            Size   = $size
            SizeKB = [math]::Round($size / 1KB, 2)
        }
    }
} |
Sort-Object Size -Descending |
Select-Object -First 20

$largestFiles | Format-Table File, SizeKB -AutoSize

# Recent activity (last 30 days)
Write-Host "`n--- RECENT ACTIVITY (Last 30 Days) ---" -ForegroundColor Cyan
$thirtyDaysAgo = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
$recentCommits = (git log --all --since="$thirtyDaysAgo" --oneline | Measure-Object).Count
$recentAuthors = git log --all --since="$thirtyDaysAgo" --format='%aN' | Sort-Object | Get-Unique
Write-Host "Recent Commits: $recentCommits" -ForegroundColor Green
Write-Host "Active Authors: $($recentAuthors.Count)" -ForegroundColor Green

# Branch statistics
Write-Host "`n--- BRANCH STATISTICS ---" -ForegroundColor Cyan
$allBranches = git branch -a
$localBranches = git branch | Measure-Object
$remoteBranches = git branch -r | Measure-Object
Write-Host "Local Branches: $($localBranches.Count)" -ForegroundColor Green
Write-Host "Remote Branches: $($remoteBranches.Count)" -ForegroundColor Green

# Most modified files
Write-Host "`n--- MOST MODIFIED FILES (Top 20) ---" -ForegroundColor Cyan
$mostModified = git log --all --pretty=format: --name-only |
Where-Object { $_ } |
Group-Object |
Select-Object @{Name = 'File'; Expression = { $_.Name } }, @{Name = 'Modifications'; Expression = { $_.Count } } |
Sort-Object Modifications -Descending |
Select-Object -First 20

$mostModified | Format-Table -AutoSize

# Commit message analysis
Write-Host "`n--- COMMIT MESSAGE KEYWORDS ---" -ForegroundColor Cyan
$keywords = @('fix', 'bug', 'feature', 'add', 'update', 'refactor', 'implement', 'create', 'remove', 'delete')
foreach ($keyword in $keywords) {
    $count = (git log --all --oneline --grep="$keyword" -i | Measure-Object).Count
    if ($count -gt 0) {
        Write-Host "$keyword : $count commits" -ForegroundColor White
    }
}

# Summary statistics
Write-Host "`n=== SUMMARY STATISTICS ===" -ForegroundColor Cyan
$totalCommits = (git log --all --oneline | Measure-Object).Count
$totalFiles = (git ls-files | Measure-Object).Count
$totalAuthors = $authors.Count
$activeDays = $commitsByDate.Count
$avgCommitsPerDay = if ($activeDays -gt 0) { [math]::Round($totalCommits / $activeDays, 2) } else { 0 }

Write-Host "Total Commits: $totalCommits" -ForegroundColor Green
Write-Host "Total Files: $totalFiles" -ForegroundColor Green
Write-Host "Total Authors: $totalAuthors" -ForegroundColor Green
Write-Host "Active Development Days: $activeDays" -ForegroundColor Green
Write-Host "Average Commits per Active Day: $avgCommitsPerDay" -ForegroundColor Green

# Calculate estimated work hours
Write-Host "`n=== ESTIMATED WORK HOURS ===" -ForegroundColor Cyan

$method1 = $totalCommits * 2
Write-Host "Method 1 (2 hrs/commit): $method1 hours" -ForegroundColor White

$method2 = $activeDays * 6
Write-Host "Method 2 (6 hrs/active day): $method2 hours" -ForegroundColor White

$totalLines = ($authorStats | Measure-Object -Property LinesAdded -Sum).Sum
$method3 = [math]::Round($totalLines / 50, 0)
Write-Host "Method 3 (50 lines/hr): $method3 hours" -ForegroundColor White

$avgEstimate = [math]::Round(($method1 + $method2 + $method3) / 3, 0)
Write-Host "`nAverage Estimate: $avgEstimate hours" -ForegroundColor Green

# Generate report
$report = @"
===================================================================
GIT CONTRIBUTION ANALYSIS REPORT
===================================================================
Repository: $repoName
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

SUMMARY STATISTICS
-------------------------------------------------------------------
Total Commits: $totalCommits
Total Files: $totalFiles
Total Authors: $totalAuthors
Active Development Days: $activeDays
Average Commits per Day: $avgCommitsPerDay

AUTHOR STATISTICS
-------------------------------------------------------------------
$($authorStats | Sort-Object Commits -Descending | Format-Table -AutoSize | Out-String)

COMMIT FREQUENCY BY DATE
-------------------------------------------------------------------
$($commitsByDate | Format-Table -AutoSize | Out-String)

COMMIT FREQUENCY BY DAY OF WEEK
-------------------------------------------------------------------
$($commitsByDayOfWeek | Format-Table -AutoSize | Out-String)

FILE TYPE STATISTICS
-------------------------------------------------------------------
$($fileTypes | Format-Table -AutoSize | Out-String)

ESTIMATED WORK HOURS
-------------------------------------------------------------------
Method 1 (2 hrs/commit): $method1 hours
Method 2 (6 hrs/active day): $method2 hours
Method 3 (50 lines/hr): $method3 hours

Average Estimate: $avgEstimate hours

===================================================================
"@

$report | Out-File -Encoding UTF8 $OutputFile
Write-Host "`nReport saved to: $OutputFile" -ForegroundColor Yellow

Pop-Location

Write-Host "`nDone!" -ForegroundColor Green
