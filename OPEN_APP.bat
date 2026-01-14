@echo off
REM ========================================
REM  Open AI Agents Platform (Correct Way)
REM ========================================

echo.
echo ========================================
echo   Starting AI Agents Platform
echo ========================================
echo.

REM Check if server is running
netstat -ano | findstr ":5001" | findstr "LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Server is running on port 5001
    echo.
    echo Opening browser at http://localhost:5001...
    echo.
    start http://localhost:5001
    echo.
    echo ========================================
    echo   Browser opened successfully!
    echo ========================================
    echo.
    echo TIP: Check DevTools Console for:
    echo   - LazyLoader initialized
    echo   - No CORS errors
    echo.
) else (
    echo [ERROR] Server is NOT running on port 5001
    echo.
    echo Please start the server first:
    echo   1. Open PowerShell
    echo   2. cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
    echo   3. Run: BISTART
    echo.
    pause
)
