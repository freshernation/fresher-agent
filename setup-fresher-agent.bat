@echo off
rem One-command setup for Windows:   setup-fresher-agent.bat
rem Safe to run more than once.
setlocal
cd /d "%~dp0"

set PYTHON=
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set PYTHON=py -3
if not defined PYTHON (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set PYTHON=python
)
if not defined PYTHON (
    echo Python 3.10 or newer is needed.
    echo Install it from https://www.python.org/downloads/ and run this script again.
    exit /b 1
)

echo 1/4  Creating .venv (a private folder for this project's packages)
if not exist .venv (
    %PYTHON% -m venv .venv || exit /b 1
)

echo 2/4  Installing packages
.venv\Scripts\python -m pip install --quiet --upgrade pip || exit /b 1
.venv\Scripts\python -m pip install --quiet -r requirements.txt || exit /b 1

echo 3/4  Creating .env
if not exist .env copy .env.example .env >nul

echo 4/4  Checking that everything works
echo.
.venv\Scripts\python check.py || exit /b 1

echo.
echo Next:
echo   .venv\Scripts\activate             do this once in every new terminal
echo   python run.py                      chat with your agent
echo   notepad tools.py                   add your own tool
echo   notepad .env                       add an API key to use a real model
