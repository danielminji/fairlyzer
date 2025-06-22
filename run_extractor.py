import os
import sys
from streamlit_frontend.lib.enhanced_extractor import EnhancedExtractor

def main():
    # Ensure the script can find the streamlit_frontend.lib module
    # This might be needed if running from a different directory or if PYTHONPATH isn't set
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(current_dir) # Assumes script is in root, and lib is in streamlit_frontend/lib
    # sys.path.insert(0, project_root) 
    # print(f"DEBUG: sys.path modified: {sys.path}")


    pdf_files_to_extract = [
        os.path.join("public", "storage", "resumes", "computerscienceResume.pdf"),
        os.path.join("public", "storage", "resumes", "financeResume.pdf"),
        os.path.join("public", "storage", "resumes", "medicalResume.pdf")
    ]

    # Instantiate extractor with debug=True to save .txt files
    extractor = EnhancedExtractor(debug=True)

    print("Starting PDF text extraction...")
    for pdf_path in pdf_files_to_extract:
        print(f"Processing: {pdf_path}")
        if not os.path.exists(pdf_path):
            print(f"Error: File not found - {pdf_path}", file=sys.stderr)
            continue
        
        try:
            # The extract_from_pdf method with debug=True will save the .txt file
            # in the current working directory (workspace root in this case)
            extracted_text = extractor.extract_from_pdf(pdf_path)
            if extracted_text:
                print(f"Successfully processed and initiated save for: {os.path.basename(pdf_path)}")
                # The debug output inside EnhancedExtractor handles the actual file saving.
            else:
                print(f"Warning: No text extracted or an error occurred for {pdf_path}", file=sys.stderr)
        except Exception as e:
            print(f"An error occurred while processing {pdf_path}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    print("PDF text extraction process complete. Check for _extracted.txt files in the workspace root.")

if __name__ == "__main__":
    main() 