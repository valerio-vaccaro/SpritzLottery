@echo off
REM SpritzLottery Startup Script for Windows
REM This script activates the virtual environment and starts the Flask application

REM Change to the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Error: Virtual environment 'venv' not found!
    echo Please create it first with: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Warning: Flask not found. Installing requirements...
    pip install -r requirements.txt
)

REM Start the Flask application
echo Starting SpritzLottery...
echo Application will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause

