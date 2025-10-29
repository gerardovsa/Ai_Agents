@echo off
REM CHAT Command - Talk to AI Agent from anywhere
REM Redirects to chat.ps1 in the AI_agents directory

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0chat.ps1" %*
