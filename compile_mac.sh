#!/bin/bash

echo "========================================================"
echo "VCut2DAW - macOS Standalone Compiler (.app)"
echo "========================================================"
echo ""

if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3.9 or higher."
    exit
fi

if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[2/4] Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo ""
echo "[3/4] Compiling VCut2DAW into a standalone Mac App..."
echo "This may take a few minutes..."
pyinstaller --noconsole --windowed --collect-all aaf2 --collect-all scenedetect --collect-all customtkinter --icon=icon.icns --add-data "icon.icns:." --name VCut2DAW app.py

echo ""
echo "[4/4] Finalizing..."
mkdir -p builds
rm -rf builds/VCut2DAW.app
cp -R dist/VCut2DAW.app builds/VCut2DAW.app
rm -rf build dist VCut2DAW.spec

echo ""
echo "========================================================"
echo "SUCCESS! Your standalone Mac App is located in the 'builds' folder."
echo "You can now double-click builds/VCut2DAW.app to run the app."
echo "========================================================"