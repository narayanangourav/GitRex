@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 --version >nul 2>&1
  if not errorlevel 1 set "PY=py -3"
)
%PY% --version >nul 2>&1
if errorlevel 1 (
 echo Python 3.10 or newer is required to run tests.
 pause & exit /b 1
)
set "PYTHONPATH=%cd%\src"
%PY% -m unittest discover -s tests -v
pause
