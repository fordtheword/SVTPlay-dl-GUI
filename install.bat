@echo off
echo ============================================================
echo  SVTPlay-dl Web GUI - Installation
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEL: Python ar inte installerat eller inte i PATH
    echo.
    echo Installera Python 3.9+ fran https://www.python.org/
    echo VIKTIGT: Bocka i "Add Python to PATH" under installationen!
    echo.
    pause
    exit /b 1
)

echo [OK] Python hittades:
python --version
echo.

echo ============================================================
echo  Skapar virtuell miljo och installerar allt...
echo ============================================================
echo.

REM Create virtual environment
echo [1/4] Skapar virtuell miljo...
python -m venv venv
if errorlevel 1 (
    echo.
    echo FEL: Kunde inte skapa virtuell miljo.
    echo.
    pause
    exit /b 1
)
echo       OK!
echo.

REM Activate virtual environment
echo [2/4] Aktiverar virtuell miljo...
call venv\Scripts\activate.bat
echo       OK!
echo.

REM Upgrade pip
echo [3/4] Uppgraderar pip...
python -m pip install --upgrade pip --quiet
echo       OK!
echo.

REM Install requirements (including FFmpeg via imageio-ffmpeg!)
echo [4/4] Installerar allt (Flask, svtplay-dl, FFmpeg, etc)...
echo       Detta kan ta ett par minuter...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo VARNING: Nagra beroenden kunde inte installeras korrekt.
    echo Forsok igen eller kontrollera internetanslutningen.
    echo.
    pause
    exit /b 1
)
echo       OK!
echo.

REM Create downloads directory
if not exist "downloads" (
    mkdir downloads
)

REM Create profiles directory
if not exist "profiles" (
    mkdir profiles
)

echo ============================================================
echo  Installation Klar!
echo ============================================================
echo.
echo FFmpeg har installerats automatiskt via pip - inga problem!
echo.
echo Nasta steg:
echo   1. Dubbelklicka pa 'start.bat' for att starta servern
echo   2. Oppna webblasaren: http://localhost:5000
echo.
echo For hjalp, se README.md
echo.
pause
