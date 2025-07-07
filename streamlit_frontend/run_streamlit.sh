#!/bin/bash

echo "Starting Streamlit Resume Analyzer Frontend..."
echo ""

cd "$(dirname "$0")"
python -m streamlit run app.py

echo ""
echo "Server stopped." 