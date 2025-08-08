@echo off
title Freenet Alias Adder - Start

:: Best practice: Change directory to the script's location.
:: This ensures that main.py and the venv folder are found,
:: no matter where the user runs the batch file from.
cd /d "%~dp0"

:: Clear the screen
cls

echo.
echo =======================================================
echo      Starting the Freenet Alias Adder...
echo =======================================================
echo.

:: Step 1: Check if the virtual environment exists.
:: This confirms that 'install.bat' has been run successfully.
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] The required environment was not found.
    echo Please run 'install.bat' first to complete the setup.
    echo.
    pause
    exit /b
)

:: Step 2: Activate the environment and run the main Python script
echo --- Activating environment and running the script ---
echo.
call venv\Scripts\activate
python main.py

echo.
echo =======================================================
echo      Script has finished its execution.
echo =======================================================
echo.
echo You can review the results in the 'output' folder.
echo Press any key to close this window.
echo.
pause
