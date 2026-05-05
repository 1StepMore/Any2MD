@echo off
chcp 65001 >nul 2>&1

REM Get the batch file's own directory and remove trailing backslash
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Get the input path from command line argument (drag and drop)
set "RAW_PATH=%~1"

REM If no input, prompt user
if "%RAW_PATH%"=="" (
    set /p RAW_PATH="Enter file or folder path: "
)

REM Remove surrounding quotes from input path
set "INPUT_PATH=%RAW_PATH%"
set "INPUT_PATH=%INPUT_PATH:"=%"

REM Activate virtual environment if it exists (use script dir, not CWD)
if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
)

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Run the conversion
python cli.py --input "%INPUT_PATH%" %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
