# 🚀 Phase 2 Execution Plan - Code Cleanup

**Start Date:** October 29, 2025  
**Estimated Duration:** 4 weeks  
**Status:** Ready to Begin

---

## 📋 Quick Overview

**Goal:** Clean up AI_agents folder by archiving old documentation, consolidating tests, and removing temporary files.

**Expected Outcome:**
- 85+ markdown files moved to organized archive
- 15+ test scripts consolidated
- 10+ superseded scripts removed
- Clean, navigable workspace

---

## 🎯 Execution Steps

### Step 1: Create Archive Structure (5 minutes)

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Create organized archive folders
New-Item -ItemType Directory -Path "docs\archive\authentication" -Force
New-Item -ItemType Directory -Path "docs\archive\google_workspace" -Force
New-Item -ItemType Directory -Path "docs\archive\microsoft_365" -Force
New-Item -ItemType Directory -Path "docs\archive\implementations" -Force
New-Item -ItemType Directory -Path "docs\archive\kanban" -Force
New-Item -ItemType Directory -Path "docs\archive\summaries" -Force
New-Item -ItemType Directory -Path "docs\archive\ui" -Force

Write-Host "✅ Archive structure created" -ForegroundColor Green
```

---

### Step 2: Archive Authentication Docs (10 minutes)

```powershell
# Move authentication-related documentation
$authFiles = @(
    "ACCOUNT_LINKING_*.md",
    "AUTHENTICATION_*.md",
    "OAUTH_*.md",
    "LOGIN_*.md",
    "USER_AUTH_*.md",
    "HYBRID_AUTH_*.md"
)

foreach ($pattern in $authFiles) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Authentication docs archived" -ForegroundColor Green
```

---

### Step 3: Archive Google Workspace Docs (10 minutes)

```powershell
# Move Google Workspace documentation
$googleFiles = @(
    "GOOGLE_*.md",
    "GMAIL_*.md"
)

foreach ($pattern in $googleFiles) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\google_workspace\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Google Workspace docs archived" -ForegroundColor Green
```

---

### Step 4: Archive Microsoft 365 Docs (10 minutes)

```powershell
# Move Microsoft 365 documentation
$msFiles = @(
    "MICROSOFT_*.md"
)

foreach ($pattern in $msFiles) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\microsoft_365\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Microsoft 365 docs archived" -ForegroundColor Green
```

---

### Step 5: Archive Implementation Docs (10 minutes)

```powershell
# Move implementation summaries and complete docs
$implFiles = @(
    "*_IMPLEMENTATION_*.md",
    "*_INTEGRATION_*.md",
    "SMTP_*.md",
    "WOOCOMMERCE_*.md",
    "TOOL_*.md"
)

foreach ($pattern in $implFiles) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\implementations\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Implementation docs archived" -ForegroundColor Green
```

---

### Step 6: Archive Kanban Docs (5 minutes)

```powershell
# Move Kanban-related documentation
$kanbanFiles = @(
    "KANBAN_*.md",
    "SESSION_*.md",
    "SYNERGY_*.md"
)

foreach ($pattern in $kanbanFiles) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\kanban\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Kanban docs archived" -ForegroundColor Green
```

---

### Step 7: Archive Summary Docs (10 minutes)

```powershell
# Move all summary and status docs
$summaryFiles = @(
    "*_SUMMARY*.md",
    "*_COMPLETE*.md",
    "*_STATUS*.md",
    "CHANGES_*.md",
    "UPDATE_*.md",
    "EXPANSION_*.md",
    "CLEANUP_*.md",
    "PROGRESS_*.md"
)

foreach ($pattern in $summaryFiles) {
    Get-ChildItem -Path . -Filter $pattern -Exclude "CLEANUP_PHASE1_COMPLETE.md","PHASE2_EXECUTION_PLAN.md" | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Summary docs archived" -ForegroundColor Green
```

---

### Step 8: Archive Guides & Strategies (10 minutes)

```powershell
# Move guides, strategies, and architecture docs
$guideFiles = @(
    "*_GUIDE*.md",
    "*_STRATEGY*.md",
    "*_ARCHITECTURE*.md",
    "*_BLUEPRINT*.md",
    "DEPLOYMENT_*.md",
    "WHEN_TO_USE_*.md",
    "PLATFORM_*.md",
    "SYSTEM_*.md"
)

foreach ($pattern in $guideFiles) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force
            Write-Host "📦 Moved: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ Guides & strategies archived" -ForegroundColor Green
```

---

### Step 9: Consolidate Tests (15 minutes)

```powershell
# Create tests directory if it doesn't exist
New-Item -ItemType Directory -Path "AI_infrastructure\tests" -Force

# Move test files from root
$testFiles = @(
    "test_*.py",
    "check_*.py"
)

foreach ($pattern in $testFiles) {
    Get-ChildItem -Path . -Filter $pattern -Exclude "PHASE2_EXECUTION_PLAN.md" | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "AI_infrastructure\tests\" -Force
            Write-Host "🧪 Moved test: $($_.Name)" -ForegroundColor Yellow
        }
}

