# Apply Automation Slug Migration to sessions.threads table
# Date: 2025-11-19

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTOMATION SLUG MIGRATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if migration file exists
$migrationFile = "migrations\add_automation_slug_to_threads.sql"
if (-not (Test-Path $migrationFile)) {
    Write-Host "ERROR: Migration file not found: $migrationFile" -ForegroundColor Red
    exit 1
}

Write-Host "Migration file found: $migrationFile" -ForegroundColor Green
Write-Host ""

# Load Supabase connection details from database-config.json
$configPath = "data\database-config.json"
if (Test-Path $configPath) {
    Write-Host "Loading database config from: $configPath" -ForegroundColor Yellow
    $config = Get-Content $configPath | ConvertFrom-Json
    
    $host_val = $config.databases.sessions.host
    $port_val = $config.databases.sessions.port
    $database_val = $config.databases.sessions.database
    $user_val = $config.databases.sessions.user
    
    Write-Host "  Host: $host_val" -ForegroundColor Gray
    Write-Host "  Port: $port_val" -ForegroundColor Gray
    Write-Host "  Database: $database_val" -ForegroundColor Gray
    Write-Host "  User: $user_val" -ForegroundColor Gray
    Write-Host ""
    
    # Get password from environment or config
    $password_val = $env:SUPABASE_PASSWORD
    if (-not $password_val) {
        $password_val = $config.databases.sessions.password
    }
    
    if (-not $password_val) {
        Write-Host "ERROR: No password found in environment (SUPABASE_PASSWORD) or config" -ForegroundColor Red
        exit 1
    }
    
    # Set environment variables for psql
    $env:PGHOST = $host_val
    $env:PGPORT = $port_val
    $env:PGDATABASE = $database_val
    $env:PGUSER = $user_val
    $env:PGPASSWORD = $password_val
    
    Write-Host "Applying migration to Supabase PostgreSQL..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check if psql is available
    $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
    if (-not $psqlPath) {
        Write-Host "ERROR: psql command not found. Please install PostgreSQL client tools." -ForegroundColor Red
        Write-Host ""
        Write-Host "Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
        Write-Host "Or install via Chocolatey: choco install postgresql" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Executing migration..." -ForegroundColor Cyan
    psql -f $migrationFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  MIGRATION SUCCESSFUL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Columns added to sessions.threads:" -ForegroundColor Green
        Write-Host "  - automation_slug (TEXT)" -ForegroundColor Gray
        Write-Host "  - automation_title (TEXT)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Restart Flask server: BISTART" -ForegroundColor Gray
        Write-Host "  2. Test automation canvas thread linking" -ForegroundColor Gray
        Write-Host "  3. Publish a workflow and verify pills appear" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "ERROR: Migration failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible causes:" -ForegroundColor Yellow
        Write-Host "  - Incorrect password" -ForegroundColor Gray
        Write-Host "  - Network connectivity issues" -ForegroundColor Gray
        Write-Host "  - Database permissions" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
    
} else {
    Write-Host "ERROR: Database config not found: $configPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Run migration manually with psql:" -ForegroundColor Yellow
    Write-Host "  psql -h <host> -U <user> -d <database> -f $migrationFile" -ForegroundColor Gray
    exit 1
}
