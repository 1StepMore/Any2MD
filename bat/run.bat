@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

REM Get the input path from command line argument (drag and drop)
REM Handle copied paths with special characters (Chinese, spaces, etc.)
set "RAW_PATH=%~1"

REM If no input, prompt user
if "%RAW_PATH%"=="" (
    set /p RAW_PATH="Enter file or folder path: "
)

REM Convert to legal Windows path (normalize)
set "INPUT_PATH=%RAW_PATH%"

REM Remove surrounding quotes if present
set "INPUT_PATH=%INPUT_PATH:"=%"

REM Use PowerShell to resolve to absolute path with proper encoding
for /f "delims=" %%i in ('powershell -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; (Get-Item -LiteralPath '%INPUT_PATH%' -ErrorAction SilentlyContinue).FullName"') do set "INPUT_PATH=%%i"

REM If PowerShell failed, try to use the path as-is but ensure it's quoted
if "%INPUT_PATH%"=="" set "INPUT_PATH=%RAW_PATH%"

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
