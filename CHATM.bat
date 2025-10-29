@echo off
REM CHATM - Chat with Microsoft 365 Account
REM Quick shortcut for: CHAT "<message>" -User "Gerardo@minivetguide.onmicrosoft.com"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CHATM.ps1" %*