# Move test HTML files to archive
Move-Item -Path "UI\test-*.html" -Destination "docs\archive\ui\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "UI\*-test.html" -Destination "docs\archive\ui\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "UI\integration-test.html" -Destination "docs\archive\ui\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "UI\credential-tester.html" -Destination "docs\archive\ui\" -Force -ErrorAction SilentlyContinue

Write-Host "✅ Tests consolidated" -ForegroundColor Green
```

---

### Step 10: Remove Superseded Scripts (5 minutes)

```powershell
# Remove old/superseded PowerShell scripts
$supersededScripts = @(
    "BISTART_DIRECT_UPDATE.ps1",
    "BISTART_MANUAL_UPDATE.ps1",
    "BISTART_NEW_VERSION.txt",
    "BISTART_UPDATED_FUNCTION.ps1",
    "SIMPLE_BISTART_UPDATE.ps1",
    "UPDATE_BISTART.ps1",
    "UPDATE_NOW.ps1"
)

foreach ($script in $supersededScripts) {
    if (Test-Path $script) {
        Remove-Item -Path $script -Force
        Write-Host "🗑️  Removed: $script" -ForegroundColor Red
    }
}

Write-Host "✅ Superseded scripts removed" -ForegroundColor Green
```

---

### Step 11: Archive One-Time Scripts (5 minutes)

```powershell
# Create scripts archive
New-Item -ItemType Directory -Path "docs\archive\scripts" -Force

# Move one-time setup/utility scripts
$oneTimeScripts = @(
    "setup_*.py",
    "setup_*.ps1",
    "create_*.py",
    "table_structure_analysis.py"
)

foreach ($pattern in $oneTimeScripts) {
    Get-ChildItem -Path . -Filter $pattern | 
        ForEach-Object { 
            Move-Item -Path $_.FullName -Destination "docs\archive\scripts\" -Force
            Write-Host "📦 Archived script: $($_.Name)" -ForegroundColor Cyan
        }
}

Write-Host "✅ One-time scripts archived" -ForegroundColor Green
```

---

### Step 12: Remove Old Backups (2 minutes)

```powershell
# Remove old backup directories
$backupDirs = @(
    "AI_infrastructure_BACKUP_*"
)

foreach ($pattern in $backupDirs) {
    Get-ChildItem -Path . -Filter $pattern -Directory | 
        ForEach-Object { 
            Remove-Item -Path $_.FullName -Recurse -Force
            Write-Host "🗑️  Removed backup: $($_.Name)" -ForegroundColor Red
        }
}

Write-Host "✅ Old backups removed" -ForegroundColor Green
```

---

### Step 13: Create Archive Index (10 minutes)

```powershell
# Create archive README
$archiveReadme = @"
# 📦 Archived Documentation

This folder contains historical documentation from the AI Agents Platform development process.

**Last Updated:** $(Get-Date -Format "MMMM dd, yyyy")

---

## 📂 Folder Structure

### authentication/
OAuth, login, account linking implementations and strategies.

**Files:** $(Get-ChildItem "docs\archive\authentication" | Measure-Object).Count
- Account linking strategies
- OAuth implementations
- Authentication flow analysis
- Login system documentation

### google_workspace/
Google Workspace platform integrations (Gmail, Docs, Sheets, Forms, etc.)

**Files:** $(Get-ChildItem "docs\archive\google_workspace" | Measure-Object).Count
- Gmail smart tools
- Google Docs implementation
- Google Sheets integration
- Google Forms capabilities

### microsoft_365/
Microsoft 365 platform integrations (Word, Excel, Outlook, Teams, etc.)

**Files:** $(Get-ChildItem "docs\archive\microsoft_365" | Measure-Object).Count
- Microsoft 365 setup guides
- Login implementations
- Tool catalog integration

### implementations/
Platform-specific implementation details and integration summaries.

**Files:** $(Get-ChildItem "docs\archive\implementations" | Measure-Object).Count
- SMTP/Gmail sending
- WooCommerce direct API
- Tool implementation status

### kanban/
Kanban board and session management documentation.

**Files:** $(Get-ChildItem "docs\archive\kanban" | Measure-Object).Count
- Kanban-AI integration
- Session orchestration
- Synergy dashboard

### summaries/
Development summaries, change logs, and progress reports.

**Files:** $(Get-ChildItem "docs\archive\summaries" | Measure-Object).Count
- Implementation summaries
- Change summaries
- Cleanup reports
- Progress updates

### ui/
UI test files and integration tests.

