# MustCare ValorAISynergySuite V3 - Render.com Deployment Script
# PowerShell version for Windows users

param(
    [switch]$SkipValidation,
    [switch]$AutoCommit,
    [string]$ServiceUrl
)

$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "MustCare ValorAI V3 - Render.com Deployment"
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host ""

# Get project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RenderDir = Join-Path $ProjectRoot "render"

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Cyan
    Write-Host ""
    
    $checks = @()
    
    # Check 1: Git repository
    if (Test-Path (Join-Path $ProjectRoot ".git")) {
        $checks += @{Name="Git repository"; Passed=$true; Details=""}
    } else {
        $checks += @{Name="Git repository"; Passed=$false; Details="Not a git repository"}
    }
    
    # Check 2: render.yaml
    if (Test-Path (Join-Path $ProjectRoot "render.yaml")) {
        $checks += @{Name="render.yaml"; Passed=$true; Details=""}
    } else {
        $checks += @{Name="render.yaml"; Passed=$false; Details="Missing blueprint"}
    }
    
    # Check 3: Dockerfile.render
    if (Test-Path (Join-Path $RenderDir "Dockerfile.render")) {
        $checks += @{Name="Dockerfile.render"; Passed=$true; Details=""}
    } else {
        $checks += @{Name="Dockerfile.render"; Passed=$false; Details="Missing Dockerfile"}
    }
    
    # Check 4: start.sh
    if (Test-Path (Join-Path $RenderDir "start.sh")) {
        $checks += @{Name="start.sh"; Passed=$true; Details=""}
    } else {
        $checks += @{Name="start.sh"; Passed=$false; Details="Missing startup script"}
    }
    
    # Check 5: Anthropic API key
    $anthropicKey = $env:ANTHROPIC_API_KEY
    if ($anthropicKey -and $anthropicKey.StartsWith("sk-ant-")) {
        $checks += @{Name="Anthropic API Key"; Passed=$true; Details=""}
    } else {
        $checks += @{Name="Anthropic API Key"; Passed=$false; Details="Not set or invalid"}
    }
    
    # Check 6: Node.js
    try {
        $nodeVersion = node --version
        if ($nodeVersion.StartsWith("v20.")) {
            $checks += @{Name="Node.js 20.x"; Passed=$true; Details=$nodeVersion}
        } else {
            $checks += @{Name="Node.js 20.x"; Passed=$false; Details="Found $nodeVersion"}
        }
    } catch {
        $checks += @{Name="Node.js 20.x"; Passed=$false; Details="Not found"}
    }
    
    # Print results
    foreach ($check in $checks) {
        $icon = if ($check.Passed) { "✅" } else { "❌" }
        $status = if ($check.Passed) { "PASS" } else { "FAIL" }
        $name = $check.Name.PadRight(25)
        Write-Host "$icon $name [$status]  $($check.Details)"
    }
    
    Write-Host ""
    
    $allPassed = ($checks | Where-Object { -not $_.Passed -and $_.Name -ne "Anthropic API Key" }).Count -eq 0
    return $allPassed
}

# Function to get git status
function Get-GitStatus {
    try {
        Push-Location $ProjectRoot
        
        $branch = git branch --show-current 2>$null
        $hasChanges = (git status --porcelain 2>$null).Length -gt 0
        $remote = git remote get-url origin 2>$null
        
        Pop-Location
        
        return @{
            Branch = $branch
            HasChanges = $hasChanges
            Remote = $remote
        }
    } catch {
        Pop-Location
        return @{
            Branch = "unknown"
            HasChanges = $true
            Remote = "unknown"
        }
    }
}

# Function to commit and push
function Push-ToGitHub {
    Write-Host ""
    Write-Host "=" -NoNewline; Write-Host ("=" * 59)
    Write-Host "Git Status Check"
    Write-Host "=" -NoNewline; Write-Host ("=" * 59)
    Write-Host ""
    
    $gitStatus = Get-GitStatus
    
    Write-Host "Current branch: $($gitStatus.Branch)"
    Write-Host "Remote: $($gitStatus.Remote)"
    Write-Host "Uncommitted changes: $(if ($gitStatus.HasChanges) {'Yes'} else {'No'})"
    Write-Host ""
    
    if ($gitStatus.HasChanges) {
        if ($AutoCommit) {
            $response = "y"
        } else {
            $response = Read-Host "Commit render deployment files? (y/n)"
        }
        
        if ($response -eq "y") {
            try {
                Push-Location $ProjectRoot
                
                git add render/ render.yaml
                git commit -m "feat: Add Render.com V8 deployment configuration"
                
                Write-Host "✅ Changes committed" -ForegroundColor Green
                
                if ($AutoCommit) {
                    $pushResponse = "y"
                } else {
                    $pushResponse = Read-Host "Push to $($gitStatus.Branch)? (y/n)"
                }
                
                if ($pushResponse -eq "y") {
                    git push origin $gitStatus.Branch
                    Write-Host "✅ Changes pushed to GitHub" -ForegroundColor Green
                }
                
                Pop-Location
                return $true
            } catch {
                Pop-Location
                Write-Host "❌ Git operation failed: $_" -ForegroundColor Red
                return $false
            }
        }
    } else {
        Write-Host "✅ No uncommitted changes" -ForegroundColor Green
        return $true
    }
}

