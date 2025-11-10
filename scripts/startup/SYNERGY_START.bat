@echo off
REM Synergy Dashboard Backend Launcher
REM ===================================
REM Quick start script for Windows

echo ========================================
echo  SYNERGY DASHBOARD BACKEND SERVER
echo ========================================
echo.

REM Set Google service account credentials
set GOOGLE_APPLICATION_CREDENTIALS=%~dp0vsa-anythingllm-project-ab7c8caf8c47.json
echo [INFO] Google service account: %GOOGLE_APPLICATION_CREDENTIALS%
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r synergy_requirements.txt
    echo [SUCCESS] Dependencies installed
    echo.
)

REM Start the server
echo [INFO] Starting Synergy Dashboard Backend...
echo [INFO] Server will be available at http://localhost:5001
echo [INFO] WebSocket at ws://localhost:5001/ws/synergy
echo [INFO] Google Tasks/Calendar sync enabled
echo [INFO] Press Ctrl+C to stop
echo.

python synergy_backend.py

pause
