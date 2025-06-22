#!/usr/bin/env python
import sys
import json
import os
import traceback # For detailed error logging

# Add the current directory (streamlit_frontend) to the path
# so we can import from lib.enhanced_parser and lib.analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.enhanced_parser import EnhancedParser
from lib.enhanced_extractor import EnhancedExtractor # Import EnhancedExtractor

def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error": "Usage: python enhanced_parser_cli.py <file_path>"
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(json.dumps({
            "error": f"File not found: {file_path}"
        }))
        sys.exit(1)
    
    try:
        # Initialize EnhancedExtractor and extract text from the PDF
        extractor = EnhancedExtractor(debug=False) # Set debug as needed
        text = extractor.extract_from_pdf(file_path)
        
        if text is None or not text.strip():
            print(json.dumps({
                "error": f"Failed to extract text from PDF: {file_path}"
            }))
            sys.exit(1)
        
        # Initialize EnhancedParser with auto-detection for primary_field
        parser = EnhancedParser()
        parsed_data = parser.parse(text)
        
        print(json.dumps(parsed_data, indent=4))
        
    except Exception as e:
        print(json.dumps({
            "error": f"Error processing resume: {str(e)}", # Changed error message slightly for clarity
            "traceback": traceback.format_exc() 
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()