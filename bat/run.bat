@echo off
chcp 65001 >nul 2>&1

REM Get the input path from command line argument (drag and drop)
set "RAW_PATH=%~1"

REM If no input, prompt user
if "%RAW_PATH%"=="" (
    set /p RAW_PATH="Enter file or folder path: "
)

REM Remove surrounding quotes from input path
set "INPUT_PATH=%RAW_PATH%"
set "INPUT_PATH=%INPUT_PATH:"=%"

REM Get project root (parent of bat directory)
set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%\.."

REM Activate virtual environment if it exists
if exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
)

REM Change to project directory
cd /d "%PROJECT_ROOT%"

REM Run the conversion
python cli.py --input "%INPUT_PATH%" %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
