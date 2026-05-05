@echo off
chcp 65001 >nul 2>&1

REM If no arguments, show help
if "%~1"=="" (
    echo Drag a file or folder onto this batch file.
    echo Or run from command line: run.bat "path\to\file.pdf"
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "%~dp0..\venv\Scripts\activate.bat" (
    call "%~dp0..\venv\Scripts\activate.bat"
)

REM Change to project directory
cd /d "%~dp0.."

REM Run conversion (config.yaml is auto-loaded by Python)
python cli.py --input "%~1"

REM Show log location
echo.
echo Conversion complete. Logs saved to logs\ directory.
pause >nul
