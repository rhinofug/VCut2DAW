@echo off
echo ========================================================
echo VCut2DAW - Windows Standalone Compiler (EXE)
echo ========================================================
echo.

IF NOT EXIST venv (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

echo [2/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [3/4] Compiling VCut2DAW into a standalone EXE...
echo This may take a few minutes...
pyinstaller --noconsole --onefile --collect-all aaf2 --collect-all scenedetect --collect-all customtkinter --icon=icon.ico --add-data "icon.ico;." --version-file=file_version_info.txt --name VCut2DAW app.py

echo.
echo [4/4] Finalizing...
IF NOT EXIST builds (
    mkdir builds
)
copy /Y "dist\VCut2DAW.exe" "builds\VCut2DAW.exe"
rmdir /S /Q build
rmdir /S /Q dist
del VCut2DAW.spec

echo.
echo ========================================================
echo SUCCESS! Your standalone EXE is located in the 'builds' folder.
echo You can now double-click builds\VCut2DAW.exe to run the app.
echo ========================================================
pause