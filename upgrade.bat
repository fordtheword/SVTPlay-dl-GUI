@echo off
echo ============================================================
echo SVTPlay-dl GUI - Uppgradering
echo ============================================================
echo.

echo Hamtar senaste uppdateringar fran GitHub...
git pull
if errorlevel 1 (
    echo.
    echo FEL: Kunde inte hamta uppdateringar fran GitHub
    echo Kontrollera din internetanslutning och forsoker igen.
    pause
    exit /b 1
)

echo.
echo Uppgraderar Python-paket...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade

echo.
echo ============================================================
echo Uppgradering klar!
echo ============================================================
echo.
echo Vill du starta servern nu? (J/N)
set /p answer=

if /i "%answer%"=="J" (
    echo.
    echo Startar servern...
    venv\Scripts\python.exe app.py
) else (
    echo.
    echo Servern startades inte. Kor start.bat nar du vill starta den.
    pause
)
