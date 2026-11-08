@echo off
setlocal
cd /d "%~dp0"
echo =========================================
echo   GitRex - Real GitHub Contributions
 echo =========================================
set "PY=python"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 --version >nul 2>&1
  if not errorlevel 1 set "PY=py -3"
)
%PY% --version >nul 2>&1
if errorlevel 1 (echo Install Python 3.10 or newer first. & pause & exit /b 1)
if not exist .venv\Scripts\python.exe (%PY% -m venv .venv || (pause & exit /b 1))
call .venv\Scripts\python.exe -m pip install -r requirements.txt || (pause & exit /b 1)
if not defined GH_TOKEN if not defined GITHUB_TOKEN (
  where gh >nul 2>&1
  if errorlevel 1 (
    echo GitHub CLI not found. Install gh from https://cli.github.com/ and run: gh auth login
    echo Or set GH_TOKEN in your environment. Do NOT put tokens in project files.
    pause & exit /b 1
  )
  for /f "usebackq delims=" %%i in (`gh auth token 2^>nul`) do set "GH_TOKEN=%%i"
  if not defined GH_TOKEN (echo Sign in first using: gh auth login & pause & exit /b 1)
)
set "USER_NAME=narayanangourav"
set /p "USER_NAME=GitHub username [narayanangourav]: "
if "%USER_NAME%"=="" set "USER_NAME=narayanangourav"
set "PYTHONPATH=%cd%\src"
call .venv\Scripts\python.exe -m gitrex live --login "%USER_NAME%" --output-dir output
if errorlevel 1 (echo Live collection failed. Existing output was not replaced by demo data. & pause & exit /b 1)
start "" "%cd%\output\preview.html"
echo Finished. Output: output\trex.gif
pause
