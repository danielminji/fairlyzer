@echo off
echo ================================================
echo Resume Analyzer & Booth Recommendations Setup
echo ================================================
echo.

echo Running setup script...
python setup.py
if %errorlevel% neq 0 (
    echo Setup failed with error code %errorlevel%
    pause
    exit /b %errorlevel%
)

echo.
echo ================================================
echo Starting the application...
echo ================================================
echo.

python -m streamlit run app.py

if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%
    pause
)

pause 