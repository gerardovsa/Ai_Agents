@echo off
REM Work Timeline Tool - Quick Start Script
REM Run this to generate your timeline dashboard

echo.
echo ===============================================
echo    Work Timeline Tool - Quick Start
echo ===============================================
echo.

REM Check if config.py exists
if not exist "config.py" (
    echo [ERROR] config.py not found!
    echo.
    echo Please create config.py from config_template.py:
    echo   1. Copy config_template.py to config.py
    echo   2. Edit config.py with your project paths
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [1/3] Found config.py - checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.x
    pause
    exit /b 1
)

echo [2/3] Generating timeline...
python create_focused_timeline.py

if errorlevel 1 (
    echo [ERROR] Timeline generation failed!
    pause
    exit /b 1
)

echo [3/3] Opening dashboard...
start focused_timeline_detailed.html

echo.
echo ===============================================
echo    SUCCESS! Timeline dashboard generated
echo ===============================================
echo.
echo The dashboard has been opened in your browser.
echo.
echo Files created:
echo   - focused_timeline_detailed.html
echo.
echo To regenerate with new data, run this script again.
echo.
pause