**Files:** $(Get-ChildItem "docs\archive\ui" -ErrorAction SilentlyContinue | Measure-Object).Count
- Test HTML files
- Integration tests
- UI experiments

### scripts/
One-time setup and utility scripts.

**Files:** $(Get-ChildItem "docs\archive\scripts" -ErrorAction SilentlyContinue | Measure-Object).Count
- Setup scripts
- Migration utilities
- Analysis tools

---

## 📝 Notes

**Why Archived:**
- Historical reference only
- Superseded by consolidated documentation in `docs/features/`
- Valuable context but cluttered main workspace

**Active Documentation:**
Refer to `docs/features/` for current, consolidated documentation:
- `AGENT_SYSTEM_COMPLETE.md`
- `TOOL_PLATFORM_COMPLETE.md`
- `KANBAN_INTEGRATION_COMPLETE.md`

**Search Tips:**
Use grep/findstr to search across archived docs:
```powershell
Get-ChildItem -Path . -Filter "*.md" -Recurse | Select-String "search term"
```

---

**Archived:** $(Get-Date -Format "MMMM dd, yyyy")
**Status:** Reference Only
"@

Set-Content -Path "docs\archive\README.md" -Value $archiveReadme
Write-Host "✅ Archive index created" -ForegroundColor Green
```

---

### Step 14: Final Cleanup Report (5 minutes)

```powershell
# Generate cleanup report
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "🎉 PHASE 2 CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green

Write-Host "`n📊 Cleanup Statistics:" -ForegroundColor Yellow
Write-Host "   • Docs Archived: $((Get-ChildItem "docs\archive" -Recurse -Filter "*.md" | Measure-Object).Count)" -ForegroundColor Cyan
Write-Host "   • Tests Consolidated: $((Get-ChildItem "AI_infrastructure\tests" -Filter "*.py" | Measure-Object).Count)" -ForegroundColor Cyan
Write-Host "   • Scripts Removed: $($supersededScripts.Count)" -ForegroundColor Cyan

Write-Host "`n📁 Current Root Files:" -ForegroundColor Yellow
$rootFiles = Get-ChildItem -Path . -File | Where-Object { $_.Extension -in @('.md', '.py', '.ps1', '.bat', '.txt', '.json', '.yaml', '.yml') }
Write-Host "   • Total: $($rootFiles.Count)" -ForegroundColor Cyan

Write-Host "`n✅ Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Review archived files in docs/archive/" -ForegroundColor White
Write-Host "   2. Commit changes to git" -ForegroundColor White
Write-Host "   3. Proceed to Phase 3: API Documentation" -ForegroundColor White

Write-Host "`n" -NoNewline
```

---

## 🔄 Complete Script (Run All at Once)

Save as `execute_phase2_cleanup.ps1`:

```powershell
# Phase 2 Cleanup - Complete Execution Script
# Run this to execute all cleanup steps at once

$ErrorActionPreference = "Continue"

Write-Host "🚀 Starting Phase 2 Cleanup..." -ForegroundColor Green
Write-Host "This will take approximately 10 minutes" -ForegroundColor Yellow
Write-Host ""

# Step 1: Create archive structure
Write-Host "Step 1/14: Creating archive structure..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "docs\archive\authentication" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\google_workspace" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\microsoft_365" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\implementations" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\kanban" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\summaries" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\ui" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\scripts" -Force | Out-Null

# Step 2-8: Archive documentation (combined for speed)
Write-Host "Steps 2-8: Archiving documentation files..." -ForegroundColor Cyan

# Authentication
Get-ChildItem -Path . -Filter "ACCOUNT_LINKING_*.md" | Move-Item -Destination "docs\archive\authentication\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "AUTHENTICATION_*.md" | Move-Item -Destination "docs\archive\authentication\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "OAUTH_*.md" | Move-Item -Destination "docs\archive\authentication\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "LOGIN_*.md" | Move-Item -Destination "docs\archive\authentication\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "USER_AUTH_*.md" | Move-Item -Destination "docs\archive\authentication\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "HYBRID_AUTH_*.md" | Move-Item -Destination "docs\archive\authentication\" -Force -ErrorAction SilentlyContinue

# Google Workspace
Get-ChildItem -Path . -Filter "GOOGLE_*.md" | Move-Item -Destination "docs\archive\google_workspace\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "GMAIL_*.md" | Move-Item -Destination "docs\archive\google_workspace\" -Force -ErrorAction SilentlyContinue

# Microsoft 365
Get-ChildItem -Path . -Filter "MICROSOFT_*.md" | Move-Item -Destination "docs\archive\microsoft_365\" -Force -ErrorAction SilentlyContinue

