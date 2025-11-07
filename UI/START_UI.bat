@echo off
REM ============================================================================
REM Business AI Platform UI Server Launcher
REM Starts HTTP server on port 8080 to avoid CORS issues
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                    Starting Business AI Platform UI                        ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found!
    echo    Please install Python 3.x and add to PATH
    pause
    exit /b 1
)

REM Start the UI server
echo 🚀 Starting UI server on http://localhost:8080...
echo.

python serve_ui.py

pause
