@echo off
REM MCP Server Build Script for Windows
REM This is a convenience wrapper around build.py

setlocal enabledelayedexpansion

echo ======================================================================
echo   MCP Server Build for Windows
echo ======================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Check if we're in a virtual environment
if not defined VIRTUAL_ENV (
    echo [WARNING] Not in a virtual environment
    echo [INFO] Checking for .venv...
    
    if exist ".venv\Scripts\activate.bat" (
        echo [INFO] Found .venv, activating...
        call .venv\Scripts\activate.bat
    ) else (
        echo [WARNING] No .venv found. Install dependencies with: pip install -e .
    )
)

REM Run the Python build script
echo [INFO] Starting build process...
echo.

python build.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    exit /b 1
)

echo.
echo [SUCCESS] Build completed successfully!
exit /b 0
