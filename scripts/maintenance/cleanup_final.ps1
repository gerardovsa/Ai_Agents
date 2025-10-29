$ErrorActionPreference = "Continue"
Write-Host "Moving remaining documentation files..." -ForegroundColor Green

$keepFiles = @("README.md", "CLEANUP_PHASE1_COMPLETE.md", "PHASE2_EXECUTION_PLAN.md")
$remainingDocs = Get-ChildItem -Path . -File -Filter "*.md" | Where-Object { $keepFiles -notcontains $_.Name }

Write-Host "Found $($remainingDocs.Count) files to archive"

foreach ($file in $remainingDocs) {
    if ($file.Name -match "^GOOGLE_|^GMAIL_|^SHEETS_") {
        Move-Item -Path $file.FullName -Destination "docs\archive\google_workspace\" -Force
    } elseif ($file.Name -match "_SUMMARY|_COMPLETE|_STATUS|_FIX|_UPDATE") {
        Move-Item -Path $file.FullName -Destination "docs\archive\summaries\" -Force
    } elseif ($file.Name -match "_IMPLEMENTATION|_INTEGRATION|SMTP_|WOOCOMMERCE_|TOOL_") {
        Move-Item -Path $file.FullName -Destination "docs\archive\implementations\" -Force
    } elseif ($file.Name -match "KANBAN|SESSION|UNIFIED_TASK|UNIVERSAL_KANBAN") {
        Move-Item -Path $file.FullName -Destination "docs\archive\kanban\" -Force
    } elseif ($file.Name -match "SAAS_|USER_PROFILE|PROFILE_") {
        Move-Item -Path $file.FullName -Destination "docs\archive\authentication\" -Force
    } else {
        Move-Item -Path $file.FullName -Destination "docs\archive\summaries\" -Force
    }
}

Write-Host "Cleanup complete! Remaining .md files: $((Get-ChildItem -Path . -File -Filter '*.md' | Measure-Object).Count)" -ForegroundColor Green
