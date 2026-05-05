@echo off
chcp 65001 >nul 2>&1

REM Get input path - use first argument as-is with quotes
if "%~1"=="" (
    echo Drag a file or folder onto this batch file.
    echo Or run from command line: run.bat "path\to\file.pdf"
    pause
    exit /b 1
)

REM Get the input path, preserving quotes for paths with spaces
set "INPUT_PATH=%~1"

REM Activate virtual environment if it exists
if exist "%~dp0..\venv\Scripts\activate.bat" (
    call "%~dp0..\venv\Scripts\activate.bat"
)

REM Change to project directory (parent of bat folder)
cd /d "%~dp0.."

REM Run the conversion with quoted path
python cli.py --input %INPUT_PATH% %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
