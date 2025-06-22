@echo off
SETLOCAL

echo Starting Streamlit server...
python -m streamlit run app.py

echo Press any key to close this window...
pause > nul
ENDLOCAL 