#!/bin/bash

echo "Starting Resume Analyzer and Booth Recommendations System..."
echo ""

# Function to clean up before exit
function cleanup {
  echo "Stopping servers..."
  kill $LARAVEL_PID
  kill $STREAMLIT_PID
  echo "Servers stopped."
  exit
}

# Trap SIGINT and SIGTERM signals
trap cleanup SIGINT SIGTERM

# Start Laravel Backend
echo "Starting Laravel Backend Server..."
cd "$(dirname "$0")" && php artisan serve &
LARAVEL_PID=$!

# Start Streamlit Frontend
echo "Starting Streamlit Frontend Server..."
cd "$(dirname "$0")/streamlit_frontend" && python -m streamlit run app.py &
STREAMLIT_PID=$!

echo ""
echo "Servers started successfully!"
echo "Laravel Backend: http://localhost:8000"
echo "Streamlit Frontend: http://localhost:8501"
echo ""
echo "Press CTRL+C to stop the servers..."

# Wait for both processes
wait 