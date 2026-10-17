@echo off
setlocal
set "SCRIPT=%~dp0scripts\Start-SysCentreWebBuildTerminal.ps1"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -RepositoryPath "%~dp0"
if errorlevel 1 (
  echo.
  echo The SysCentre Web Build Terminal exited with an error.
  pause
)
endlocal
