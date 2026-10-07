@echo off
chcp 65001 >nul
echo.
echo   me-archive  -  now sealing today
echo   ---------------------------------
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-daily.ps1"
echo.
echo   done.  log: logs\
pause
