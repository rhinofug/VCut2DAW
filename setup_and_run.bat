@echo off
echo Starting VCut2ProTools Setup for Windows...

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing required libraries...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Starting the application...
python app.py
pause
