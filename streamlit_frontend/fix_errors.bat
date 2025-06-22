@echo off
echo =====================================================
echo Resume Analyzer - System Error Fixer and Launcher
echo =====================================================

REM Check for Python installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b
)

REM Ensure required packages are installed
echo Installing/updating required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Check if spaCy model is installed
python -c "import spacy; exit(0 if 'en_core_web_sm' in spacy.util.get_installed_models() else 1)" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing spaCy language model...
    python -m spacy download en_core_web_sm
)

REM Navigate to app directory
cd %~dp0

REM Start the application
echo Starting application...
streamlit run app.py

pause 