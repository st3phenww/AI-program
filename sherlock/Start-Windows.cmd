@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 setup.py
  if errorlevel 1 goto finish
)
".venv\Scripts\python.exe" run.py %*
:finish
pause
