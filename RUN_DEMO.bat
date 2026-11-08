@echo off
setlocal
cd /d "%~dp0"
echo =========================================
echo   GitRex - Offline Demo / GIF Generator
 echo =========================================
set "PY=python"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 --version >nul 2>&1
  if not errorlevel 1 set "PY=py -3"
)
%PY% --version >nul 2>&1
if errorlevel 1 (
 echo Python 3.10 or newer is required for generating GIFs.
 echo You can still open OPEN_PREVIEW.html now without installing anything.
 pause & exit /b 1
)
if not exist .venv\Scripts\python.exe (
 echo Setting up local Python environment...
 %PY% -m venv .venv || (pause & exit /b 1)
)
call .venv\Scripts\python.exe -m pip install -r requirements.txt || (pause & exit /b 1)
set "PYTHONPATH=%cd%\src"
call .venv\Scripts\python.exe -m gitrex demo --output-dir output
if errorlevel 1 (echo Rendering failed. & pause & exit /b 1)
start "" "%cd%\output\preview.html"
echo Finished. GIF is in output\trex.gif
pause
