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

echo [1/3] Starting Flask Backend...
echo       Location: %FLASK_DIR%
echo       Port: 5001
echo.

REM Start Flask in new terminal window
start "Flask Backend (Port 5001)" cmd /k "cd /d %FLASK_DIR% && python flask_app.py"

REM Wait 3 seconds for Flask to initialize
timeout /t 3 /nobreak >nul

echo [2/3] Starting UI Server...
echo       Location: %UI_DIR%
echo       Port: 8080
echo.

REM Start UI server in new terminal window
start "UI Server (Port 8080)" cmd /k "cd /d %UI_DIR% && python -m http.server 8080"

REM Wait 2 seconds for UI server to start
timeout /t 2 /nobreak >nul

echo [3/3] Opening Platform in Browser...
echo.

REM Open browser to platform
start http://localhost:8080/business-ai-platform-v2.html

echo.
echo ============================================================
echo    PLATFORM LAUNCHED SUCCESSFULLY!
echo ============================================================
echo.
echo     Flask Backend:  http://localhost:5001
echo     UI Platform:    http://localhost:8080/business-ai-platform-v2.html
echo.
echo     2 terminal windows opened:
echo     1. Flask Backend (Port 5001)
echo     2. UI Server (Port 8080)
echo.
echo     Press Ctrl+C in each terminal to stop servers
echo.
echo ============================================================

REM Return to original directory
cd /d %ORIGINAL_DIR%

pause
