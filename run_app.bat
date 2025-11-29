@echo off
REM FinCA AI Application Launcher
REM This script activates the virtual environment and runs the Streamlit app

echo 🚀 Starting FinCA AI...
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)

echo ✅ Virtual environment activated successfully
echo.

REM Set default port if not specified
if "%1"=="" (
    set PORT=8506
) else (
    set PORT=%1
)

echo 🌐 Starting Streamlit app on port %PORT%...
echo URL: http://localhost:%PORT%
echo.
echo 📝 Press Ctrl+C to stop the application
echo.

REM Run the Streamlit app
streamlit run src/ui/app_integrated.py --server.port %PORT% --server.headless true

REM Deactivate venv when done
call venv\Scripts\deactivate.bat