import json
import sys
import os
from streamlit_frontend.lib.enhanced_parser import EnhancedParser
import traceback

def main():
    extracted_txt_files = [
        # "computerscienceResume_extracted.txt",
        # "financeResume_extracted.txt",
        "medicalResume_extracted.txt"
    ]

    parser = EnhancedParser(debug=True)

    for txt_file in extracted_txt_files:
        print(f"--- Parsing: {txt_file} ---", file=sys.stderr)
        if not os.path.exists(txt_file):
            print(f"Error: Extracted text file not found - {txt_file}. Please run an extractor first.", file=sys.stderr)
            continue

        try:
            with open(txt_file, "r", encoding="utf-8-sig") as f:
                resume_text = f.read()
            
            parsed_data = parser.parse(resume_text)
            print(json.dumps(parsed_data, indent=4))
        
        except Exception as e:
            print(f"An unexpected error occurred while processing {txt_file}:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print(f"Error details: {e}", file=sys.stderr)

if __name__ == "__main__":
    main() 