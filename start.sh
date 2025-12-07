#!/bin/bash

# SpritzLottery Startup Script
# This script activates the virtual environment and starts the Flask application

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment 'venv' not found!"
    echo "Please create it first with: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Error: Failed to activate virtual environment!"
    exit 1
fi

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Warning: Flask not found. Installing requirements..."
    pip install -r requirements.txt
fi

# Start the Flask application
echo "Starting SpritzLottery..."
echo "Application will be available at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

