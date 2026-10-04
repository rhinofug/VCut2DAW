#!/bin/bash

echo "Starting VCut2ProTools Setup for macOS/Linux..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3.9 or higher."
    exit
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the app
echo "Starting VCut2ProTools..."
python app.py
