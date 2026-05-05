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

REM Change to project directory (parent of bat folder)
cd /d "%~dp0.."

REM Run the conversion - pass all arguments through to preserve quotes
python cli.py %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
