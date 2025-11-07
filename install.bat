@echo off
echo ============================================================
echo  SVTPlay-dl Web GUI - Enkel Installation
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

REM Check if ffmpeg is in PATH
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ffmpeg ar inte installerat i PATH
    echo.
    echo Vill du att installationen laddar ner ffmpeg automatiskt? (Rekommenderat)
    echo Detta laddar ner ffmpeg till projektkatalogen - ingen PATH-konfiguration behovs.
    echo.
    echo Alternativ:
    echo   [A] Ladda ner ffmpeg automatiskt till projektkatalogen (Enklast)
    echo   [S] Hoppa over - jag installerar ffmpeg sjalv
    echo.
    set /p ffmpeg_choice=Val (A/S):

    if /i "%ffmpeg_choice%"=="A" (
        echo.
        echo Laddar ner ffmpeg...
        echo.

        REM Create bin directory
        if not exist "bin" mkdir bin

        REM Download ffmpeg using PowerShell (Windows 10+)
        echo Detta kan ta nagra minuter beroende pa internetanslutning...
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'bin\ffmpeg.zip'}"

        if errorlevel 1 (
            echo.
            echo VARNING: Kunde inte ladda ner ffmpeg automatiskt.
            echo.
            echo Installera ffmpeg manuellt:
            echo   1. Ga till: https://ffmpeg.org/download.html
            echo   2. Ladda ner Windows build
            echo   3. Extrahera ffmpeg.exe till 'bin' mappen i projektet
            echo      ELLER installera med: choco install ffmpeg / scoop install ffmpeg
            echo.
        ) else (
            echo.
            echo Packar upp ffmpeg...
            powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Expand-Archive -Path 'bin\ffmpeg.zip' -DestinationPath 'bin\temp' -Force}"

            REM Find and move ffmpeg.exe
            for /r "bin\temp" %%i in (ffmpeg.exe) do (
                copy "%%i" "bin\ffmpeg.exe" >nul 2>&1
            )

            REM Cleanup
            del /q "bin\ffmpeg.zip" >nul 2>&1
            rmdir /s /q "bin\temp" >nul 2>&1

            if exist "bin\ffmpeg.exe" (
                echo [OK] ffmpeg installerat lokalt i bin\ffmpeg.exe
                echo.
            ) else (
                echo VARNING: Kunde inte extrahera ffmpeg. Installera manuellt.
                echo.
            )
        )
    ) else (
        echo.
        echo Hoppar over ffmpeg-installation.
        echo OBS: Du maste installera ffmpeg manuellt for att programmet ska fungera!
        echo.
    )
) else (
    echo [OK] ffmpeg hittades i PATH:
    ffmpeg -version 2>&1 | findstr "ffmpeg version"
    echo.
)

REM Create virtual environment
echo Skapar virtuell miljo...
python -m venv venv
if errorlevel 1 (
    echo.
    echo FEL: Kunde inte skapa virtuell miljo.
    echo.
    pause
    exit /b 1
)
echo [OK] Virtuell miljo skapad
echo.

REM Activate virtual environment
echo Aktiverar virtuell miljo...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Uppgraderar pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip uppgraderad
echo.

REM Install requirements
echo Installerar beroenden (Flask, svtplay-dl, etc)...
echo Detta kan ta ett par minuter...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo VARNING: Nagra beroenden kunde inte installeras korrekt.
    echo Forsok igen eller kontrollera internetanslutningen.
    echo.
) else (
    echo [OK] Alla beroenden installerade
    echo.
)

REM Create downloads directory
if not exist "downloads" (
    echo Skapar nedladdningsmapp...
    mkdir downloads
    echo [OK] Mappen 'downloads' skapad
    echo.
)

REM Create profiles directory
if not exist "profiles" (
    mkdir profiles
)

echo ============================================================
echo  Installation Klar!
echo ============================================================
echo.
echo Nasta steg:
echo   1. Dubbelklicka pa 'start.bat' for att starta servern
echo   2. Oppna webblasaren: http://localhost:5000
echo.
if exist "bin\ffmpeg.exe" (
    echo OBS: ffmpeg har installerats lokalt i projektet.
    echo      Du behover INTE lagga till nagonting i PATH!
    echo.
)
echo For hjalp, se README.md eller:
echo   https://github.com/andersmolausson/SVTPlay-dl-GUI
echo.
pause
