@echo off
echo ============================================================
echo SVTPlay-dl GUI Server
echo ============================================================
echo.
echo Startar servern...
echo.
echo Efter start kan du oppna webblasaren och ga till:
echo http://localhost:5000
echo.
echo Tryck Ctrl+C for att stoppa servern
echo.
echo ============================================================
echo.

venv\Scripts\python.exe app.py

pause
