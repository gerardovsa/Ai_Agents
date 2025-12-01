#Requires -Version 5.1
<#
.SYNOPSIS
    Create new version branch with automatic configuration
    
.DESCRIPTION
    Automates creation of new version branches (v11, v12, v13...)
    - Creates new branch from current branch
    - Copies and updates render config template
    - Updates GitHub Actions workflow
    - Commits changes and pushes to remote
    
.PARAMETER Version
    Version number to create (e.g., 11 for v11)
    
.PARAMETER BaseBranch
    Branch to create from (default: current branch)
    
.PARAMETER Push
    Push changes to remote after commit (default: true)
    
.EXAMPLE
    .\create_new_version.ps1 -Version 11
    
.EXAMPLE
    .\create_new_version.ps1 -Version 12 -BaseBranch v11 -Push:$false
#>

param(
    [Parameter(Mandatory = $true)]
    [int]$Version,
    
    [Parameter(Mandatory = $false)]
    [string]$BaseBranch = "",
    
    [Parameter(Mandatory = $false)]
    [bool]$Push = $true
)

$ErrorActionPreference = "Stop"

# Colors for output
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"
$ErrorColor = "Red"

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $SuccessColor
}

function Write-Warn {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $WarningColor
}

function Write-Fail {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ErrorColor
}

# Validate version number
if ($Version -lt 1) {
    Write-Fail "Version must be a positive number"
    exit 1
}

$VersionBranch = "v$Version"
$ProjectRoot = "c:\Users\gpoli\GIT\AI_agents"

Write-Host "`n🚀 Creating new version: $VersionBranch" -ForegroundColor $InfoColor
Write-Host "=" * 60 -ForegroundColor $InfoColor

# Step 1: Navigate to project root
Write-Step "Navigating to project root..."
Set-Location $ProjectRoot
Write-Success "In directory: $ProjectRoot"

# Step 2: Get current branch if not specified
if ([string]::IsNullOrEmpty($BaseBranch)) {
    $BaseBranch = git rev-parse --abbrev-ref HEAD
    Write-Step "Using current branch as base: $BaseBranch"
}
else {
    Write-Step "Using specified base branch: $BaseBranch"
}

# Step 3: Check if branch already exists
Write-Step "Checking if branch exists..."
$BranchExists = git branch --list $VersionBranch
if ($BranchExists) {
    Write-Fail "Branch '$VersionBranch' already exists!"
    Write-Host "To recreate, delete it first: git branch -D $VersionBranch"
    exit 1
}
Write-Success "Branch name available: $VersionBranch"

# Step 4: Create and checkout new branch
Write-Step "Creating new branch from $BaseBranch..."
git checkout -b $VersionBranch $BaseBranch
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Failed to create branch"
    exit 1
}
Write-Success "Branch created and checked out"

# Step 5: Create version_info.json
Write-Step "Creating version_info.json..."
$VersionInfo = @{
    branch       = $VersionBranch
    version      = $Version.ToString()
    expected_url = "https://ai-agents-v$Version.onrender.com"
    commit       = (git rev-parse --short HEAD)
} | ConvertTo-Json

$VersionInfo | Out-File -FilePath "$ProjectRoot\AI_infrastructure\version_info.json" -Encoding UTF8
Write-Success "Version info created"

# Step 6: Update render.yaml (if template exists)
$RenderYaml = "$ProjectRoot\render.yaml"
if (Test-Path $RenderYaml) {
    Write-Step "Updating render.yaml..."
    $Content = Get-Content $RenderYaml -Raw
    
    # Update service name
    $Content = $Content -replace "name: ai-agents-v\d+", "name: ai-agents-v$Version"
    
    # Update EXPECTED_URL
    $Content = $Content -replace "EXPECTED_URL: https://ai-agents-v\d+\.onrender\.com", "EXPECTED_URL: https://ai-agents-v$Version.onrender.com"
    
    # Update VERSION_NUMBER
    $Content = $Content -replace "VERSION_NUMBER: `"\d+`"", "VERSION_NUMBER: `"$Version`""
    
    $Content | Set-Content $RenderYaml -NoNewline
    Write-Success "render.yaml updated"
}
else {
    Write-Warn "render.yaml not found - skipping"
}

# Step 7: Update GitHub Actions workflow
$WorkflowFile = "$ProjectRoot\.github\workflows\docker-build-deploy.yml"
if (Test-Path $WorkflowFile) {
    Write-Step "Updating GitHub Actions workflow..."
    $Content = Get-Content $WorkflowFile -Raw
    
    # Update branch filter if it exists
    if ($Content -match "branches:\s*\[\s*'?v\d+'?\s*\]") {
        $Content = $Content -replace "branches:\s*\[\s*'?v\d+'?\s*\]", "branches: ['$VersionBranch']"
        $Content | Set-Content $WorkflowFile -NoNewline
        Write-Success "GitHub Actions workflow updated"
    }
    else {
        Write-Warn "Could not find branch filter in workflow - may need manual update"
    }
}
else {
    Write-Warn "GitHub Actions workflow not found - skipping"
}

# Step 8: Commit changes
Write-Step "Committing changes..."
git add .
git commit -m "feat: Create $VersionBranch deployment with auto-detection

- Add version_info.json for version detection
- Update render.yaml for v$Version deployment
- Update GitHub Actions workflow
- Expected URL: https://ai-agents-v$Version.onrender.com

Created via automation script"

if ($LASTEXITCODE -ne 0) {
    Write-Fail "Failed to commit changes"
    exit 1
}
Write-Success "Changes committed"

# Step 9: Push to remote (if enabled)
if ($Push) {
    Write-Step "Pushing to remote..."
    git push origin $VersionBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to push to remote"
        exit 1
    }
    Write-Success "Pushed to remote: origin/$VersionBranch"
}
else {
    Write-Warn "Push skipped - push manually with: git push origin $VersionBranch"
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor $SuccessColor
Write-Host "🎉 Version $VersionBranch created successfully!" -ForegroundColor $SuccessColor
Write-Host ("=" * 60) -ForegroundColor $SuccessColor

Write-Host "`n📋 Next Steps:" -ForegroundColor $InfoColor
Write-Host "1. GitHub Actions will build Docker image: ghcr.io/gerardovsa/ai-agents-backend:$VersionBranch"
Write-Host "2. Create Render service:"
Write-Host "   - Service name: ai-agents-v$Version"
Write-Host "   - Image: ghcr.io/gerardovsa/ai-agents-backend:$VersionBranch"
Write-Host "   - Custom domain: https://ai-agents-v$Version.onrender.com"
Write-Host "3. No environment variables needed - auto-detection handles it!"
Write-Host "4. Test OAuth flow stays on v$Version URL"

Write-Host "`n🔗 Expected URLs:" -ForegroundColor $InfoColor
Write-Host "   Frontend: https://ai-agents-v$Version.onrender.com"
Write-Host "   API: https://ai-agents-v$Version.onrender.com/api"
Write-Host "   Health: https://ai-agents-v$Version.onrender.com/api/v1/system/check"

Write-Host ""
