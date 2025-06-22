"""
Test script for resume upload functionality

This script can be run to test the resume upload functionality
without using the full Streamlit interface.

Usage:
    python test_upload.py
"""

import os
import sys
import tempfile
from lib import api
import logging
import json
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_test_pdf():
    """Create a simple test PDF file in memory"""
    try:
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "Test Resume for Upload")
        c.drawString(100, 700, "Skills: Python, JavaScript, API Integration")
        c.drawString(100, 650, "Experience: Software Developer, 5 years")
        c.drawString(100, 600, "Education: Computer Science Degree")
        c.save()
        buffer.seek(0)
        
        # Create a temporary file to simulate file upload
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp.write(buffer.read())
        temp_filename = temp.name
        temp.close()
        
        # Create a file-like object to mimic what Streamlit gives
        class MockFileUpload:
            def __init__(self, path, name):
                self.path = path
                self.name = name
                self.type = "application/pdf"
            
            def read(self):
                with open(self.path, 'rb') as f:
                    return f.read()
                    
            def getvalue(self):
                return self.read()
        
        return MockFileUpload(temp_filename, "test_resume.pdf"), temp_filename
    except ImportError:
        logger.error("reportlab module not installed. Please install it with: pip install reportlab")
        sys.exit(1)

def test_resume_upload():
    """Test the resume upload functionality"""
    logger.info("Testing resume upload functionality")
    
    # Mock authorization (for testing only)
    # In a real scenario, you would login first
    import streamlit as st
    if "user_token" not in st.session_state:
        # For testing only - this will make API calls fail unless you login first
        st.session_state.user_token = None
        logger.warning("No auth token set. Login manually first or API calls will fail!")
    
    # Create test PDF
    mock_file, temp_filename = create_test_pdf()
    
    try:
        # Test the upload function
        logger.info(f"Uploading test resume: {mock_file.name}")
        response, success = api.upload_resume(mock_file, "Test resume upload")
        
        # Print results
        if success:
            logger.info("✅ Upload successful!")
            logger.info(f"Response: {json.dumps(response, indent=2)}")
        else:
            logger.error("❌ Upload failed!")
            logger.error(f"Error: {response.get('error', 'Unknown error')}")
            if 'details' in response:
                logger.error(f"Details: {response['details']}")
    
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_filename)
            logger.info(f"Temporary file {temp_filename} deleted")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file: {e}")

if __name__ == "__main__":
    # Run the test
    test_resume_upload() 