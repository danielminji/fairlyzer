import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import re

# Optional: Specify Tesseract path if not in system PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Example for Windows

def get_image_from_url(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img_bytes = BytesIO(response.content)
        return img_bytes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL {image_url}: {e}")
        return None

def highlight_booths_on_map(image_bytes, recommended_booth_numbers):
    """
    Detects booth numbers on a map image using OCR and highlights the recommended ones.

    Args:
        image_bytes (BytesIO): The job fair map image in bytes.
        recommended_booth_numbers (list): A list of strings representing the booth numbers to highlight.

    Returns:
        PIL.Image: The image with recommended booths highlighted, or the original image if errors occur.
                   Returns None if the input image cannot be processed.
    """
    if not image_bytes or not recommended_booth_numbers:
        return None

    try:
        pil_image = Image.open(image_bytes).convert("RGB")
        opencv_image = np.array(pil_image)
        # Convert RGB to BGR for OpenCV
        opencv_image = opencv_image[:, :, ::-1].copy()
    except Exception as e:
        print(f"Error loading image for OCR: {e}")
        return None # Return None if image loading fails

    # Preprocessing (optional, but can improve OCR)
    gray_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # --- Experimental: Dilate the image slightly to thicken characters --- 
    kernel = np.ones((2,2),np.uint8) # REVERTED to (2,2) DILATION KERNEL
    dilated_image = cv2.dilate(thresh_image, kernel, iterations = 1)
    # --- End Experimental Dilation ---

    cv2.imwrite("debug_ocr_input_map_dilated.png", dilated_image) # DEBUG: Save the DILATED image
    print("DEBUG: Saved DILATED thresh_image as debug_ocr_input_map_dilated.png")
    # cv2.imwrite("debug_ocr_input_NO_DILATION.png", dilated_image) # DEBUG: Save the NON-DILATED image
    # print("DEBUG: Saved NON-DILATED thresh_image as debug_ocr_input_NO_DILATION.png")
    # Could add more: noise removal, scaling, etc.

    found_booth_boxes = []
    
    try:
        # Use pytesseract to get detailed data including bounding boxes
        tesseract_config = '--psm 6 --oem 3'
        ocr_data = pytesseract.image_to_data(dilated_image, output_type=pytesseract.Output.DICT, config=tesseract_config)
        
        n_boxes = len(ocr_data['level'])
        print(f"OCR: Found {n_boxes} potential text boxes. Iterating...") 

        raw_detections = []
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            # Log everything Tesseract sees above a very low confidence for debugging
            # print(f"OCR Raw Detect (conf > 0): '{text}' at ({ocr_data['left'][i]},{ocr_data['top'][i]},{ocr_data['width'][i]},{ocr_data['height'][i]}) conf: {conf}") #生产环境下注释掉
            
            # Store reasonably confident raw detections for matching logic
            if conf > 30 and text: # Minimum confidence for considering a piece for matching
                raw_detections.append({
                    "text": text,
                    "box": (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]),
                    "conf": conf
                })
        print("DEBUG: OCR Detected Texts:")
        for det in raw_detections:
            print(f"  Text: '{det['text']}' Conf: {det['conf']} Box: {det['box']}")
        print(f"DEBUG: Recommended booth numbers: {recommended_booth_numbers}")
        # Try matching both digit-only and 'Booth X' style
        for rec_num in recommended_booth_numbers:
            rec_num_str = str(rec_num)
            # Accept both digit-only and 'Booth X' style
            possible_patterns = [rec_num_str, f"Booth {rec_num_str}", f"Booth{rec_num_str}"]
            found_match = False
            for detection in raw_detections:
                for pat in possible_patterns:
                    if detection["text"].replace(" ", "").lower() == pat.replace(" ", "").lower() and detection["conf"] > 50:
                        x, y, w, h = detection["box"]
                        found_booth_boxes.append({
                            "text": detection["text"],
                            "box": (x, y, w, h)
                        })
                        print(f"MATCHED: '{detection['text']}' for recommended '{rec_num_str}' at {detection['box']}")
                        found_match = True
                        break
                if found_match:
                    break
        # Fallback: try partial match if nothing found
        if not found_booth_boxes:
            for rec_num in recommended_booth_numbers:
                for detection in raw_detections:
                    if rec_num in detection["text"] and detection["conf"] > 50:
                        x, y, w, h = detection["box"]
                        found_booth_boxes.append({
                            "text": detection["text"],
                            "box": (x, y, w, h)
                        })
                        print(f"PARTIAL MATCH: '{detection['text']}' for recommended '{rec_num}' at {detection['box']}")
    except pytesseract.TesseractNotFoundError:
        print("Tesseract is not installed or not in your PATH.")
        return pil_image # Return original image
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return pil_image # Return original image on other OCR errors

    if not found_booth_boxes:
        print("No recommended booth numbers found on the map via OCR.")
        return pil_image # Return original if nothing found or to highlight

    # Draw highlights on the original PIL image
    draw = ImageDraw.Draw(pil_image, "RGBA") # Use RGBA for semi-transparent highlights

    padding = 10 # INCREASED PADDING

    for item in found_booth_boxes:
        # item["box"] is (x, y, width, height)
        x_coord, y_coord, w_coord, h_coord = item["box"]

        # Convert to (x0, y0, x1, y1) for Pillow, where (x1,y1) is bottom-right
        box_x0 = x_coord
        box_y0 = y_coord
        box_x1 = x_coord + w_coord
        box_y1 = y_coord + h_coord

        # Add padding, ensuring coordinates stay within image bounds
        img_width, img_height = pil_image.size
        padded_x0_for_pillow = max(0, box_x0 - padding)
        padded_y0_for_pillow = max(0, box_y0 - padding)
        padded_x1_for_pillow = min(img_width, box_x1 + padding)
        padded_y1_for_pillow = min(img_height, box_y1 + padding)
        
        # Ensure x1 >= x0 and y1 >= y0 after padding to prevent Pillow error
        # This can happen if width/height is very small and padding is large
        if padded_x1_for_pillow < padded_x0_for_pillow:
            padded_x1_for_pillow = padded_x0_for_pillow 
        if padded_y1_for_pillow < padded_y0_for_pillow:
            padded_y1_for_pillow = padded_y0_for_pillow

        final_padded_box_for_pillow = (padded_x0_for_pillow, padded_y0_for_pillow, padded_x1_for_pillow, padded_y1_for_pillow)

        # Draw a semi-transparent rectangle
        draw.rectangle(final_padded_box_for_pillow, outline="red", fill=(255, 0, 0, 200), width=8)
        
        # Optionally, draw the detected text again (e.g., if preprocessing made it hard to see)
        draw.text((padded_x0_for_pillow, padded_y0_for_pillow - 20), item["text"], fill="red")

    return pil_image