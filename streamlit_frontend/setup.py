#!/usr/bin/env python
"""
Setup script for Resume Analyzer & Booth Recommendations

This script installs required dependencies and downloads models needed for NLP tasks.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install requirements from requirements.txt"""
    print("Installing requirements...")
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if not requirements_path.exists():
        print("Error: requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
        print("✅ Successfully installed Python requirements")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def download_spacy_model():
    """Download spaCy language model"""
    print("Downloading spaCy model...")
    try:
        # Download the small English model
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ Successfully downloaded spaCy model")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading spaCy model: {e}")
        return False

def download_nltk_resources():
    """Download necessary NLTK resources"""
    print("Downloading NLTK resources...")
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        print("✅ Successfully downloaded NLTK resources")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK resources: {e}")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed and provide installation instructions if not"""
    print("Checking for Tesseract OCR...")
    try:
        import pytesseract
        try:
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR is installed (version {version})")
            return True
        except Exception:
            print("❌ Tesseract OCR is not installed or not in PATH")
            print("\nInstallation instructions:")
            print("  - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki")
            print("  - macOS: Run 'brew install tesseract'")
            print("  - Ubuntu/Debian: Run 'sudo apt install tesseract-ocr'")
            print("\nAfter installation, make sure the Tesseract executable is in your PATH")
            return False
    except ImportError:
        print("❌ pytesseract package is not installed")
        return False

def main():
    """Main setup function"""
    print("=" * 70)
    print("Setting up Resume Analyzer & Booth Recommendations")
    print("=" * 70)
    
    success = True
    
    # Install Python requirements
    if not install_requirements():
        success = False
    
    # Download spaCy model
    if not download_spacy_model():
        success = False
    
    # Download NLTK resources
    if not download_nltk_resources():
        success = False
    
    # Check for Tesseract OCR
    if not check_tesseract():
        print("⚠️ Warning: Tesseract OCR not found. OCR features will not work.")
        print("See above for installation instructions.")
    
    print("\n" + "=" * 70)
    if success:
        print("✅ Setup completed successfully!")
        print("\nYou can now run the application with:")
        print("  python -m streamlit run app.py")
    else:
        print("⚠️ Setup completed with some issues. Please check the messages above.")
    print("=" * 70)

if __name__ == "__main__":
    main() 