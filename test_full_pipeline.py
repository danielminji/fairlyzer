import sys
import json
import os

# Adjust Python path to include the streamlit_frontend/lib directory
# This allows importing modules from that directory when the script is run from the root
sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_frontend', 'lib'))

try:
    from enhanced_extractor import EnhancedExtractor
    from enhanced_parser import EnhancedParser
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure that enhanced_extractor.py and enhanced_parser.py are in the streamlit_frontend/lib directory,")
    print("and that you are running this script from the workspace root (resume/).")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_full_pipeline.py <path_to_pdf_resume>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)

    print(f"--- Starting Full Pipeline Test for: {pdf_path} ---")

    # 1. Extract text from PDF
    print("\n--- Stage 1: Extracting Text from PDF ---")
    # It's good practice to set debug on the instances if you want their internal debug prints
    extractor = EnhancedExtractor(debug=True) 
    extracted_text = None
    try:
        extracted_text = extractor.extract_from_pdf(pdf_path)
    except Exception as e:
        print(f"Error during PDF text extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not extracted_text or not extracted_text.strip():
        print("Text extraction yielded no content. Exiting.")
        # Optionally, save the (empty) extracted text for inspection
        # with open("debug_empty_extracted_text.txt", "w", encoding='utf-8') as f:
        # f.write(extracted_text if extracted_text else "")
        sys.exit(1)
    else:
        print(f"Text extracted successfully (length: {len(extracted_text)} chars).")
        # For brevity in the main test script log, we won't print the full text here.
        # The extractor itself will save it if its debug is on.
        # print("\n--- Extracted Text (first 500 chars) ---")
        # print(extracted_text[:500])
        # print("...\n")


    # 2. Parse the extracted text
    print("\n--- Stage 2: Parsing Extracted Text ---")
    # Parser also has its own debug prints if debug=True
    parser = EnhancedParser(debug=True) 
    parsed_data = None
    try:
        parsed_data = parser.parse(extracted_text)
    except Exception as e:
        print(f"Error during text parsing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not parsed_data:
        print("Parsing yielded no data. Exiting.")
        sys.exit(1)

    # 3. Print the final JSON output
    print("\n--- Final Parsed JSON Output ---")
    try:
        # ensure_ascii=False is important for handling non-ASCII characters if any
        print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error serializing parsed data to JSON: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n--- Full Pipeline Test Finished ---")

    primary_field = parsed_data.get("primary_field", "NOT_FOUND_IN_PARSED_DATA")
    print(f"\n**************************************************")
    print(f"FINAL_PRIMARY_FIELD_IN_TEST_OUTPUT: {primary_field}")
    print(f"**************************************************\n")
    
    print("FULL_JSON_OUTPUT_FROM_TEST_FULL_PIPELINE:")
    print(json.dumps(parsed_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 