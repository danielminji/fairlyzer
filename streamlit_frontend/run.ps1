# Resume Analyzer Application Launcher
# PowerShell script to run the Streamlit application

Write-Host "=====================================================
Resume Analyzer - Application Launcher
=====================================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python and add it to your PATH before running this script."
    Read-Host "Press Enter to exit"
    exit
}

# Ensure required packages are installed
Write-Host "Checking and installing required packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Check if spaCy model is installed
try {
    $spaCyModelInstalled = python -c "import spacy; print('en_core_web_sm' in spacy.util.get_installed_models())"
    if ($spaCyModelInstalled -eq "False") {
        Write-Host "Installing spaCy language model..." -ForegroundColor Yellow
        python -m spacy download en_core_web_sm
    }
} catch {
    Write-Host "Could not check spaCy models. Will attempt to install anyway..." -ForegroundColor Yellow
    python -m spacy download en_core_web_sm
}

# Set environment variables if .env file exists
$envFile = ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment from .env file..." -ForegroundColor Yellow
}
else {
    Write-Host "No .env file found. Creating default configuration..." -ForegroundColor Yellow
    # Create a default .env file
    @"
# Resume Analyzer Application Configuration
API_BASE_URL=http://localhost:8000/api
DEBUG=True
"@ | Out-File -FilePath $envFile -Encoding utf8
}

# Start the application
Write-Host "Starting Resume Analyzer application..." -ForegroundColor Green
try {
    # Run Streamlit with error handling
    streamlit run app.py
}
catch {
    Write-Host "Error starting Streamlit application: $_" -ForegroundColor Red
    Write-Host "Please check that all requirements are installed and try again."
    Read-Host "Press Enter to exit"
} 