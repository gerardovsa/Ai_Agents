# Start AI Agent with Supabase Connection
# This script sets environment variables and starts the Flask app

Write-Host "`n[SUPABASE] Starting AI Agent with Supabase Connection" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor DarkGray

# Set Supabase environment variables
$env:USE_SUPABASE = "true"
$env:RENDER = "true"  # Required by is_using_supabase() check
$env:SUPABASE_URL = "https://ryoicrdifiqhqpsnjmdo.supabase.co"
$env:SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ5b2ljcmRpZmlxaHFwc25qbWRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjY2NDI0NSwiZXhwIjoyMDc4MjQwMjQ1fQ.ebI6qfDzSt1skNm0hsBD-blyR7AJJUej5BcN-Bpp3PI"
$env:SUPABASE_DB_URL = "postgresql://postgres:inhouseprint@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres"

Write-Host "✅ Environment variables set:" -ForegroundColor Green
Write-Host "   USE_SUPABASE = $env:USE_SUPABASE" -ForegroundColor Gray
Write-Host "   RENDER = $env:RENDER" -ForegroundColor Gray
Write-Host "   SUPABASE_URL = $env:SUPABASE_URL" -ForegroundColor Gray
Write-Host "   SUPABASE_DB_URL = postgresql://postgres:***@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres" -ForegroundColor Gray
Write-Host ""

# Change to AI_infrastructure directory and start Flask
Write-Host "Starting Flask app..." -ForegroundColor Cyan
Set-Location -Path "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure"

# Run Flask app
python flask_app.py
