@echo off
setlocal
title SysCentre Git Push Pull Terminal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0scripts\Start-SysCentreGitTerminal.ps1"
endlocal
