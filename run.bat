@echo off
echo Starting Resume Analyzer and Booth Recommendations System...
echo.

echo Starting Laravel Backend Server...
start cmd /k "cd %~dp0 && php artisan serve"

echo Starting Streamlit Frontend Server...
start cmd /k "cd %~dp0streamlit_frontend && python -m streamlit run app.py"

echo.
echo Servers started successfully!
echo Laravel Backend: http://localhost:8000
echo Streamlit Frontend: http://localhost:8501
echo.
echo Press any key to stop the servers...
pause > nul

echo Stopping servers...
taskkill /F /FI "WINDOWTITLE eq Laravel Backend*" > nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Streamlit Frontend*" > nul 2>&1
echo Servers stopped. 