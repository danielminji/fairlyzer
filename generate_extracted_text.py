import os
import sys
from pathlib import Path

# Ensure streamlit_frontend.lib can be found
# This assumes the script is run from the workspace root 'resume'
# and the library is in 'resume/streamlit_frontend/lib'
sys.path.insert(0, os.getcwd())

from streamlit_frontend.lib.enhanced_extractor import EnhancedExtractor

def run_extraction(pdf_file_path):
    print(f"Processing {pdf_file_path}...")
    if not os.path.exists(pdf_file_path):
        print(f"ERROR: PDF file not found - {pdf_file_path}")
        return

    # Instantiate EnhancedExtractor with debug=True to save _extracted.txt files
    extractor = EnhancedExtractor(debug=True)
    
    # extract_from_pdf will save the file due to debug=True
    extracted_text = extractor.extract_from_pdf(pdf_file_path)
    
    if extracted_text:
        # The file is saved by the extractor itself when debug=True
        # Output filename will be like <pdf_name>_extracted.txt or <pdf_name>_ocr_extracted.txt
        print(f"Text extraction successful for {pdf_file_path}.")
        # We can list expected output file names for confirmation if needed
        base_name = Path(pdf_file_path).stem
        expected_miner_file = f"{base_name}_extracted.txt"
        expected_ocr_file = f"{base_name}_ocr_extracted.txt"
        if os.path.exists(expected_miner_file):
            print(f"Saved to: {expected_miner_file}")
        elif os.path.exists(expected_ocr_file):
            print(f"Saved to: {expected_ocr_file} (used OCR)")
        else:
            print(f"WARN: Extracted text but output file not found for {base_name}")

    else:
        print(f"ERROR: Failed to extract text from {pdf_file_path}")

def main():
    # List of PDF files to process
    # Assuming they are in public/storage/resumes/ as before
    # The paths should be relative to the workspace root where this script is run
    resume_pdfs = [
        os.path.join("public", "storage", "resumes", "computerscienceResume.pdf"),
        os.path.join("public", "storage", "resumes", "financeResume.pdf"),
        os.path.join("public", "storage", "resumes", "medicalResume.pdf")
    ]

    for pdf_path in resume_pdfs:
        run_extraction(pdf_path)
    
    print("\nExtraction process finished.")

if __name__ == "__main__":
    # Ensure correct CWD if running from an IDE, etc.
    # For this tool, it should run from the workspace root.
    # print(f"Current Working Directory: {os.getcwd()}")
    main() 