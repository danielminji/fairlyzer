#!/usr/bin/env python
import os
import re
import sys
import json
from pathlib import Path

# PDF Extraction
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import pytesseract
from pdf2image import convert_from_path
import tempfile
import io
import cv2
import numpy as np

class EnhancedExtractor:
    """Improved PDF text extraction with better layout handling for modern resumes"""
    
    def __init__(self, debug=False):
        self.debug = debug
        # Pre-normalized section headers for efficient lookup in _process_layout
        self._normalized_section_keywords = {
            header_enum.upper().replace(" ", ""): True 
            for header_list in [
                ['PROFILE', 'SUMMARY', 'OBJECTIVE'], 
                ['WORK EXPERIENCE', 'EXPERIENCE', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE'],
                ['EDUCATION', 'ACADEMIC BACKGROUND', 'QUALIFICATIONS'],
                ['SKILLS', 'TECHNICAL SKILLS'],
                ['LANGUAGES'],
                ['PROJECTS', 'CERTIFICATIONS'], # Grouped some for simplicity of the set
                ['ACHIEVEMENTS', 'INTERESTS', 'CONTACT', 'REFERENCES', 'TRAINING', 'PUBLICATIONS', 'AWARDS', 'VOLUNTEER']
            ] for header_enum in header_list
        }
        if self.debug:
            print(f"DEBUG (__init__): Normalized section keywords for matching: {list(self._normalized_section_keywords.keys())[:10]}")
        
    def extract_from_pdf(self, pdf_path):
        """Extract text from PDF with enhanced layout recognition"""
        try:
            if self.debug:
                print(f"Extracting text from: {pdf_path}")
            
            # First try with PDFMiner for better text-based extraction
            text_from_miner = self._extract_with_pdfminer(pdf_path)
            
            # Check if the extraction was successful and has enough content
            if text_from_miner and len(text_from_miner.strip()) > 200:
                processed_text = self._process_layout(text_from_miner)
                
                # Save extracted text to file for debugging if needed
                if self.debug:
                    # Output to the current working directory of the script execution
                    debug_output_filename = f"{Path(Path(pdf_path).name).stem}_extracted.txt"
                    with open(debug_output_filename, "w", encoding="utf-8") as f:
                        f.write(processed_text)
                    if self.debug: print(f"DEBUG (EnhancedExtractor): Saved PDFMiner extracted text to: {os.path.abspath(debug_output_filename)}")
                    
                return processed_text
            
            # If PDFMiner failed or returned minimal text, try OCR as fallback
            if self.debug:
                print("PDFMiner extraction insufficient, trying OCR...")
                
            text_from_ocr = self._extract_with_ocr(pdf_path)
            processed_text = self._process_layout(text_from_ocr)
            
            # Save extracted text to file for debugging if needed
            if self.debug:
                # Output to the current working directory of the script execution
                debug_output_filename_ocr = f"{Path(Path(pdf_path).name).stem}_ocr_extracted.txt"
                with open(debug_output_filename_ocr, "w", encoding="utf-8") as f:
                    f.write(processed_text)
                if self.debug: print(f"DEBUG (EnhancedExtractor): Saved OCR extracted text to: {os.path.abspath(debug_output_filename_ocr)}")
                    
            return processed_text
            
        except Exception as e:
            if self.debug:
                print(f"Error extracting PDF: {str(e)}")
                import traceback
                traceback.print_exc()
            return None
    
    def _extract_with_pdfminer(self, pdf_path):
        """Extract text using PDFMiner with optimized parameters"""
        # Configure optimized layout parameters for better text extraction
        laparams = LAParams(
            line_margin=0.25,      # Lower value to detect closely spaced lines
            word_margin=0.1,       # Lower for better word grouping
            char_margin=1.5,       # Character spacing
            boxes_flow=0.5,        # Controls text flow detection (Reverted from -0.8)
            detect_vertical=True,  # Important for modern layouts with columns
            all_texts=True         # Capture all text blocks
        )
        
        # Extract raw text
        raw_text = extract_text(pdf_path, laparams=laparams)
        return raw_text
    
    def _extract_with_ocr(self, pdf_path):
        """Extract text using OCR for better handling of complex layouts"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            extracted_text = ""
            
            for i, image in enumerate(images):
                # Convert PIL image to OpenCV format
                open_cv_image = np.array(image) 
                open_cv_image = open_cv_image[:, :, ::-1].copy() 
                
                # Apply image preprocessing to improve OCR
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                
                # Find contours and sort them from top to bottom
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[1])
                
                # Create image mask for sections
                mask = np.ones(gray.shape, dtype=np.uint8) * 255
                
                # Extract each section and perform OCR
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    # Skip very small contours that could be noise
                    if w < 50 or h < 50:  
                        continue
                    
                    # Extract only this contour
                    section_roi = gray[y:y+h, x:x+w]
                    section_text = pytesseract.image_to_string(section_roi)
                    extracted_text += section_text + "\n\n"
                
                # If no contours were processed, fall back to whole page OCR
                if not extracted_text.strip():
                    extracted_text = pytesseract.image_to_string(gray)
            
            return extracted_text
            
        except Exception as e:
            if self.debug:
                print(f"OCR extraction error: {str(e)}")
            # Return an empty string on error
            return ""
    
    def _process_layout(self, text):
        """Process extracted text to handle modern resume layouts"""
        if not text:
            return ""
            
        # Split into lines
        lines = text.split('\n')
        
        # Remove excess blank lines but preserve meaningful spacing
        processed_lines = []
        blank_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_count += 1
                if blank_count <= 2:  # Keep up to two consecutive blank lines
                    processed_lines.append('')
            else:
                blank_count = 0
                processed_lines.append(stripped)
        
        # Identify and mark potential section headers
        structured_text = []
        for i, line in enumerate(processed_lines):
            if not line:
                structured_text.append('')
                continue
            
            current_line_normalized = line.upper().replace(" ", "")
            is_header = self._normalized_section_keywords.get(current_line_normalized, False)
            
            is_likely_header = False
            if not is_header: # Only evaluate likely_header if not an exact known header
                line_stripped_for_check = line.strip()
                num_words = len(line_stripped_for_check.split())

                # Main reliable heuristic for a likely header if not in the known list: ends with a colon.
                if line_stripped_for_check.endswith(':') and len(line_stripped_for_check) <= 50 and num_words < 7 and num_words > 0:
                    is_likely_header = True
                
                # The ISUPPER and isolated_short_line heuristics were too prone to marking content as headers.
                # For now, we are making is_likely_header much more conservative.
                # Advanced sub-header detection could be added later if needed, but primary sections are key.

                # Example of a very specific ISUPPER rule if needed for certain subheaders (currently disabled):
                # if not is_likely_header and line_stripped_for_check.isupper() and \
                #    line_stripped_for_check in ["GENERAL", "TECHNICAL"]: # Only very specific, known subheader words
                #        is_likely_header = True

            if is_header or is_likely_header:
                # Add extra spacing around headers
                if structured_text and structured_text[-1]:
                    structured_text.append('')
                structured_text.append(f"SECTION_MARKER: {line}")
                structured_text.append('')
            else:
                structured_text.append(line)
        
        if self.debug:
            print("DEBUG (_process_layout): Structured text WITH SECTION_MARKERS before _process_two_column call:")
            for i, line_debug in enumerate(structured_text[:50]): # Print first 50 lines
                print(f"  Line {i}: {line_debug}")
            if len(structured_text) > 50: print("  ...")

        # Handle potential two-column layouts
        if self._is_likely_two_column(structured_text):
            if self.debug: print("DEBUG (_process_layout): _is_likely_two_column is TRUE. Calling _process_two_column.")
            structured_text = self._process_two_column(structured_text)
            
        # Join processed text and clean up section markers
        result = '\n'.join(structured_text)
        result = re.sub(r'SECTION_MARKER: ', '', result)
        
        return result
    
    def _is_likely_two_column(self, lines):
        """Detect if text likely has a two-column layout"""
        # Count short lines (potential column content)
        short_lines = sum(1 for line in lines if line and len(line) < 40)
        non_empty = sum(1 for line in lines if line)
        
        if non_empty == 0:
            return False
            
        # If more than 60% are short lines, likely two columns
        return (short_lines / non_empty) > 0.6
    
    def _process_two_column(self, lines):
        """Process two-column layout by attempting to reconstruct correct reading order"""
        # Identify section markers
        section_markers = []
        for i, line in enumerate(lines):
            if line.startswith("SECTION_MARKER:"):
                section_markers.append((i, line))
                
        # If we found sections, try to reorganize
        if len(section_markers) >= 2:
            # Extract sections between markers
            sections = []
            for i in range(len(section_markers)):
                start_idx = section_markers[i][0]
                end_idx = section_markers[i+1][0] if i < len(section_markers)-1 else len(lines)
                
                # Extract section content including the header
                section_content = lines[start_idx:end_idx]
                section_title = section_markers[i][1].replace("SECTION_MARKER: ", "")
                
                if self.debug:
                    print(f"DEBUG (_process_two_column): Identified raw section - Title: '{section_title}', StartIdx: {start_idx}, EndIdx: {end_idx}")
                    # print(f"  Content lines for '{section_title}': {section_content[:3]}") # Might be too verbose

                # Add to sections with its title for better sorting
                sections.append({
                    "title": section_title,
                    "content": section_content,
                    "position": start_idx
                })
            
            # Sort sections by their original position
            sections.sort(key=lambda x: x["position"])
            
            # Reconstruct text with left column first, then right column
            reconstructed_lines = []
            
            for section in sections:
                reconstructed_lines.extend(section["content"])
                reconstructed_lines.append('')  # Add a blank line between sections
            
            reconstructed_lines.append('')  # Separation between columns
            
            return reconstructed_lines
        
        # Default - return original lines if we couldn't identify sections
        return lines 

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhanced_extractor.py <path_to_pdf_file>")
        sys.exit(1)
    
    pdf_file_path = sys.argv[1]
    
    if not os.path.exists(pdf_file_path):
        print(f"Error: PDF file not found at {pdf_file_path}")
        sys.exit(1)
        
    print(f"Attempting to extract text from: {pdf_file_path}")
    
    # Instantiate the extractor with debug mode on
    extractor = EnhancedExtractor(debug=True)
    
    # Extract text
    extracted_text = extractor.extract_from_pdf(pdf_file_path)
    
    if extracted_text:
        print("\\n--- EXTRACTED TEXT ---")
        # Print first 1000 characters of extracted text for brevity
        print(extracted_text[:1000])
        print("\\n----------------------")
        
        # You can also save the full output to a file if you want to inspect it all
        # output_file_name = f"{Path(pdf_file_path).stem}_fully_extracted_by_script.txt"
        # with open(output_file_name, "w", encoding="utf-8") as f_out:
        #     f_out.write(extracted_text)
        # print(f"Full extracted text saved to: {output_file_name}")
    else:
        print("Failed to extract text or an error occurred.") 