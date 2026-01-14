@echo off
REM Quick Start Script for New Flask App
REM Location: C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure

echo ================================================================================
echo 🚀 NEW FLASK APP - QUICK START
echo ================================================================================
echo.

REM Check Python
echo ✓ Checking Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo  Python not found! Please install Python 3.x
    pause
    exit /b 1
)

echo.
echo ✓ Installing dependencies...
pip install -r requirements.txt --quiet

if %ERRORLEVEL% NEQ 0 (
    echo  Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo  DEPENDENCIES INSTALLED
echo ================================================================================
echo.
echo Installed packages:
echo   - Flask (web framework)
echo   - anthropic (Claude API)
echo   - openai (GPT API)
echo   - requests (DeepSeek API)
echo   - Flask-CORS, Flask-SocketIO
echo.
echo ================================================================================
echo 🚀 STARTING NEW FLASK APP
echo ================================================================================
echo.
echo 📡 Port: 5001 (testing - old app on 5000)
echo 🌐 URL: http://localhost:5001
echo 🏥 Health: http://localhost:5001/health
echo.
echo Press Ctrl+C to stop
echo ================================================================================
echo.

REM Run Flask app
python flask_app.py

pause
