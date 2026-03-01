@echo off
echo Starting JarvisLite Setup...

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

:: Activate venv and install requirements if needed
call venv\Scripts\activate.bat
echo Verifying dependencies...
pip install -r backend\requirements.txt

:: Start Backend server
echo.
echo =======================================
echo Starting FastAPI Backend using Uvicorn
echo =======================================
start cmd /k "call venv\Scripts\activate.bat && cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for a few seconds to let backend initialize
timeout /t 3 /nobreak > nul

:: Open Frontend in browser
echo.
echo =======================================
echo Opening Frontend in default browser...
echo =======================================
start "" "%CD%\frontend\index.html"

echo.
echo JarvisLite is running!
pause
