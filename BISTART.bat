@echo off
REM ==================== BUSINESS AI PLATFORM LAUNCHER ====================
REM Launch Flask backend + UI from any directory
REM Usage: Just run BISTART.bat or type "BISTART" in terminal

echo.
echo ============================================================
echo    BUSINESS AI PLATFORM LAUNCHER
echo    [SUPABASE MODE - PostgreSQL Database]
echo ============================================================
echo.

REM Store current directory
set ORIGINAL_DIR=%CD%

REM Set paths (FIXED Jan 27, 2026: Use V11 folder)
set FLASK_DIR=C:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\AI_infrastructure
set UI_DIR=C:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI

REM Check if Flask app exists
if not exist "%FLASK_DIR%\flask_app.py" (
    echo [ERROR] Flask app not found at: %FLASK_DIR%\flask_app.py
    pause
    exit /b 1
)

REM Check if UI exists
if not exist "%UI_DIR%\business-ai-platform-v2.html" (
    echo [ERROR] UI not found at: %UI_DIR%\business-ai-platform-v2.html
    pause
    exit /b 1
)

echo [0/4] Cleaning up zombie Python processes...

REM Kill ALL Python processes first
setlocal enabledelayedexpansion
set PYTHON_KILLED=0

for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /NH 2^>nul') do (
    set PID=%%a
    echo       Stopping Python PID !PID!...
    taskkill /F /PID !PID! >nul 2>&1
    set PYTHON_KILLED=1
)

if !PYTHON_KILLED! equ 1 (
    timeout /t 2 /nobreak >nul
    echo       [OK] All Python processes stopped
) else (
    echo       [OK] No Python processes to clean
)
endlocal
echo.

echo [1/4] Checking for existing Flask servers on port 5001...

REM Kill processes using port 5001 (Flask backend only)
REM Use more reliable netstat parsing
setlocal enabledelayedexpansion
set FOUND_PROCESS=0

for /f "tokens=5" %%a in ('netstat -aon ^| findstr /R "[:]5001.*LISTENING"') do (
    set PID=%%a
    REM Remove any non-numeric characters
    set PID=!PID: =!
    
    REM Check if PID is numeric
    echo !PID! | findstr /R "^[0-9][0-9]*$" >nul
    if !errorlevel! equ 0 (
        echo       Stopping PID !PID! on port 5001...
        taskkill /F /PID !PID! >nul 2>&1
        set FOUND_PROCESS=1
    )
)

if !FOUND_PROCESS! equ 1 (
    timeout /t 2 /nobreak >nul
    echo       [OK] Port 5001 cleared
) else (
    echo       [OK] Port 5001 is available
)
endlocal
echo.

echo [2/4] Starting Flask Backend with Supabase...
echo       Location: %FLASK_DIR%
echo       Port: 5001
echo       Database: Supabase PostgreSQL
echo.

REM Start Flask in new terminal window with UTF-8 encoding and Supabase environment variables
start "Flask Backend - Supabase Mode" cmd /k "cd /d %FLASK_DIR% && set PYTHONIOENCODING=utf-8 && set USE_SUPABASE=true && set RENDER=true && set SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co && set SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ5b2ljcmRpZmlxaHFwc25qbWRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjY2NDI0NSwiZXhwIjoyMDc4MjQwMjQ1fQ.ebI6qfDzSt1skNm0hsBD-blyR7AJJUej5BcN-Bpp3PI && set SUPABASE_DB_URL=postgresql://postgres:inhouseprint@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres && echo. && echo [SUPABASE MODE] Connected to PostgreSQL Database && echo. && python flask_app.py"

REM Wait 3 seconds for Flask to initialize
timeout /t 3 /nobreak >nul

echo [3/4] Opening Platform in Browser...
echo.

REM Open browser to platform (direct file access)
start "" "%UI_DIR%\business-ai-platform-v2.html"

echo.
echo ============================================================
echo    PLATFORM LAUNCHED SUCCESSFULLY!
echo ============================================================
echo.
echo     Flask Backend:  http://localhost:5001
echo     UI Platform:    Opened in default browser
echo.
echo     Note: UI opened directly from file system
echo           Connected to Flask backend on port 5001
echo     1 terminal window opened:
echo     - Flask Backend (Port 5001)
echo.
echo     Press Ctrl+C in each terminal to stop servers
echo.
echo ============================================================

REM Return to original directory
cd /d %ORIGINAL_DIR%

pause
