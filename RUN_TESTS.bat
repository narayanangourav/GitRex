@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
set "PYTHONPATH=%cd%\src"
%PY% -m unittest discover -s tests -v
pause
