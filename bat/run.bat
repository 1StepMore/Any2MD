@echo off
chcp 65001 >nul 2>&1

REM Get the input path from command line argument (drag and drop)
REM Quotes are needed to handle spaces and Chinese characters
set "INPUT_PATH=%~1"

REM If no input, prompt user
if %INPUT_PATH%=="" (
    set /p INPUT_PATH="Enter file or folder path: "
)

REM If still empty, exit
if %INPUT_PATH%=="" exit /b 1

REM Activate virtual environment if it exists
if exist "%~dp0..\venv\Scripts\activate.bat" (
    call "%~dp0..\venv\Scripts\activate.bat"
)

REM Change to project directory (parent of bat folder)
cd /d "%~dp0.."

REM Run the conversion with quoted path
python cli.py --input "%INPUT_PATH%" %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
