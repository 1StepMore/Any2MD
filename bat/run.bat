@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

REM Get the batch file's own directory (D:\贯维\Any2MD\)
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Get the input path from command line argument (drag and drop)
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

REM Activate virtual environment if it exists (use script dir, not CWD)
if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
)

REM Run the conversion (use script dir, not CWD)
cd /d "%SCRIPT_DIR%"
python "%SCRIPT_DIR%\cli.py" --input "%INPUT_PATH%" %*

REM Pause to show results
echo.
echo Conversion complete. Press any key to exit.
pause >nul
