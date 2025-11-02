@echo off
echo ============================================================
echo  SVTPlay-dl Web GUI Installation
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: ffmpeg is not installed or not in PATH
    echo ffmpeg is required for svtplay-dl to work properly
    echo.
    echo Install ffmpeg using one of these methods:
    echo   1. Download from https://ffmpeg.org/download.html
    echo   2. Use Chocolatey: choco install ffmpeg
    echo   3. Use Scoop: scoop install ffmpeg
    echo.
    echo Continue anyway? (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" (
        echo Installation cancelled
        pause
        exit /b 1
    )
) else (
    echo ffmpeg found:
    ffmpeg -version | findstr "ffmpeg version"
    echo.
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Create downloads directory
if not exist "downloads" (
    echo Creating downloads directory...
    mkdir downloads
    echo.
)

echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo To start the application, run: start.bat
echo.
echo The web interface will be accessible at:
echo   - Local: http://localhost:5000
echo   - Network: http://[YOUR_IP]:5000
echo.
echo To find your IP address, run: ipconfig
echo.
pause
