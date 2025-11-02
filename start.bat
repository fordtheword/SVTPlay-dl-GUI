@echo off
echo ============================================================
echo  SVTPlay-dl Web GUI Starter
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Start the application
echo.
echo Starting SVTPlay-dl Web GUI...
echo.
python app.py

REM If the application stops, pause to show any errors
pause