# Function to show deployment instructions
function Show-DeploymentInstructions {
    Write-Host ""
    Write-Host "=" -NoNewline; Write-Host ("=" * 59)
    Write-Host "Deploy via Render Dashboard"
    Write-Host "=" -NoNewline; Write-Host ("=" * 59)
    Write-Host ""
    
    Write-Host "Follow these steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Go to: " -NoNewline
    Write-Host "https://dashboard.render.com" -ForegroundColor Cyan
    Write-Host "2. Click 'New +' (top right)"
    Write-Host "3. Select 'Blueprint'"
    Write-Host "4. Connect repository: MustCare_ValorAISynergySuite"
    Write-Host "5. Select branch: V8-Render"
    Write-Host "6. Blueprint file: render.yaml (auto-detected)"
    Write-Host "7. Click 'Apply'"
    Write-Host ""
    Write-Host "After deployment:" -ForegroundColor Yellow
    Write-Host "8. Go to: Services → mustcare-valorai-v3 → Environment"
    Write-Host "9. Add ANTHROPIC_API_KEY: sk-ant-your-key-here"
    Write-Host "10. Click 'Save Changes'"
    Write-Host "11. Wait for deployment (~10 minutes)"
    Write-Host ""
    Write-Host "Your service will be available at:" -ForegroundColor Green
    Write-Host "https://mustcare-valorai-v3.onrender.com" -ForegroundColor Cyan
    Write-Host ""
}

# Function to validate deployment
function Test-Deployment {
    param([string]$Url)
    
    if (-not $Url) {
        $Url = Read-Host "Enter your Render service URL"
    }
    
    Write-Host ""
    Write-Host "Validating deployment: $Url" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $healthUrl = "$Url/api/v1/system/check"
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 10
        
        Write-Host "✅ Health check passed" -ForegroundColor Green
        Write-Host "   Status: $($response.status)"
        Write-Host "   Version: $($response.version)"
        Write-Host "   Node: $($response.node)"
        Write-Host "   Uptime: $($response.uptime)s"
        Write-Host ""
        
        return $true
    } catch {
        Write-Host "❌ Health check failed: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible reasons:" -ForegroundColor Yellow
        Write-Host "- Service is still deploying (wait 5-10 minutes)"
        Write-Host "- Environment variables not configured"
        Write-Host "- Build failed (check Render logs)"
        Write-Host ""
        
        return $false
    }
}

# Main execution
try {
    # Step 1: Validate prerequisites
    if (-not $SkipValidation) {
        $allPassed = Test-Prerequisites
        
        if (-not $allPassed) {
            Write-Host "❌ Prerequisites check failed" -ForegroundColor Red
            Write-Host "Please fix the issues above before deploying"
            exit 1
        }
        
        Write-Host "✅ All prerequisites passed" -ForegroundColor Green
    }
    
    # Step 2: Commit and push
    $pushed = Push-ToGitHub
    
    # Step 3: Show deployment instructions
    Show-DeploymentInstructions
    
    # Step 4: Offer validation
    if ($ServiceUrl) {
        Test-Deployment -Url $ServiceUrl
    } else {
        Write-Host "To validate deployment after it's live, run:" -ForegroundColor Yellow
        Write-Host "  .\render\deploy.ps1 -ServiceUrl https://mustcare-valorai-v3.onrender.com"
        Write-Host ""
        Write-Host "Or use the Python validator:" -ForegroundColor Yellow
        Write-Host "  python render\validate_deployment.py https://mustcare-valorai-v3.onrender.com"
    }
    
    Write-Host ""
    Write-Host "=" -NoNewline; Write-Host ("=" * 59)
    Write-Host "Next Steps"
    Write-Host "=" -NoNewline; Write-Host ("=" * 59)
    Write-Host ""
    Write-Host "1. Monitor deployment in Render Dashboard"
    Write-Host "2. Wait for build to complete (~10 minutes)"
    Write-Host "3. Test health endpoint: /api/v1/system/check"
    Write-Host "4. Create admin account"
    Write-Host "5. Test Claude 4 features"
    Write-Host ""
    Write-Host "For detailed instructions, see:" -ForegroundColor Cyan
    Write-Host "  render\RENDER_DEPLOYMENT_GUIDE.md"
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Deployment script failed: $_" -ForegroundColor Red
    exit 1
}
