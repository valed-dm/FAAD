@echo off
title Freenet Alias Adder - Installer

:: Clear the screen for a clean start
cls

echo.
echo =======================================================
echo     Welcome to the Freenet Alias Adder Installer!
echo =======================================================
echo.
echo This script will set up the necessary environment and
echo install the required Python packages.
echo.

:: Step 1: Check if Python is installed and available in PATH
echo --- [Step 1/3] Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found on your system or is not in your PATH.
    echo Please install Python 3.8+ from python.org and ensure you check
    echo "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)
echo Python found!
echo.

:: Step 2: Check if the virtual environment already exists
echo --- [Step 2/3] Setting up virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment 'venv' already exists. Skipping creation.
) else (
    echo Creating virtual environment 'venv'...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create the virtual environment.
        pause
        exit /b
    )
    echo Virtual environment created successfully.
)
echo.

:: Step 3: Activate the virtual environment and install packages
echo --- [Step 3/3] Installing required packages from requirements.txt...
call venv\Scripts\activate
pip install -r requirements.txt

:: Check if pip install was successful
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed. Please check your internet connection
    echo and run this script again.
    pause
    exit /b
)
echo.
echo =======================================================
echo      SUCCESS! Installation is complete.
echo =======================================================
echo.
echo You can now run 'start.bat' to launch the application.
echo.
pause
