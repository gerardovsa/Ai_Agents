@echo off
REM ==================== BUSINESS AI PLATFORM LAUNCHER ====================
REM Launch Flask backend + UI from any directory
REM Usage: Just run BISTART.bat or type "BISTART" in terminal

echo.
echo ============================================================
echo    BUSINESS AI PLATFORM LAUNCHER
echo ============================================================
echo.

REM Store current directory
set ORIGINAL_DIR=%CD%

REM Set paths
set FLASK_DIR=C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
set UI_DIR=C:\Users\gpoli\GIT\AI_agents\UI

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

echo [0/2] Checking for existing Flask servers on port 5001...

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

echo [1/2] Starting Flask Backend...
echo       Location: %FLASK_DIR%
echo       Port: 5001
echo.

REM Start Flask in new terminal window with UTF-8 encoding
start "Flask Backend (Port 5001)" cmd /k "cd /d %FLASK_DIR% && set PYTHONIOENCODING=utf-8 && python flask_app.py"

REM Wait 3 seconds for Flask to initialize
timeout /t 3 /nobreak >nul

echo [2/2] Opening Platform in Browser...
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