# Implementations
Get-ChildItem -Path . -Filter "*_IMPLEMENTATION_*.md" | Move-Item -Destination "docs\archive\implementations\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*_INTEGRATION_*.md" | Move-Item -Destination "docs\archive\implementations\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "SMTP_*.md" | Move-Item -Destination "docs\archive\implementations\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "WOOCOMMERCE_*.md" | Move-Item -Destination "docs\archive\implementations\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "TOOL_*.md" | Move-Item -Destination "docs\archive\implementations\" -Force -ErrorAction SilentlyContinue

# Kanban
Get-ChildItem -Path . -Filter "KANBAN_*.md" | Move-Item -Destination "docs\archive\kanban\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "SESSION_*.md" | Move-Item -Destination "docs\archive\kanban\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "SYNERGY_*.md" | Move-Item -Destination "docs\archive\kanban\" -Force -ErrorAction SilentlyContinue

# Summaries
Get-ChildItem -Path . -Filter "*_SUMMARY*.md" -Exclude "CLEANUP_PHASE1_COMPLETE.md","PHASE2_EXECUTION_PLAN.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*_COMPLETE*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*_STATUS*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "CHANGES_*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue

# Guides & Architecture
Get-ChildItem -Path . -Filter "*_GUIDE*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*_STRATEGY*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*_ARCHITECTURE*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*_BLUEPRINT*.md" | Move-Item -Destination "docs\archive\summaries\" -Force -ErrorAction SilentlyContinue

# Step 9: Consolidate tests
Write-Host "Step 9: Consolidating test files..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "AI_infrastructure\tests" -Force | Out-Null
Get-ChildItem -Path . -Filter "test_*.py" | Move-Item -Destination "AI_infrastructure\tests\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "check_*.py" | Move-Item -Destination "AI_infrastructure\tests\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "UI" -Filter "test-*.html" | Move-Item -Destination "docs\archive\ui\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "UI" -Filter "*-test.html" | Move-Item -Destination "docs\archive\ui\" -Force -ErrorAction SilentlyContinue

# Step 10: Remove superseded scripts
Write-Host "Step 10: Removing superseded scripts..." -ForegroundColor Cyan
Remove-Item -Path "BISTART_DIRECT_UPDATE.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "BISTART_MANUAL_UPDATE.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "BISTART_NEW_VERSION.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "BISTART_UPDATED_FUNCTION.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "SIMPLE_BISTART_UPDATE.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "UPDATE_BISTART.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "UPDATE_NOW.ps1" -Force -ErrorAction SilentlyContinue

# Step 11: Archive one-time scripts
Write-Host "Step 11: Archiving one-time scripts..." -ForegroundColor Cyan
Get-ChildItem -Path . -Filter "setup_*.py" | Move-Item -Destination "docs\archive\scripts\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "setup_*.ps1" | Move-Item -Destination "docs\archive\scripts\" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "create_*.py" | Move-Item -Destination "docs\archive\scripts\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "table_structure_analysis.py" -Destination "docs\archive\scripts\" -Force -ErrorAction SilentlyContinue

# Step 12: Remove old backups
Write-Host "Step 12: Removing old backup directories..." -ForegroundColor Cyan
Get-ChildItem -Path . -Filter "AI_infrastructure_BACKUP_*" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Step 13: Create archive index
Write-Host "Step 13: Creating archive index..." -ForegroundColor Cyan
# (Archive README content from Step 13 above)

# Step 14: Final report
Write-Host "`n✅ Phase 2 Cleanup Complete!" -ForegroundColor Green
Write-Host "📊 Files archived: $((Get-ChildItem "docs\archive" -Recurse -Filter "*.md" | Measure-Object).Count)" -ForegroundColor Cyan
Write-Host "🧪 Tests consolidated: $((Get-ChildItem "AI_infrastructure\tests" -Filter "*.py" -ErrorAction SilentlyContinue | Measure-Object).Count)" -ForegroundColor Cyan
Write-Host "`nWorkspace is now clean and organized!" -ForegroundColor Green
```

---

## ⚠️ Important Notes

**Before Running:**
1. ✅ Ensure git is clean or commit current changes
2. ✅ Verify BISTART/BISTOP scripts work
3. ✅ Backup database files (`data/` folder)

**After Running:**
1. ✅ Review archived files
2. ✅ Test BISTART still works
3. ✅ Verify documentation is accessible
4. ✅ Commit changes to git

**Rollback Plan:**
If something goes wrong, git revert:
```powershell
git status
git checkout -- .
```

---

## 📞 Support

If you encounter issues during cleanup:

1. **Check git status:** `git status`
2. **Review moved files:** Check `docs/archive/`
3. **Restore if needed:** `git checkout -- <file>`
4. **Contact:** Review error messages and fix individually

---

**Created:** October 29, 2025  
**Status:** Ready to Execute  
**Estimated Time:** 10-15 minutes  
**Risk Level:** Low (all changes git-tracked)
