@echo off
setlocal

REM Get the input path from command line argument (drag and drop)
set "INPUT_PATH=%~1"

REM If no input, prompt user
if "%INPUT_PATH%"=="" (
    set /p INPUT_PATH="Enter file or folder path: "
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the conversion
python cli.py --input "%INPUT_PATH%" %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
